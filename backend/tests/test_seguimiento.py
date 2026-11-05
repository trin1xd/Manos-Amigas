"""Pruebas de permisos y transiciones del seguimiento, sin SQL Server real."""
import sys
from pathlib import Path
import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import seguimiento_service as svc
from services.auth_service import ServiceError

USUARIOS = {
    1: {'id': 1, 'nombre': 'Adulto de prueba', 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
    2: {'id': 2, 'nombre': 'Estudiante de prueba', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO',
        'estado_verificacion': 'VERIFICADO'},
    3: {'id': 3, 'nombre': 'Familiar de prueba', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    4: {'id': 4, 'nombre': 'Admin de prueba', 'rol': 'ADMIN', 'estado': 'ACTIVO'},
    5: {'id': 5, 'nombre': 'Otro adulto', 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda uid: USUARIOS[int(uid)].copy())
    instance = create_app()
    instance.config['TESTING'] = True
    return instance


def token(app, user_id):
    with app.app_context():
        jwt = create_access_token(identity=str(user_id))
    return {'Authorization': 'Bearer ' + jwt}


def test_rutas_protegidas(app, monkeypatch):
    client = app.test_client()
    assert client.get('/api/seguimiento/mios').status_code == 401
    assert client.get('/api/seguimiento/mios', headers=token(app, 4)).status_code == 403
    assert client.post('/api/seguimiento/solicitudes/1/accion',
                       headers=token(app, 4), json={'accion': 'LLEGADA'}).status_code == 403
    monkeypatch.setattr(svc, 'listar', lambda user: [{'id': 5}])
    assert client.get('/api/seguimiento/mios', headers=token(app, 2)).get_json()['servicios'][0]['id'] == 5


def test_pedido_invalido_no_toca_bd(monkeypatch):
    monkeypatch.setattr(svc, 'get_connection', lambda: pytest.fail('No debe acceder a SQL Server'))
    for payload in [None, [], {}, {'accion': 'OTRO'},
                    {'accion': 'LLEGADA', 'fecha': '2030-01-01'}]:
        with pytest.raises(ServiceError) as error:
            svc.realizar(USUARIOS[2], 7, payload)
        assert error.value.status == 400


class FakeConnection:
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


def escenario(monkeypatch, estado='ASIGNADA', estudiante=2, seguimiento=None, vinculo=True):
    conn = FakeConnection()
    eventos = []
    monkeypatch.setattr(svc, 'get_connection', lambda: conn)
    monkeypatch.setattr(svc.repo, 'bloquear_solicitud', lambda *_: {
        'id': 7, 'id_adulto_mayor': 1, 'estado': estado, 'id_estudiante': estudiante})
    monkeypatch.setattr(svc.repo, 'estado_seguimiento', lambda *_: seguimiento)
    monkeypatch.setattr(svc.repo, 'registrar_accion', lambda _, id_, autor, accion: eventos.append((id_, autor, accion)))
    monkeypatch.setattr(svc.ops_repo, 'estudiante_verificado', lambda *_: {'id': estudiante})
    monkeypatch.setattr(svc.ops_repo, 'vinculo', lambda *_args, **_kwargs: {'activo': True} if vinculo else None)
    monkeypatch.setattr(svc.ops_repo, 'adulto_activo', lambda *_: {'id': 1})
    return conn, eventos


def test_estudiante_aceptado_registra_llegada_y_confirmador_es_adulto(monkeypatch):
    conn, eventos = escenario(monkeypatch)
    r = svc.realizar(USUARIOS[2], 7, {'accion': 'LLEGADA'})
    assert r['estado'] == 'ASIGNADA'
    assert eventos == [(7, 2, 'LLEGADA')]
    assert conn.commits == 1

    conn, eventos = escenario(monkeypatch, estado='EN_CURSO', seguimiento={
        'llegada': 1, 'inicio': 1, 'termino': 1, 'confirmacion': None})
    result = svc.realizar(USUARIOS[1], 7, {'accion': 'CONFIRMAR'})
    assert result['estado'] == 'FINALIZADA'
    assert eventos == [(7, 1, 'CONFIRMAR')]
    assert conn.commits == 1


def test_no_se_pueden_saltar_pasos(monkeypatch):
    conn, _ = escenario(monkeypatch)
    with pytest.raises(ServiceError) as error:
        svc.realizar(USUARIOS[2], 7, {'accion': 'INICIO'})
    assert error.value.status == 409
    assert conn.commits == 0 and conn.rollbacks == 1


def test_estudiante_ajeno_no_puede_registrar_llegada(monkeypatch):
    conn, _ = escenario(monkeypatch, estudiante=99)
    with pytest.raises(ServiceError) as error:
        svc.realizar(USUARIOS[2], 7, {'accion': 'LLEGADA'})
    assert error.value.status == 403
    assert conn.commits == 0


def test_familiar_revocado_no_confirma(monkeypatch):
    conn, _ = escenario(monkeypatch, estado='EN_CURSO', vinculo=False, seguimiento={
        'llegada': 1, 'inicio': 1, 'termino': 1, 'confirmacion': None})
    with pytest.raises(ServiceError) as error:
        svc.realizar(USUARIOS[3], 7, {'accion': 'CONFIRMAR'})
    assert error.value.status == 403
    assert conn.commits == 0


def test_adulto_ajeno_no_confirma(monkeypatch):
    conn, _ = escenario(monkeypatch, estado='EN_CURSO', seguimiento={
        'llegada': 1, 'inicio': 1, 'termino': 1, 'confirmacion': None})
    with pytest.raises(ServiceError) as error:
        svc.realizar(USUARIOS[5], 7, {'accion': 'CONFIRMAR'})
    assert error.value.status == 403
    assert conn.commits == 0


def test_inicio_y_termino_en_orden(monkeypatch):
    conn, eventos = escenario(monkeypatch, estado='ASIGNADA', seguimiento={
        'llegada': 1, 'inicio': None, 'termino': None, 'confirmacion': None})
    result = svc.realizar(USUARIOS[2], 7, {'accion': 'INICIO'})
    assert result['estado'] == 'EN_CURSO'
    assert eventos == [(7, 2, 'INICIO')]
    assert conn.commits == 1

    conn, eventos = escenario(monkeypatch, estado='EN_CURSO', seguimiento={
        'llegada': 1, 'inicio': 1, 'termino': None, 'confirmacion': None})
    result = svc.realizar(USUARIOS[2], 7, {'accion': 'TERMINO'})
    assert result['estado'] == 'EN_CURSO'
    assert eventos == [(7, 2, 'TERMINO')]
    assert conn.commits == 1


def test_familiar_autorizado_confirma(monkeypatch):
    conn, eventos = escenario(monkeypatch, estado='EN_CURSO', seguimiento={
        'llegada': 1, 'inicio': 1, 'termino': 1, 'confirmacion': None})
    result = svc.realizar(USUARIOS[3], 7, {'accion': 'CONFIRMAR'})
    assert result['estado'] == 'FINALIZADA'
    assert eventos == [(7, 3, 'CONFIRMAR')]
    assert conn.commits == 1


def test_no_confirmar_antes_de_termino(monkeypatch):
    conn, _ = escenario(monkeypatch, estado='EN_CURSO', seguimiento={
        'llegada': 1, 'inicio': 1, 'termino': None, 'confirmacion': None})
    with pytest.raises(ServiceError) as error:
        svc.realizar(USUARIOS[1], 7, {'accion': 'CONFIRMAR'})
    assert error.value.status == 409
    assert conn.rollbacks == 1
