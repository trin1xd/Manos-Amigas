"""Pruebas aisladas de agenda y avisos PostgreSQL, sin credenciales."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from repositories import postgres_agenda_repository as agenda
from repositories import postgres_notificaciones_repository as notif


class Cursor:
    def __init__(self, rows=None, columns=None, rowcount=1):
        self.rows = list(rows or [])
        self.description = [(c,) for c in (columns or ["id"])]
        self.rowcount = rowcount
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        result = self.rows
        self.rows = []
        return result


def test_agenda_usa_filtro_familiar_autorizado():
    cur = Cursor()
    assert agenda.listar(cur, "FAMILIAR", 8) == []
    sql, params = cur.calls[0]
    assert 'public."FamiliarAdultoMayor"' in sql
    assert "f.activo = TRUE" in sql
    assert "LIMIT 100" in sql
    assert params == (8,)


def test_agenda_rechaza_rol_invalido():
    with pytest.raises(ValueError):
        agenda.listar(Cursor(), "ADMIN", 1)


def test_conflicto_bloquea_estudiante():
    cur = Cursor(rows=[(11,), (22,)])
    assert agenda.conflicto_de_aceptacion(cur, 1, 2) == {"id": 22}
    assert "FOR UPDATE OF u" in cur.calls[0][0]
    assert "INTERVAL '1 hour'" in cur.calls[1][0]


def test_conflicto_no_encontrado_falla_cerrado():
    cur = Cursor()
    assert agenda.conflicto_de_aceptacion(cur, 1, 2) == {"no_disponible": True}
    assert len(cur.calls) == 1


def test_avisos_solo_para_usuario_propio():
    cur = Cursor()
    notif.listar(cur, 4)
    sql, params = cur.calls[0]
    assert "n.id_usuario = %s" in sql
    assert "LIMIT 100" in sql
    assert params == (4,)


def test_marcar_aviso_leido_restringe_propietario():
    cur = Cursor()
    assert notif.marcar_leida(cur, 7, 10)
    sql, params = cur.calls[0]
    assert "id_usuario = %s" in sql
    assert "leida_utc IS NULL" in sql
    assert params == (10, 7)
