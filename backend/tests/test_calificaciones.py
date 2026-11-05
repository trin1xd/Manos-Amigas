"""Pruebas de calificaciones y permisos sin depender de SQL Server real."""
import sys
from pathlib import Path
import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import calificaciones_service as svc
from services.auth_service import ServiceError

CUENTAS = {
    1: {'id': 1, 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
    2: {'id': 2, 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO', 'estado_verificacion': 'VERIFICADO'},
    3: {'id': 3, 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    4: {'id': 4, 'rol': 'ADMIN', 'estado': 'ACTIVO'},
    5: {'id': 5, 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda uid: CUENTAS[int(uid)].copy())
    app = create_app()
    app.config['TESTING'] = True
    return app


def token(app, uid):
    with app.app_context():
        token = create_access_token(identity=str(uid))
    return {'Authorization': 'Bearer ' + token}


def test_rutas_protegidas(app, monkeypatch):
    c = app.test_client()
    assert c.get('/api/calificaciones/mias').status_code == 401
    assert c.post('/api/calificaciones/solicitudes/9', json={'puntaje': 5}).status_code == 401
    assert c.get('/api/calificaciones/mias', headers=token(app, 4)).status_code == 403
    monkeypatch.setattr(svc, 'listar', lambda user: [{'id': 9}])
    r = c.get('/api/calificaciones/mias', headers=token(app, 2))
    assert r.status_code == 200 and r.get_json()['servicios'][0]['id'] == 9


class Conexion:
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


def escenario(monkeypatch, finalizada=True, vinculo=True, existente=False):
    conn = Conexion()
    acciones = []
    monkeypatch.setattr(svc, 'get_connection', lambda: conn)
    monkeypatch.setattr(svc.repo, 'solicitud_finalizada', lambda *_: (
        {'id_adulto': 1, 'id_universitario': 2} if finalizada else None))
    monkeypatch.setattr(svc.ops_repo, 'vinculo', lambda *_, **__: {'activo': True} if vinculo else None)
    monkeypatch.setattr(svc.ops_repo, 'adulto_activo', lambda *_: {'id': 1})
    monkeypatch.setattr(svc.repo, 'existe', lambda *_: existente)
    monkeypatch.setattr(svc.repo, 'registrar', lambda _, sid, actor, objetivo, tipo, puntaje, comentario:
                        acciones.append((sid, actor, objetivo, tipo, puntaje, comentario)) or 22)
    return conn, acciones


@pytest.mark.parametrize('datos', [None, [], {}, {'puntaje': True}, {'puntaje': 0},
    {'puntaje': 6}, {'puntaje': '5'}, {'puntaje': 4, 'comentario': 3},
    {'puntaje': 5, 'comentario': 'a' * 301}, {'puntaje': 5, 'otra': 'campo'}])
def test_validacion_no_abre_bd(monkeypatch, datos):
    monkeypatch.setattr(svc, 'get_connection', lambda: pytest.fail('No consultar SQL'))
    with pytest.raises(ServiceError) as err:
        svc.evaluar(CUENTAS[1], 9, datos)
    assert err.value.status == 400


def test_no_permite_evaluar_sin_confirmacion(monkeypatch):
    conn, acciones = escenario(monkeypatch, finalizada=False)
    with pytest.raises(ServiceError) as err:
        svc.evaluar(CUENTAS[1], 9, {'puntaje': 5})
    assert err.value.status == 409
    assert acciones == [] and conn.commits == 0


def test_adulto_y_universitario_califican_distinto_sentido(monkeypatch):
    conn, acciones = escenario(monkeypatch)
    assert svc.evaluar(CUENTAS[1], 9, {'puntaje': 4, 'comentario': 'Muy bien'})['puntaje'] == 4
    assert acciones == [(9, 1, 2, 'ADULTO_A_UNIVERSITARIO', 4, 'Muy bien')]
    assert conn.commits == 1

    conn, acciones = escenario(monkeypatch)
    svc.evaluar(CUENTAS[2], 9, {'puntaje': 5})
    assert acciones == [(9, 2, 1, 'UNIVERSITARIO_A_ADULTO', 5, None)]
    assert conn.commits == 1


def test_familiar_revocado_no_puede_evaluar(monkeypatch):
    conn, acciones = escenario(monkeypatch, vinculo=False)
    with pytest.raises(ServiceError) as err:
        svc.evaluar(CUENTAS[3], 9, {'puntaje': 5})
    assert err.value.status == 403
    assert conn.commits == 0 and not acciones


def test_adulto_ajeno_no_puede_evaluar(monkeypatch):
    conn, acciones = escenario(monkeypatch)
    with pytest.raises(ServiceError) as err:
        svc.evaluar(CUENTAS[5], 9, {'puntaje': 5})
    assert err.value.status == 403
    assert conn.commits == 0 and not acciones


def test_dos_calificaciones_mismo_sentido_rechazadas(monkeypatch):
    conn, acciones = escenario(monkeypatch, existente=True)
    with pytest.raises(ServiceError) as err:
        svc.evaluar(CUENTAS[1], 9, {'puntaje': 5})
    assert err.value.status == 409
    assert conn.commits == 0 and not acciones
