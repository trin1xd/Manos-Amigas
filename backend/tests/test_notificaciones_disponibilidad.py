"""Contratos y reglas del Megaparche 3 sin SQL Server real."""
import sys
from pathlib import Path
import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import notificaciones_service as notif
from services import disponibilidad_service as disp
from services.auth_service import ServiceError

USUARIOS = {
    1: {'id': 1, 'nombre': 'Adulto', 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
    2: {'id': 2, 'nombre': 'Estudiante', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO', 'estado_verificacion': 'VERIFICADO'},
    3: {'id': 3, 'nombre': 'Familiar', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    4: {'id': 4, 'nombre': 'Admin', 'rol': 'ADMIN', 'estado': 'ACTIVO'},
}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda uid: USUARIOS[int(uid)].copy())
    a = create_app()
    a.config['TESTING'] = True
    return a


def cabecera(app, uid):
    with app.app_context():
        jwt = create_access_token(identity=str(uid))
    return {'Authorization': f'Bearer {jwt}'}


def test_notificaciones_requieren_token_y_rol(app):
    c = app.test_client()
    assert c.get('/api/notificaciones/mias').status_code == 401
    assert c.get('/api/notificaciones/mias', headers=cabecera(app, 4)).status_code == 403
    assert c.post('/api/notificaciones/10/leer').status_code == 401
    assert c.post('/api/notificaciones/leer-todas', headers=cabecera(app, 4)).status_code == 403


def test_notificaciones_solo_usuario_del_token(app, monkeypatch):
    IDs = []
    def lista(user):
        IDs.append(user['id'])
        return {'notificaciones': [{'id': 1, 'leida_utc': None}], 'no_leidas': 1}
    monkeypatch.setattr(notif, 'mias', lista)
    r = app.test_client().get('/api/notificaciones/mias', headers=cabecera(app, 3))
    assert r.status_code == 200
    assert r.get_json()['no_leidas'] == 1
    assert IDs == [3]


def test_marcar_leido_solo_destinatario(app, monkeypatch):
    llamadas = []
    def leer(user, id_notificacion):
        llamadas.append((user['id'], id_notificacion))
        return {'id': id_notificacion, 'leida': True}
    monkeypatch.setattr(notif, 'leer', leer)
    r = app.test_client().post('/api/notificaciones/9/leer', headers=cabecera(app, 1))
    assert r.status_code == 200
    assert llamadas == [(1, 9)]


def test_disponibilidad_solo_estudiante(app, monkeypatch):
    c = app.test_client()
    assert c.get('/api/disponibilidad/mia').status_code == 401
    assert c.get('/api/disponibilidad/mia', headers=cabecera(app, 1)).status_code == 403
    assert c.put('/api/disponibilidad/mia', headers=cabecera(app, 3), json={'franjas': []}).status_code == 403
    monkeypatch.setattr(disp, 'mia', lambda u: [{'dia_semana': 0, 'hora_inicio': '09:00', 'hora_fin': '12:00'}])
    r = c.get('/api/disponibilidad/mia', headers=cabecera(app, 2))
    assert r.status_code == 200 and r.get_json()['franjas'][0]['dia_semana'] == 0


def test_disponibilidad_validada_antes_de_tocar_bd(monkeypatch):
    monkeypatch.setattr(disp, 'get_connection', lambda: pytest.fail('No debe tocar SQL Server'))
    bad = [None, [], {}, {'franjas': 'lunes'}, {'franjas': [{}]},
           {'franjas': [{'dia_semana': True, 'hora_inicio': '09:00', 'hora_fin': '10:00'}]},
           {'franjas': [{'dia_semana': 7, 'hora_inicio': '09:00', 'hora_fin': '10:00'}]},
           {'franjas': [{'dia_semana': 0, 'hora_inicio': '09:00', 'hora_fin': '09:15'}]},
           {'franjas': [{'dia_semana': 0, 'hora_inicio': '09:00', 'hora_fin': '08:00'}]},
           {'franjas': [{'dia_semana': 0, 'hora_inicio': '25:00', 'hora_fin': '26:00'}]},
           {'franjas': [{'dia_semana': 0, 'hora_inicio': '09:00', 'hora_fin': '11:00'},
                        {'dia_semana': 0, 'hora_inicio': '10:00', 'hora_fin': '12:00'}]},
           {'franjas': [] , 'id_universitario': 4}]
    for payload in bad:
        with pytest.raises(ServiceError) as error:
            disp.guardar(USUARIOS[2], payload)
        assert error.value.status == 400


def test_disponibilidad_adyacente_permitida():
    franjas = disp.validar({'franjas': [
        {'dia_semana': 0, 'hora_inicio': '11:00', 'hora_fin': '13:00'},
        {'dia_semana': 0, 'hora_inicio': '09:00', 'hora_fin': '11:00'},
    ]})
    assert [f['hora_inicio'] for f in franjas] == ['09:00', '11:00']
    assert disp.validar({'franjas': []}) == []


def test_notificacion_repositorio_filtra_destinatario():
    from repositories import notificaciones_repository as repo
    class Cursor:
        def execute(self, query, args):
            self.query = query
            self.args = args
            self.rowcount = 0
    cursor = Cursor()
    assert repo.marcar_leida(cursor, 8, 11) is False
    assert cursor.args == (11, 8)
    assert 'id_usuario = ?' in cursor.query


def test_notificaciones_y_disponibilidad_no_exponen_terceros(app, monkeypatch):
    monkeypatch.setattr(disp, 'guardar', lambda u, d: d['franjas'])
    r = app.test_client().put('/api/disponibilidad/mia',
        headers=cabecera(app, 2), json={'franjas': []})
    assert r.status_code == 200
    assert 'id_usuario' not in r.get_json()
