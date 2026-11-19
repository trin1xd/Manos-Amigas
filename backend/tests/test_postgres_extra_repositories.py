"""Pruebas sin red de los repositorios PostgreSQL adicionales."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repositories import postgres_disponibilidad_repository as disp
from repositories import postgres_verificacion_repository as verif
from repositories import postgres_verificacion_institucional_repository as inst
from repositories import postgres_recuperacion_repository as reset


class Cursor:
    def __init__(self, rows=(), rowcount=1):
        self.rows = list(rows)
        self.rowcount = rowcount
        self.description = [("dia_semana",), ("hora_inicio",), ("hora_fin",)]
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        return self.rows


def test_disponibilidad_formatea_hora():
    cur = Cursor()
    assert disp.listar(cur, 4) == []
    assert "TO_CHAR(hora_inicio" in cur.calls[0][0]
    assert cur.calls[0][1] == (4,)


def test_verificacion_administrativa_bloquea_perfil():
    cur = Cursor([( "PENDIENTE_VERIFICACION", 8 )])
    assert verif.bloquear_universitario(cur, 8)["id"] == 8
    assert "FOR UPDATE OF p" in cur.calls[0][0]


def test_verificacion_institucional_bloquea_codigo():
    cur = Cursor()
    assert inst.codigo(cur, 8, lock=True) is None
    assert "FOR UPDATE" in cur.calls[0][0]


def test_recuperacion_no_guarda_token_en_claro():
    cur = Cursor()
    reset.crear(cur, 8, "digest-hash-no-real")
    assert len(cur.calls) == 2
    assert "token_hash" in cur.calls[1][0]
    assert cur.calls[1][1] == (8, "digest-hash-no-real")


def test_recuperacion_bloquea_token_valido():
    cur = Cursor([(5,)])
    assert reset.validar_y_bloquear(cur, "hash") == 5
    sql, params = cur.calls[0]
    assert "LIMIT 1" in sql and "FOR UPDATE OF r" in sql
    assert params == ("hash",)
