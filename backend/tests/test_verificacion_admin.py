"""Contrato y permisos de habilitación ADMIN; no usa SQL Server real."""
import os
from pathlib import Path
import sys

import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import verificacion_service as svc
from services.auth_service import ServiceError

CUENTAS = {
    1: {'id': 1, 'nombre': 'Prueba Estudiante', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO',
        'estado_verificacion': 'PENDIENTE_VERIFICACION'},
    2: {'id': 2, 'nombre': 'Prueba Administrador', 'rol': 'ADMIN', 'estado': 'ACTIVO'},
    3: {'id': 3, 'nombre': 'Prueba Familiar', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda id_: CUENTAS[int(id_)].copy())
    app_ = create_app()
    app_.config['TESTING'] = True
    return app_


def auth(app, ident):
    with app.app_context():
        token = create_access_token(identity=str(ident))
    return {'Authorization': 'Bearer ' + token}


def test_solo_admin_puede_ver_estudiantes(app, monkeypatch):
    monkeypatch.setattr(svc, 'listado', lambda: [{'id': 1, 'estado_verificacion': 'PENDIENTE_VERIFICACION'}])
    cli = app.test_client()
    assert cli.get('/api/admin/universitarios').status_code == 401
    assert cli.get('/api/admin/universitarios', headers=auth(app, 1)).status_code == 403
    assert cli.get('/api/admin/universitarios', headers=auth(app, 3)).status_code == 403
    r = cli.get('/api/admin/universitarios', headers=auth(app, 2))
    assert r.status_code == 200
    assert r.get_json()['universitarios'][0]['id'] == 1


def test_decision_requiere_flag_y_rol_admin(app, monkeypatch):
    monkeypatch.delenv('ADMIN_VERIFICACION_PRUEBAS', raising=False)
    cli = app.test_client()
    body = {'accion': 'RECHAZAR', 'observacion': 'Caso de prueba rechazado'}
    assert cli.post('/api/admin/universitarios/1/decision', json=body, headers=auth(app, 2)).status_code == 403
    monkeypatch.setenv('ADMIN_VERIFICACION_PRUEBAS', 'true')
    assert cli.post('/api/admin/universitarios/1/decision', json=body, headers=auth(app, 1)).status_code == 403


def test_decision_solo_admin_habilitado(app, monkeypatch):
    monkeypatch.setenv('ADMIN_VERIFICACION_PRUEBAS', 'true')
    capturado = {}
    def fake_decidir(user, target, datos):
        capturado.update({'user': user, 'target': target, 'datos': datos})
        return {'id': target, 'estado_verificacion': 'VERIFICADO'}
    monkeypatch.setattr(svc, 'decidir', fake_decidir)
    body = {'accion': 'APROBAR', 'observacion': 'Aprobado únicamente para pruebas',
            'confirmacion_pruebas': True}
    cli = app.test_client()
    respuesta = cli.post('/api/admin/universitarios/1/decision', json=body, headers=auth(app, 2))
    assert respuesta.status_code == 200
    assert capturado['user']['rol'] == 'ADMIN'
    assert capturado['target'] == 1


@pytest.mark.parametrize('datos', [
    None,
    [],
    {},
    {'accion': 'APROBAR', 'observacion': 'Corta', 'confirmacion_pruebas': True},
    {'accion': 'APROBAR', 'observacion': 'Observación suficientemente larga'},
    {'accion': 'SUSPENDER', 'observacion': 'Observación suficientemente larga'},
    {'accion': 'RECHAZAR', 'observacion': 'a' * 501},
])
def test_validacion_no_llega_a_base(datos):
    with pytest.raises(ServiceError) as error:
        svc.decidir(CUENTAS[2], 1, datos)
    assert error.value.status == 400


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


def test_pendiente_se_actualiza_y_audita(monkeypatch):
    c = FakeConn()
    capturado = {}
    monkeypatch.setattr(svc, 'get_connection', lambda: c)
    monkeypatch.setattr(svc.repo, 'bloquear_universitario', lambda cursor, id_: {'id': id_, 'estado': 'PENDIENTE_VERIFICACION'})
    def fake_aplicar(cursor, id_, admin_id, anterior, nuevo, razon):
        capturado.update(locals())
        return True
    monkeypatch.setattr(svc.repo, 'aplicar_decision', fake_aplicar)
    resultado = svc.decidir(CUENTAS[2], 1, {
        'accion': 'APROBAR', 'observacion': 'Solo entorno de desarrollo',
        'confirmacion_pruebas': True,
    })
    assert resultado['estado_verificacion'] == 'VERIFICADO'
    assert capturado['admin_id'] == 2
    assert c.commits == 1 and c.rollbacks == 0


def test_estado_ya_decidido_no_se_sobrescribe(monkeypatch):
    c = FakeConn()
    monkeypatch.setattr(svc, 'get_connection', lambda: c)
    monkeypatch.setattr(svc.repo, 'bloquear_universitario', lambda *args: {'id': 1, 'estado': 'RECHAZADO'})
    with pytest.raises(ServiceError) as error:
        svc.decidir(CUENTAS[2], 1, {'accion': 'RECHAZAR', 'observacion': 'Una explicación para la prueba'})
    assert error.value.status == 409
    assert c.commits == 0 and c.rollbacks == 1
