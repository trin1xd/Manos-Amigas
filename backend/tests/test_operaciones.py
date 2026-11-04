"""Contrato HTTP y reglas de permisos, sin requerir SQL Server.

Para probar la persistencia real hay que ejecutar la migración 06 y las
pruebas manuales descritas en docs/operaciones-api.md.
"""
from datetime import datetime, timedelta
from pathlib import Path
import sys

import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from services import auth_service
from services import operations_service as ops
from services.auth_service import ServiceError

USERS = {
    1: {'id': 1, 'nombre': 'Rosa Ejemplo', 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
    2: {'id': 2, 'nombre': 'Juan Estudiante', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO',
        'estado_verificacion': 'PENDIENTE_VERIFICACION'},
    3: {'id': 3, 'nombre': 'Eva Familiar', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    4: {'id': 4, 'nombre': 'Sofía Estudiante', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO',
        'estado_verificacion': 'VERIFICADO'},
}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda uid: USERS[int(uid)].copy())
    application = create_app()
    application.config['TESTING'] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def headers(app, user_id):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={'rol': USERS[user_id]['rol']})
    return {'Authorization': f'Bearer {token}'}


def test_sin_token_no_hay_acceso(client):
    assert client.get('/api/catalogo/servicios').status_code == 401
    assert client.get('/api/solicitudes/mias').status_code == 401
    assert client.get('/api/familiares/adultos').status_code == 401


def test_roles_no_pueden_saltar_de_perfil(client, app):
    assert client.post('/api/solicitudes', headers=headers(app, 4), json={}).status_code == 403
    assert client.get('/api/solicitudes/disponibles', headers=headers(app, 1)).status_code == 403
    assert client.get('/api/familiares/adultos', headers=headers(app, 1)).status_code == 403
    assert client.post('/api/familiares/vincular', headers=headers(app, 3), json={}).status_code == 403
    assert client.post('/api/solicitudes/2/aceptar', headers=headers(app, 2)).status_code == 404


def test_estudiante_pendiente_sin_tareas_ni_postulaciones_nuevas(client, app):
    resp = client.get('/api/solicitudes/disponibles', headers=headers(app, 2))
    assert resp.status_code == 403
    assert resp.get_json()['success'] is False
    resp2 = client.post('/api/solicitudes/10/postular', headers=headers(app, 2))
    assert resp2.status_code == 403


def test_universitario_verificado_puede_abrir_listado_sin_datos_reales(client, app, monkeypatch):
    monkeypatch.setattr(ops, 'disponibles', lambda u: [{'id': 3, 'servicio': 'Compras'}])
    res = client.get('/api/solicitudes/disponibles', headers=headers(app, 4))
    assert res.status_code == 200
    assert res.get_json()['solicitudes'][0]['id'] == 3


def test_adulto_puede_crear_solicitud(client, app, monkeypatch):
    captured = {}
    def fake_create(user, payload):
        captured.update({'user': user, 'payload': payload})
        return {'id': 101, 'estado': 'PENDIENTE'}
    monkeypatch.setattr(ops, 'crear_solicitud', fake_create)
    res = client.post('/api/solicitudes', headers=headers(app, 1), json={
        'id_servicio': 1, 'fecha': '2026-12-11', 'hora': '15:00',
        'duracion_horas': 2, 'descripcion': 'Apoyo para realizar compras.'
    })
    assert res.status_code == 201
    assert captured['user']['id'] == 1
    assert res.get_json()['solicitud']['id'] == 101


def test_payload_json_obligatorio(client, app):
    res = client.post('/api/solicitudes', headers=headers(app, 1), data='mal',
                      content_type='application/json')
    assert res.status_code == 400
    res2 = client.post('/api/familiares/vincular', headers=headers(app, 1), json=[])
    assert res2.status_code == 400


@pytest.mark.parametrize('patch', [
    {'duracion_horas': 0},
    {'duracion_horas': True},
    {'duracion_horas': 4},
    {'id_servicio': '1'},
    {'descripcion': 'corta'},
    {'fecha': '2020-01-01'},
    {'hora': '25:61'},
])
def test_validacion_no_crea_solicitudes_incorrectas(patch):
    fecha = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    fields = {'id_servicio': 1, 'fecha': fecha, 'hora': '15:00',
              'duracion_horas': 2, 'descripcion': 'Necesito ayuda con las compras'}
    fields.update(patch)
    with pytest.raises(ServiceError) as e:
        ops.crear_solicitud(USERS[1], fields)
    assert e.value.status == 400


class FakeConn:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0
    def cursor(self):
        return object()
    def commit(self):
        self.commits += 1
    def rollback(self):
        self.rollbacks += 1
    def close(self):
        pass


def test_familiar_sin_vinculo_no_puede_crear_para_terceros(monkeypatch):
    c = FakeConn()
    monkeypatch.setattr(ops, 'get_connection', lambda: c)
    monkeypatch.setattr(ops.repo, 'vinculo', lambda *args, **kwargs: None)
    fecha = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    with pytest.raises(ServiceError) as e:
        ops.crear_solicitud(USERS[3], {
            'id_adulto_mayor': 1, 'id_servicio': 1, 'fecha': fecha, 'hora': '15:00',
            'duracion_horas': 2, 'descripcion': 'Ayuda con las compras del hogar'
        })
    assert e.value.status == 403
    assert c.commits == 0
    assert c.rollbacks == 1


def test_familiar_sin_vinculo_no_puede_aceptar_postulacion(monkeypatch):
    c = FakeConn()
    monkeypatch.setattr(ops, 'get_connection', lambda: c)
    monkeypatch.setattr(ops.repo, 'solicitud', lambda *args, **kwargs: {
        'id': 8, 'id_adulto_mayor': 99, 'estado': 'PENDIENTE'
    })
    monkeypatch.setattr(ops.repo, 'vinculo', lambda *args, **kwargs: None)
    with pytest.raises(ServiceError) as e:
        ops.aceptar(USERS[3], 8, 18)
    assert e.value.status == 403
    assert c.commits == 0


def test_adulto_no_puede_aceptar_solicitud_de_otro_adulto(monkeypatch):
    c = FakeConn()
    monkeypatch.setattr(ops, 'get_connection', lambda: c)
    monkeypatch.setattr(ops.repo, 'solicitud', lambda *args, **kwargs: {
        'id': 8, 'id_adulto_mayor': 99, 'estado': 'PENDIENTE'
    })
    with pytest.raises(ServiceError) as e:
        ops.aceptar(USERS[1], 8, 18)
    assert e.value.status == 403
    assert c.commits == 0


def test_postulacion_repetida_rechazada(monkeypatch):
    c = FakeConn()
    monkeypatch.setattr(ops, 'get_connection', lambda: c)
    monkeypatch.setattr(ops.repo, 'estudiante_verificado', lambda *args: {'id': 4})
    fecha = (datetime.now() + timedelta(days=3)).isoformat()
    monkeypatch.setattr(ops.repo, 'solicitud', lambda *args, **kwargs: {
        'id': 8, 'estado': 'PENDIENTE', 'fecha_solicitada': fecha
    })
    monkeypatch.setattr(ops.repo, 'postulacion_existente', lambda *args: {'id': 100})
    with pytest.raises(ServiceError) as e:
        ops.postular(USERS[4], 8)
    assert e.value.status == 409
    assert c.commits == 0


def test_lista_familiar_no_muestra_datos_ajenos(client, app, monkeypatch):
    monkeypatch.setattr(ops, 'mis_adultos', lambda u: [])
    res = client.get('/api/familiares/adultos', headers=headers(app, 3))
    assert res.status_code == 200
    assert res.get_json()['adultos'] == []
