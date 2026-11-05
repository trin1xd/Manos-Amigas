"""Comprobaciones de contrato HTTP sin conexión a SQL Server.

Las pruebas integrales con SQL Server deben realizarse por separado.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()


def test_health_no_es_prueba_de_bd(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


@pytest.mark.parametrize('ruta', [
    '/api/auth/me',
    '/api/solicitudes/mias',
    '/api/postulaciones/mias',
    '/api/familiares/adultos',
    '/api/admin/universitarios',
])
def test_rutas_privadas_sin_token_responden_401(client, ruta):
    respuesta = client.get(ruta)
    assert respuesta.status_code == 401
    assert respuesta.get_json()['success'] is False


def test_token_invalido_responde_401(client):
    respuesta = client.get('/api/auth/me', headers={'Authorization': 'Bearer no-es-un-jwt'})
    assert respuesta.status_code == 401
    assert respuesta.get_json()['success'] is False


def test_metodo_incorrecto_y_ruta_inexistente_devuelven_json(client):
    mal_metodo = client.get('/api/auth/login')
    assert mal_metodo.status_code == 405
    assert mal_metodo.get_json()['success'] is False
    inexistente = client.get('/api/no-existe-en-manos-amigas')
    assert inexistente.status_code == 404
    assert inexistente.get_json()['success'] is False
