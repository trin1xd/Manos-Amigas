"""Reglas de agenda y bloqueo de doble asignación (sin SQL Server real)."""
from datetime import datetime, timedelta
from pathlib import Path
import sys

import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import agenda_service
from services import operations_service as ops
from repositories import agenda_repository
from services.auth_service import ServiceError

USERS = {
    1: {'id': 1, 'nombre': 'Rosa', 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
    2: {'id': 2, 'nombre': 'Juan', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO',
        'estado_verificacion': 'VERIFICADO'},
    3: {'id': 3, 'nombre': 'Eva', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    4: {'id': 4, 'nombre': 'Admin', 'rol': 'ADMIN', 'estado': 'ACTIVO'},
}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda uid: USERS[int(uid)].copy())
    a = create_app()
    a.config['TESTING'] = True
    return a


def bearer(app, usuario):
    with app.app_context():
        jwt = create_access_token(identity=str(usuario))
    return {'Authorization': f'Bearer {jwt}'}


def test_agenda_exige_jwt_y_rol(app):
    c = app.test_client()
    assert c.get('/api/agenda/mia').status_code == 401
    assert c.get('/api/agenda/mia', headers=bearer(app, 4)).status_code == 403


@pytest.mark.parametrize('usuario', [1, 2, 3])
def test_agenda_identidad_sale_del_token(app, monkeypatch, usuario):
    llamadas = []
    monkeypatch.setattr(agenda_service, 'mia', lambda user: llamadas.append(user['id']) or [])
    c = app.test_client()
    assert c.get('/api/agenda/mia', headers=bearer(app, usuario)).status_code == 200
    assert llamadas == [usuario]


def test_agenda_servicio_rechaza_admin_sin_tocar_bd(monkeypatch):
    monkeypatch.setattr(agenda_service, 'get_connection', lambda: pytest.fail('No abrir BD'))
    with pytest.raises(ServiceError) as e:
        agenda_service.mia(USERS[4])
    assert e.value.status == 403


class CursorLista:
    def __init__(self):
        self.query = ''
        self.args = None
        self.description = [('id',), ('servicio',), ('fecha_solicitada',), ('duracion_horas',), ('estado',)]
    def execute(self, query, args):
        self.query, self.args = query, args
        return self
    def fetchall(self):
        return [(7, 'Compras', datetime(2026, 12, 11, 15, 0), 2, 'ASIGNADA')]


@pytest.mark.parametrize('rol,filtro', [
    ('UNIVERSITARIO', 'p.id_universitario = ?'),
    ('ADULTO_MAYOR', 's.id_adulto_mayor = ?'),
    ('FAMILIAR', 'f.id_familiar = ? AND f.activo = 1'),
])
def test_agenda_repo_filtra_en_sql_por_rol(rol, filtro):
    cur = CursorLista()
    listado = agenda_repository.listar(cur, rol, 99)
    assert cur.args == (99,)
    assert filtro in cur.query
    assert "p.estado = 'ACEPTADA'" in cur.query
    assert 's.fecha_solicitada' in cur.query
    assert listado[0]['fecha_solicitada'] == '2026-12-11T15:00'
    assert 'nombre_completo' not in cur.query


def test_agenda_no_acepta_rol_arbitrario():
    with pytest.raises(ValueError):
        agenda_repository.listar(CursorLista(), 'ADMIN', 1)


class CursorConflicto:
    def __init__(self, conflicto):
        self.queries = []
        self.conflicto = conflicto
    def execute(self, sql, args):
        self.queries.append((sql, args))
        return self
    def fetchone(self):
        return (2,) if len(self.queries) == 1 else ((88,) if self.conflicto else None)


@pytest.mark.parametrize('hay_conflicto', [True, False])
def test_consulta_bloquea_estudiante_y_solo_aceptadas(hay_conflicto):
    cur = CursorConflicto(hay_conflicto)
    resultado = agenda_repository.conflicto_de_aceptacion(cur, 10, 21)
    assert resultado == ({'id': 88} if hay_conflicto else None)
    assert 'UPDLOCK, HOLDLOCK' in cur.queries[0][0]
    assert cur.queries[0][1] == (10, 21)
    assert "p.estado = 'ACEPTADA'" in cur.queries[1][0]
    assert "otra.estado IN ('ASIGNADA', 'EN_CURSO')" in cur.queries[1][0]
    assert 'DATEADD(HOUR' in cur.queries[1][0]
    assert cur.queries[1][1] == (10, 2)


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


def configurar_aceptacion(monkeypatch, conflicto):
    con = FakeConn()
    fecha = (datetime.now() + timedelta(days=7)).isoformat(timespec='minutes')
    monkeypatch.setattr(ops, 'get_connection', lambda: con)
    monkeypatch.setattr(ops.repo, 'solicitud', lambda *_args, **_kwargs: {
        'id': 7, 'id_adulto_mayor': 1, 'estado': 'PENDIENTE', 'fecha_solicitada': fecha})
    monkeypatch.setattr(ops.repo, 'postulacion_aceptable', lambda *_args: {'id': 10, 'estado': 'PENDIENTE'})
    monkeypatch.setattr(ops.agenda_repo, 'conflicto_de_aceptacion', lambda *_args: conflicto)
    llamadas = []
    monkeypatch.setattr(ops.repo, 'aceptar_postulacion', lambda *_args: llamadas.append('aceptar') or True)
    monkeypatch.setattr(ops.notif_repo, 'avisar_adulto_y_familia', lambda *_args: llamadas.append('aviso_adulto'))
    monkeypatch.setattr(ops.notif_repo, 'avisar_postulante', lambda *_args: llamadas.append('aviso_elegido'))
    monkeypatch.setattr(ops.notif_repo, 'avisar_postulantes_no_seleccionados', lambda *_args: llamadas.append('aviso_no_elegido'))
    return con, llamadas


def test_conflicto_no_acepta_no_notifica_y_revierte(monkeypatch):
    con, llamadas = configurar_aceptacion(monkeypatch, {'id': 88})
    with pytest.raises(ServiceError) as err:
        ops.aceptar(USERS[1], 7, 10)
    assert err.value.status == 409
    assert llamadas == []
    assert con.commits == 0 and con.rollbacks == 1


def test_sin_conflicto_acepta_y_notifica(monkeypatch):
    con, llamadas = configurar_aceptacion(monkeypatch, None)
    respuesta = ops.aceptar(USERS[1], 7, 10)
    assert respuesta['estado'] == 'ASIGNADA'
    assert llamadas == ['aceptar', 'aviso_adulto', 'aviso_elegido', 'aviso_no_elegido']
    assert con.commits == 1 and con.rollbacks == 0
