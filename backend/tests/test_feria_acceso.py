"""Entrada sin formularios para visitantes, probada solo con DB ficticia."""
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from services import auth_service
from tests.test_auth_jwt import JwtFakeRepo
from tests.test_auth import FakeConnection, FakeDb
from utils.rut import is_valid_rut


class FeriaRepo(JwtFakeRepo):
    def habilitar_universitario_para_feria(self, db, id_usuario):
        perfil = next((p for p in db.profiles if p['id_usuario'] == id_usuario), None)
        if not perfil or perfil['estado_verificacion'] != 'PENDIENTE_VERIFICACION':
            raise RuntimeError('Perfil de prueba inválido.')
        perfil['estado_verificacion'] = 'VERIFICADO'


@pytest.fixture
def contexto(monkeypatch):
    fake = FakeDb()
    monkeypatch.setattr(auth_service, 'get_connection', lambda: FakeConnection(fake))
    monkeypatch.setattr(auth_service, 'repo', FeriaRepo())
    monkeypatch.setenv('DB_ENGINE', 'postgres')
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client(), fake


def test_entrada_sin_flag_no_esta_disponible(contexto, monkeypatch):
    client, db = contexto
    monkeypatch.delenv('FERIA_REGISTRO_LIBRE', raising=False)
    response = client.post('/api/auth/demo', json={'rol': 'UNIVERSITARIO'})
    assert response.status_code == 404
    assert len(db.users) == 0


@pytest.mark.parametrize('rol', ['ADULTO_MAYOR', 'UNIVERSITARIO'])
def test_visitante_ingresa_directamente_y_consulta_su_perfil(contexto, monkeypatch, rol):
    client, db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    response = client.post('/api/auth/demo', json={'rol': rol})
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert body['user']['rol'] == rol
    assert body['access_token']
    assert not any(k in body for k in ('password', 'password_hash'))
    assert is_valid_rut(db.users[0]['rut'])
    assert db.users[0]['email'].endswith('@demo.invalid')
    me = client.get('/api/auth/me', headers={
        'Authorization': 'Bearer ' + body['access_token']
    })
    assert me.status_code == 200, me.get_json()
    assert me.get_json()['user']['rol'] == rol
    if rol == 'UNIVERSITARIO':
        assert body['user']['estado_verificacion'] == 'VERIFICADO'
        assert db.profiles[0]['estado_verificacion'] == 'VERIFICADO'


def test_registro_publico_universitario_sin_correo_uss_es_habilitado(contexto, monkeypatch):
    client, db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    datos = {
        'nombre_completo': 'Universitaria ficticia',
        'rut': '12345678-5',
        'fecha_nacimiento': '2002-03-10',
        'telefono': '+56911112222',
        'email': 'universitaria@example.com',
        'password': 'clave-demostracion-123',
        'universidad': 'Universidad de prueba',
        'carrera': 'Enfermería',
        'anio_cursa': 2,
        'contacto_emergencia_nombre': 'Contacto de ejemplo',
        'contacto_emergencia_telefono': '+56911112222',
    }
    response = client.post('/api/auth/register/universitario', json=datos)
    assert response.status_code == 201, response.get_json()
    assert response.get_json()['user']['estado_verificacion'] == 'VERIFICADO'
    assert db.profiles[0]['correo_institucional'].endswith('@demo.invalid')
    assert db.profiles[0]['estado_verificacion'] == 'VERIFICADO'


def test_entrada_invalida_no_crea_usuarios(contexto, monkeypatch):
    client, db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    for data in ({'rol': 'ADMIN'}, {'rol': 'FAMILIAR'}, {}, {'rol': 'UNIVERSITARIO', 'id': 1}):
        response = client.post('/api/auth/demo', json=data)
        assert response.status_code == 400
    assert len(db.users) == 0
