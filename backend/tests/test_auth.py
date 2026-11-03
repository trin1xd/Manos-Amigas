"""Pruebas de autenticación.

Estas pruebas NO necesitan SQL Server: reemplazan la conexión y el repositorio
por una base en memoria (FakeDb) que imita commit/rollback. Sirven para validar
rutas, validaciones, hashing y reglas de negocio.

La prueba contra SQL Server real se hace manualmente (ver docs/api.md).
"""
import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from services import auth_service
from utils.rut import calculate_dv, is_valid_rut, normalize_rut


class FakeDb:
    """Base en memoria con transacciones simples (snapshot + rollback)."""

    def __init__(self):
        self.users = []
        self.profiles = []
        self.fail_profile = False

    def snapshot(self):
        return copy.deepcopy((self.users, self.profiles))


class FakeConnection:
    def __init__(self, db):
        self.db = db
        self._saved = db.snapshot()
        self.committed = False
        self.rolled_back = False

    def cursor(self):
        return self.db

    def commit(self):
        self.committed = True
        self._saved = self.db.snapshot()

    def rollback(self):
        self.rolled_back = True
        self.db.users, self.db.profiles = copy.deepcopy(self._saved)

    def close(self):
        pass


class FakeRepo:
    """Misma interfaz que repositories.user_repository, pero sobre FakeDb."""

    ROLES = {"ADULTO_MAYOR": 1, "UNIVERSITARIO": 2, "FAMILIAR": 3}

    def get_role_id(self, db, name):
        return self.ROLES.get(name)

    def rut_exists(self, db, rut):
        return any(u["rut"] == rut for u in db.users)

    def email_exists(self, db, email):
        return any(u["email"] == email for u in db.users)

    def institutional_email_exists(self, db, email):
        return any(p.get("correo_institucional") == email for p in db.profiles)

    def insert_user(self, db, **kwargs):
        user = dict(kwargs, id_usuario=len(db.users) + 1)
        db.users.append(user)
        return user["id_usuario"]

    def _profile(self, db, id_usuario, kind, **fields):
        if db.fail_profile:
            raise RuntimeError("fallo simulado al crear el perfil")
        db.profiles.append(dict(fields, id_usuario=id_usuario, tipo=kind))

    def insert_adulto_mayor_profile(self, db, id_usuario, **f):
        self._profile(db, id_usuario, "ADULTO_MAYOR", **f)

    def insert_universitario_profile(self, db, id_usuario, **f):
        self._profile(db, id_usuario, "UNIVERSITARIO",
                      estado_verificacion="PENDIENTE_VERIFICACION", **f)

    def insert_familiar_profile(self, db, id_usuario, **f):
        self._profile(db, id_usuario, "FAMILIAR", **f)

    def find_user_by_email(self, db, email):
        for u in db.users:
            if u["email"] == email:
                rol = {v: k for k, v in self.ROLES.items()}[u["id_rol"]]
                profile = next((p for p in db.profiles if p["id_usuario"] == u["id_usuario"]), {})
                return {
                    "id_usuario": u["id_usuario"],
                    "nombre_completo": u["nombre_completo"],
                    "email": u["email"],
                    "password_hash": u["password_hash"],
                    "estado": "ACTIVO",
                    "rol": rol,
                    "estado_verificacion": profile.get("estado_verificacion"),
                }
        return None


@pytest.fixture
def db(monkeypatch):
    fake = FakeDb()
    monkeypatch.setattr(auth_service, "get_connection", lambda: FakeConnection(fake))
    monkeypatch.setattr(auth_service, "repo", FakeRepo())
    return fake


@pytest.fixture
def client(db):
    return create_app().test_client()


def rut_with_dv(body):
    return f"{body}-{calculate_dv(body)}"


ADULTO = {
    "nombre_completo": "Rosa Muñoz Pérez",
    "rut": rut_with_dv("7654321"),
    "fecha_nacimiento": "1950-05-20",
    "telefono": "+56912345678",
    "email": "rosa@example.com",
    "password": "clave-segura-1",
    "direccion": "Av. Siempre Viva 123, Valdivia",
    "contacto_confianza_nombre": "Luis Muñoz",
    "contacto_confianza_telefono": "+56987654321",
    "indicaciones_acceso": "Portón verde, perro pequeño",
}

UNIVERSITARIO = {
    "nombre_completo": "Camila Rojas",
    "rut": rut_with_dv("20123456"),
    "fecha_nacimiento": "2002-03-10",
    "telefono": "+56911112222",
    "email": "camila@example.com",
    "password": "clave-segura-2",
    "universidad": "Universidad Austral",
    "carrera": "Enfermería",
    "anio_cursa": 3,
    "correo_institucional": "camila@alumnos.uach.cl",
    "contacto_emergencia_nombre": "Marta Rojas",
    "contacto_emergencia_telefono": "+56933334444",
}

FAMILIAR = {
    "nombre_completo": "Pedro Soto",
    "rut": rut_with_dv("12345678"),
    "telefono": "+56955556666",
    "email": "pedro@example.com",
    "password": "clave-segura-3",
    "parentesco": "Hijo",
}


# ---------- RUT ----------
def test_rut_normalization_and_validation():
    assert normalize_rut("12.345.678-5") == "12345678-5"
    assert is_valid_rut("12.345.678-5")
    assert not is_valid_rut("12.345.678-9")
    assert not is_valid_rut("abc")
    assert is_valid_rut("1-9") is False  # cuerpo demasiado corto


# ---------- Registro exitoso ----------
def test_register_adulto_mayor(client, db):
    res = client.post("/api/auth/register/adulto-mayor", json=ADULTO)
    assert res.status_code == 201
    body = res.get_json()
    assert body["success"] is True
    assert body["user"]["rol"] == "ADULTO_MAYOR"
    assert len(db.users) == 1 and db.profiles[0]["tipo"] == "ADULTO_MAYOR"
    assert "password" not in res.get_data(as_text=True)


def test_register_universitario_queda_pendiente(client, db):
    res = client.post("/api/auth/register/universitario", json=UNIVERSITARIO)
    assert res.status_code == 201
    assert res.get_json()["user"]["rol"] == "UNIVERSITARIO"
    assert db.profiles[0]["estado_verificacion"] == "PENDIENTE_VERIFICACION"


def test_register_familiar(client, db):
    res = client.post("/api/auth/register/familiar", json=FAMILIAR)
    assert res.status_code == 201
    assert res.get_json()["user"]["rol"] == "FAMILIAR"
    assert db.profiles[0]["tipo"] == "FAMILIAR"


def test_password_is_hashed_and_never_returned(client, db):
    res = client.post("/api/auth/register/familiar", json=FAMILIAR)
    stored = db.users[0]["password_hash"]
    assert stored != FAMILIAR["password"]
    assert FAMILIAR["password"] not in res.get_data(as_text=True)
    assert "password_hash" not in res.get_data(as_text=True)


# ---------- Duplicados ----------
def test_duplicate_email(client):
    client.post("/api/auth/register/familiar", json=FAMILIAR)
    other = dict(FAMILIAR, rut=rut_with_dv("11111111"), email="PEDRO@example.com")
    res = client.post("/api/auth/register/familiar", json=other)
    assert res.status_code == 409
    assert "email" in res.get_json()["errors"]


def test_duplicate_rut(client):
    client.post("/api/auth/register/familiar", json=FAMILIAR)
    other = dict(FAMILIAR, rut=FAMILIAR["rut"].replace("-", ""), email="otro@example.com")
    res = client.post("/api/auth/register/familiar", json=other)
    assert res.status_code == 409
    assert "rut" in res.get_json()["errors"]


# ---------- Validaciones ----------
def test_missing_required_fields(client, db):
    res = client.post("/api/auth/register/universitario", json={"email": "x@example.com"})
    assert res.status_code == 400
    errors = res.get_json()["errors"]
    assert "nombre_completo" in errors and "universidad" in errors
    assert db.users == []


def test_invalid_rut_check_digit(client):
    bad = dict(FAMILIAR, rut="12345678-0")
    res = client.post("/api/auth/register/familiar", json=bad)
    assert res.status_code == 400
    assert "rut" in res.get_json()["errors"]


def test_non_json_body(client):
    res = client.post("/api/auth/register/familiar", data="hola")
    assert res.status_code == 400


# ---------- Transacción ----------
def test_rollback_if_profile_fails(client, db):
    db.fail_profile = True
    res = client.post("/api/auth/register/adulto-mayor", json=ADULTO)
    assert res.status_code == 500
    assert db.users == [] and db.profiles == []  # no queda un usuario incompleto


# ---------- Login ----------
def test_login_ok_returns_role(client):
    client.post("/api/auth/register/universitario", json=UNIVERSITARIO)
    res = client.post("/api/auth/login", json={
        "email": "Camila@Example.com", "password": UNIVERSITARIO["password"]})
    assert res.status_code == 200
    user = res.get_json()["user"]
    assert user["rol"] == "UNIVERSITARIO"
    assert user["estado_verificacion"] == "PENDIENTE_VERIFICACION"
    assert "password_hash" not in res.get_data(as_text=True)


def test_login_wrong_password(client):
    client.post("/api/auth/register/familiar", json=FAMILIAR)
    res = client.post("/api/auth/login", json={"email": FAMILIAR["email"], "password": "incorrecta"})
    assert res.status_code == 401
    assert res.get_json()["success"] is False


def test_login_unknown_email(client):
    res = client.post("/api/auth/login", json={"email": "nadie@example.com", "password": "x"})
    assert res.status_code == 401


def test_login_missing_fields(client):
    res = client.post("/api/auth/login", json={"email": "a@b.cl"})
    assert res.status_code == 400

