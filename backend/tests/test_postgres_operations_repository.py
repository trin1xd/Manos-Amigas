"""Pruebas aisladas de consultas PostgreSQL, sin acceso a Supabase."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from repositories import postgres_operations_repository as repo


class CursorFalso:
    def __init__(self, rows=None, names=None, rowcount=1):
        self.rows = rows or []
        self.description = [(name,) for name in (names or ["id"])]
        self.rowcount = rowcount
        self.calls = []

    def execute(self, query, params=None):
        self.calls.append((query, params))

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        return self.rows


def test_crear_solicitud_devuelve_id():
    cur = CursorFalso(rows=[(20,)])
    result = repo.crear_solicitud(cur, 1, 2, 3, "2027-01-01 12:00", 2, "Prueba")
    assert result == {"id": 20}
    sql, params = cur.calls[0]
    assert "RETURNING id_solicitud AS id" in sql
    assert "public.\"Solicitudes\"" in sql
    assert len(params) == 6


def test_crear_postulacion_devuelve_id():
    cur = CursorFalso(rows=[(10,)])
    assert repo.crear_postulacion(cur, 3, 5) == {"id": 10}
    assert "RETURNING id_postulacion" in cur.calls[0][0]


def test_lista_tareas_no_muestra_contactos_y_tiene_limite():
    cur = CursorFalso(names=["id", "servicio", "fecha_solicitada", "duracion_horas", "estado"])
    repo.solicitudes_disponibles(cur)
    sql, params = cur.calls[0]
    assert "LIMIT 100" in sql
    assert "CURRENT_TIMESTAMP" in sql
    assert "direccion" not in sql.lower()
    assert "telefono" not in sql.lower()
    assert params is None


def test_lectura_con_bloqueo_postgres():
    cur = CursorFalso(rows=[(1, True)], names=["id", "activo"])
    repo.vinculo(cur, 4, 7, lock=True)
    assert "FOR UPDATE" in cur.calls[0][0]
    assert cur.calls[0][1] == (4, 7)


def test_aceptacion_modifica_una_postulacion():
    cur = CursorFalso()
    assert repo.aceptar_postulacion(cur, 3, 9) is True
    assert len(cur.calls) == 3
    assert 'public."Solicitudes"' in cur.calls[2][0]


def test_aceptacion_sin_fila_no_prosigue():
    cur = CursorFalso(rowcount=0)
    assert repo.aceptar_postulacion(cur, 3, 9) is False
    assert len(cur.calls) == 1


def test_servicio_activo_usa_boolean_postgres():
    cur = CursorFalso(rows=[(5,)])
    assert repo.servicio_activo(cur, 5) == {"id": 5}
    assert "activo = TRUE" in cur.calls[0][0]
