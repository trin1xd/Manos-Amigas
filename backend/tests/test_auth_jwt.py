"""Pruebas automáticas para autenticación persistente con JWT y control de acceso.

Valida:
- Emisión de token en login.
- Consulta de usuario actual en GET /api/auth/me con validación de estado en BD.
- Formato uniforme de errores 401 (sin token, token corrupto, token expirado).
- Protección de endpoints con @require_role (200 para rol permitido, 403 para no autorizado).
- Bloqueo inmediato de cuentas inactivas (403).
- Invalidez de tokens antiguos cuando cambia el rol en la base de datos.
- Ausencia total de contraseñas o password_hash en respuestas.
"""
from datetime import timedelta
from pathlib import Path
import sys

import pytest
from flask_jwt_extended import create_access_token, decode_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from services import auth_service
from tests.test_auth import (
    ADULTO,
    FAMILIAR,
    UNIVERSITARIO,
    FakeConnection,
    FakeDb,
    FakeRepo,
)


class JwtFakeRepo(FakeRepo):
    """Extiende FakeRepo añadiendo find_user_by_id de forma puramente aditiva."""

    def find_user_by_id(self, db, user_id):
        try:
            uid = int(user_id)
        except (ValueError, TypeError):
            return None

        for u in db.users:
            if u["id_usuario"] == uid:
                rol = {v: k for k, v in self.ROLES.items()}[u["id_rol"]]
                profile = next((p for p in db.profiles if p["id_usuario"] == u["id_usuario"]), {})
                return {
                    "id_usuario": u["id_usuario"],
                    "nombre_completo": u["nombre_completo"],
                    "email": u["email"],
                    "password_hash": u["password_hash"],
                    "estado": u.get("estado", "ACTIVO"),
                    "rol": rol,
                    "estado_verificacion": profile.get("estado_verificacion"),
                }
        return None

    def find_user_by_email(self, db, email):
        res = super().find_user_by_email(db, email)
        if res:
            for u in db.users:
                if u["id_usuario"] == res["id_usuario"]:
                    res["estado"] = u.get("estado", "ACTIVO")
                    break
        return res


@pytest.fixture
def db(monkeypatch):
    fake = FakeDb()
    repo = JwtFakeRepo()
    monkeypatch.setattr(auth_service, "get_connection", lambda: FakeConnection(fake))
    monkeypatch.setattr(auth_service, "repo", repo)
    return fake


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app, db):
    return app.test_client()


def _login_and_get_token(client, register_endpoint, user_data):
    """Helper para registrar usuario, iniciar sesión y obtener su access_token."""
    reg_res = client.post(register_endpoint, json=user_data)
    assert reg_res.status_code == 201

    login_res = client.post("/api/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"],
    })
    assert login_res.status_code == 200
    body = login_res.get_json()
    assert "access_token" in body
    return body["access_token"], body


# 1. Login devuelve access_token
def test_login_returns_access_token_and_valid_claims(client, app):
    token, body = _login_and_get_token(client, "/api/auth/register/universitario", UNIVERSITARIO)
    assert isinstance(token, str) and len(token) > 20
    assert body["success"] is True
    assert body["user"]["rol"] == "UNIVERSITARIO"
    assert body["user"]["estado"] == "ACTIVO"
    assert body["user"]["estado_verificacion"] == "PENDIENTE_VERIFICACION"

    # Verificar claims internos del JWT
    with app.app_context():
        decoded = decode_token(token)
        assert decoded["sub"] == str(body["user"]["id"])
        assert decoded["rol"] == "UNIVERSITARIO"


# 2. /me con token válido devuelve el usuario correcto
def test_get_me_with_valid_token_adulto_mayor(client):
    token, login_body = _login_and_get_token(client, "/api/auth/register/adulto-mayor", ADULTO)
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["id"] == login_body["user"]["id"]
    assert data["user"]["nombre"] == ADULTO["nombre_completo"]
    assert data["user"]["rol"] == "ADULTO_MAYOR"
    assert data["user"]["estado"] == "ACTIVO"
    assert "estado_verificacion" not in data["user"]


def test_get_me_with_valid_token_universitario(client):
    token, login_body = _login_and_get_token(client, "/api/auth/register/universitario", UNIVERSITARIO)
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["rol"] == "UNIVERSITARIO"
    assert data["user"]["estado_verificacion"] == "PENDIENTE_VERIFICACION"


# 3. /me sin token, token basura y token expirado responden 401 en español
def test_get_me_missing_token_returns_401(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    body = res.get_json()
    assert body["success"] is False
    assert body["message"] == "Token de autenticación no proporcionado."


def test_get_me_invalid_token_returns_401(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer token_corrupto_invalido"})
    assert res.status_code == 401
    body = res.get_json()
    assert body["success"] is False
    assert body["message"] == "Token de autenticación inválido."


def test_get_me_expired_token_returns_401(client, app):
    with app.app_context():
        expired_token = create_access_token(
            identity="1",
            additional_claims={"rol": "UNIVERSITARIO"},
            expires_delta=timedelta(seconds=-1),
        )

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    body = res.get_json()
    assert body["success"] is False
    assert body["message"] == "El token de autenticación ha expirado."


# 4. Control de acceso por rol: ADULTO_MAYOR recibe 403 y UNIVERSITARIO recibe 200
def test_role_protection_forbids_wrong_role_and_allows_correct_role(client):
    token_adulto, _ = _login_and_get_token(client, "/api/auth/register/adulto-mayor", ADULTO)
    res_adulto = client.get(
        "/api/auth/prueba-universitario",
        headers={"Authorization": f"Bearer {token_adulto}"},
    )
    assert res_adulto.status_code == 403
    body_adulto = res_adulto.get_json()
    assert body_adulto["success"] is False
    assert body_adulto["message"] == "No tiene permisos para acceder a este recurso."

    token_uni, _ = _login_and_get_token(client, "/api/auth/register/universitario", UNIVERSITARIO)
    res_uni = client.get(
        "/api/auth/prueba-universitario",
        headers={"Authorization": f"Bearer {token_uni}"},
    )
    assert res_uni.status_code == 200
    body_uni = res_uni.get_json()
    assert body_uni["success"] is True
    assert body_uni["user"]["rol"] == "UNIVERSITARIO"


# 5. Cuenta no activa recibe 403 de inmediato
def test_inactive_account_blocked_returns_403(client, db):
    token_uni, login_body = _login_and_get_token(
        client, "/api/auth/register/universitario", UNIVERSITARIO
    )

    # Simular bloqueo de cuenta por administración en la base de datos
    user_id = login_body["user"]["id"]
    for u in db.users:
        if u["id_usuario"] == user_id:
            u["estado"] = "BLOQUEADO"

    # GET /me debe rechazar con 403
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_uni}"})
    assert res_me.status_code == 403
    assert res_me.get_json()["message"] == "La cuenta no está activa."

    # Ruta protegida por rol también debe rechazar con 403
    res_role = client.get(
        "/api/auth/prueba-universitario",
        headers={"Authorization": f"Bearer {token_uni}"},
    )
    assert res_role.status_code == 403
    assert res_role.get_json()["message"] == "La cuenta no está activa."


def test_inactive_account_desactivado_returns_403(client, db):
    token_uni, login_body = _login_and_get_token(
        client, "/api/auth/register/universitario", UNIVERSITARIO
    )

    user_id = login_body["user"]["id"]
    for u in db.users:
        if u["id_usuario"] == user_id:
            u["estado"] = "DESACTIVADO"

    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_uni}"})
    assert res_me.status_code == 403
    assert res_me.get_json()["message"] == "La cuenta no está activa."


# 6. Si cambia el rol en la base, token viejo con rol desactualizado ya no da acceso
def test_stale_token_with_old_role_is_rejected_when_db_role_changes(client, db):
    # Emitir token para usuario que inicialmente era UNIVERSITARIO
    token_stale, login_body = _login_and_get_token(
        client, "/api/auth/register/universitario", UNIVERSITARIO
    )

    # Cambiar rol en base de datos a ADULTO_MAYOR
    user_id = login_body["user"]["id"]
    for u in db.users:
        if u["id_usuario"] == user_id:
            u["id_rol"] = JwtFakeRepo.ROLES["ADULTO_MAYOR"]

    # El token aún contiene {"rol": "UNIVERSITARIO"} en sus claims,
    # pero el endpoint protegido debe consultar la BD y rechazarlo con 403.
    res = client.get(
        "/api/auth/prueba-universitario",
        headers={"Authorization": f"Bearer {token_stale}"},
    )
    assert res.status_code == 403
    assert res.get_json()["message"] == "No tiene permisos para acceder a este recurso."


# 7. Ninguna respuesta incluye password ni password_hash
def test_sensitive_passwords_never_returned_in_any_response(client):
    token, login_body = _login_and_get_token(client, "/api/auth/register/familiar", FAMILIAR)

    # Login
    login_str = str(login_body)
    assert FAMILIAR["password"] not in login_str
    assert "password_hash" not in login_str

    # GET /me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    me_str = me_res.get_data(as_text=True)
    assert FAMILIAR["password"] not in me_str
    assert "password_hash" not in me_str

    # Ruta de rol con universitario
    uni_token, _ = _login_and_get_token(client, "/api/auth/register/universitario", UNIVERSITARIO)
    role_res = client.get(
        "/api/auth/prueba-universitario",
        headers={"Authorization": f"Bearer {uni_token}"},
    )
    role_str = role_res.get_data(as_text=True)
    assert UNIVERSITARIO["password"] not in role_str
    assert "password_hash" not in role_str

