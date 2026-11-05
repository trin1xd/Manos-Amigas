"""Permisos de listado de familiares autorizados, sin SQL Server real."""
import sys
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import operations_service as ops

CUENTAS = {
    1: {'id': 1, 'nombre': 'Adulto de prueba', 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
    2: {'id': 2, 'nombre': 'Familiar de prueba', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    3: {'id': 3, 'nombre': 'Universitario de prueba', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO'},
}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda uid: CUENTAS[int(uid)].copy())
    application = create_app()
    application.config['TESTING'] = True
    return application


def token(app, id_usuario):
    with app.app_context():
        jwt = create_access_token(identity=str(id_usuario))
    return {'Authorization': 'Bearer ' + jwt}


def test_listar_familiares_solo_adulto_autenticado(app, monkeypatch):
    llamadas = []
    def lista(user):
        llamadas.append(user['id'])
        return [{'id': 2, 'nombre': 'Familiar de prueba', 'parentesco': 'Hija',
                 'email': 'familiar@example.com'}]
    monkeypatch.setattr(ops, 'mis_familiares', lista)
    cliente = app.test_client()
    assert cliente.get('/api/familiares/mios').status_code == 401
    assert cliente.get('/api/familiares/mios', headers=token(app, 2)).status_code == 403
    assert cliente.get('/api/familiares/mios', headers=token(app, 3)).status_code == 403
    resultado = cliente.get('/api/familiares/mios', headers=token(app, 1))
    assert resultado.status_code == 200
    assert resultado.get_json()['familiares'][0]['nombre'] == 'Familiar de prueba'
    assert llamadas == [1]


def test_listado_de_familiares_vacio(app, monkeypatch):
    monkeypatch.setattr(ops, 'mis_familiares', lambda user: [])
    respuesta = app.test_client().get('/api/familiares/mios', headers=token(app, 1))
    assert respuesta.status_code == 200
    assert respuesta.get_json()['familiares'] == []
