"""Decoradores de autorización y control de acceso basado en roles."""
from functools import wraps
from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from services import auth_service
from services.auth_service import ServiceError


def require_role(*roles):
    """Decorador para proteger rutas requiriendo uno o más roles específicos.

    Verifica el JWT, carga el usuario fresco desde la base de datos (rechazando cuentas
    inactivas o bloqueadas), valida el rol real contra la base y almacena el usuario
    en flask.g.current_user.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            user_id = get_jwt_identity()
            try:
                user = auth_service.get_user_by_id(user_id)
            except ServiceError as error:
                return jsonify({"success": False, "message": error.message}), error.status

            if roles and user["rol"] not in roles:
                return jsonify({
                    "success": False,
                    "message": "No tiene permisos para acceder a este recurso.",
                }), 403

            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator

