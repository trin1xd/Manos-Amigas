from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Correo y contraseña son obligatorios."}), 400

    # TODO: reemplazar por autenticación contra SQL Server.
    return jsonify({
        "message": "Endpoint preparado. Falta implementar autenticación real.",
        "implemented": False,
    }), 501


@auth_bp.post("/register")
def register():
    # TODO: validar datos y registrar el usuario mediante la capa de servicios.
    return jsonify({
        "message": "Endpoint preparado. Falta implementar registro real.",
        "implemented": False,
    }), 501
