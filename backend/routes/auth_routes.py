from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from services import auth_service
from services.auth_service import ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO, ServiceError
from utils.auth_decorators import require_role

auth_bp = Blueprint("auth", __name__)


def _error(error):
    body = {"success": False, "message": error.message}
    if error.errors:
        body["errors"] = error.errors
    return jsonify(body), error.status


def _register(role):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Se esperaba un cuerpo JSON."}), 400
    try:
        user = auth_service.register_user(role, data)
    except ServiceError as error:
        return _error(error)
    return jsonify({
        "success": True,
        "message": "Usuario registrado correctamente",
        "user": user,
    }), 201


@auth_bp.post("/register/adulto-mayor")
def register_adulto_mayor():
    return _register(ADULTO_MAYOR)


@auth_bp.post("/register/universitario")
def register_universitario():
    return _register(UNIVERSITARIO)


@auth_bp.post("/register/familiar")
def register_familiar():
    return _register(FAMILIAR)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Se esperaba un cuerpo JSON."}), 400
    try:
        user = auth_service.login(data.get("email"), data.get("password"))
    except ServiceError as error:
        return _error(error)
    access_token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"rol": user["rol"]},
    )
    return jsonify({
        "success": True,
        "message": "Inicio de sesión correcto",
        "user": user,
        "access_token": access_token,
    })


@auth_bp.get("/me")
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    try:
        user = auth_service.get_user_by_id(user_id)
    except ServiceError as error:
        return _error(error)
    return jsonify({"success": True, "user": user})


@auth_bp.get("/prueba-universitario")
@require_role(UNIVERSITARIO)
def prueba_universitario():
    return jsonify({
        "success": True,
        "message": "Acceso permitido a universitario.",
        "user": g.current_user,
    })
