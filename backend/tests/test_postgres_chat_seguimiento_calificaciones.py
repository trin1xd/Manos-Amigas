"""Pruebas sin Supabase de chat, seguimiento y calificaciones PostgreSQL."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repositories import postgres_chat_repository as chat
from repositories import postgres_seguimiento_repository as seguimiento
from repositories import postgres_calificaciones_repository as calif


class Cursor:
    def __init__(self, rows=(), count=1):
        self.rows = list(rows)
        self.rowcount = count
        self.calls = []
        self.description = [("id",)]

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        return self.rows


def test_chat_mensajes_restringidos():
    cur = Cursor()
    assert chat.listar_mensajes(cur, 6) == []
    assert "LIMIT 80" in cur.calls[0][0]
    assert cur.calls[0][1] == (6,)


def test_chat_inserta_mensaje_con_returning():
    cur = Cursor([(17,)])
    assert chat.guardar(cur, 6, 3, "Mensaje de prueba") == 17
    assert "RETURNING id_mensaje" in cur.calls[0][0]


def test_chat_contexto_usa_bloqueo():
    cur = Cursor()
    assert chat.contexto(cur, 7, bloquear=True) is None
    assert "FOR UPDATE OF s" in cur.calls[0][0]


def test_seguimiento_bloquea_solicitud():
    cur = Cursor()
    assert seguimiento.bloquear_solicitud(cur, 4) is None
    assert "FOR UPDATE OF s" in cur.calls[0][0]


def test_calificacion_usa_returning():
    cur = Cursor([(8,)])
    assert calif.registrar(cur, 1, 2, 3, "ADULTO_A_UNIVERSITARIO", 5, None) == 8
    assert "RETURNING id_calificacion" in cur.calls[0][0]


def test_seguimiento_llegada_genera_historial():
    cur = Cursor()
    seguimiento.registrar_accion(cur, 1, 2, "LLEGADA")
    assert len(cur.calls) == 2
    assert 'public."SeguimientoServicios"' in cur.calls[0][0]
    assert 'public."HistorialSeguimiento"' in cur.calls[1][0]
