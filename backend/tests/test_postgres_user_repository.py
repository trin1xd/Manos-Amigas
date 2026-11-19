"""Pruebas sin red de la interfaz PostgreSQL de autenticación.

No contienen credenciales ni dependen de un proyecto Supabase.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repositories import postgres_user_repository as repo


class FakeCursor:
    def __init__(self, row=None, columns=None):
        self.row = row
        self.description = [(name,) for name in (columns or [])]
        self.query = None
        self.parameters = None

    def execute(self, query, parameters):
        self.query = query
        self.parameters = parameters

    def fetchone(self):
        return self.row


def test_role_query_uses_postgres_placeholders():
    cur = FakeCursor((3,))
    assert repo.get_role_id(cur, "FAMILIAR") == 3
    assert 'public."Roles"' in cur.query
    assert '%s' in cur.query
    assert cur.parameters == ("FAMILIAR",)


def test_user_insert_returns_generated_id():
    cur = FakeCursor((42,))
    result = repo.insert_user(
        cur, nombre_completo="Persona Ejemplo", rut="12345678-5",
        email="ejemplo@example.test", telefono="000000000",
        fecha_nacimiento=None, password_hash="hash-no-real", id_rol=3,
    )
    assert result == 42
    assert "RETURNING id_usuario" in cur.query
    assert "OUTPUT INSERTED" not in cur.query
    assert len(cur.parameters) == 7


def test_login_row_returns_dictionary():
    names = [
        "id_usuario", "nombre_completo", "email", "password_hash",
        "estado", "password_version", "rol", "estado_verificacion",
    ]
    cur = FakeCursor(
        (5, "Ejemplo", "a@example.test", "hash", "ACTIVO", 0, "FAMILIAR", None),
        names,
    )
    user = repo.find_user_by_email(cur, "a@example.test")
    assert user["id_usuario"] == 5
    assert user["rol"] == "FAMILIAR"
    assert cur.parameters == ("a@example.test",)
    assert 'public."Usuarios"' in cur.query


def test_missing_account_returns_none():
    cur = FakeCursor()
    assert repo.find_user_by_id(cur, 999) is None
