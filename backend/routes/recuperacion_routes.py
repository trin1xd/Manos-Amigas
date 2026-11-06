"""Rutas públicas de recuperación de contraseña, con mensajes no enumerables."""
from flask import Blueprint, jsonify, request
from services import recuperacion_service as svc
from services.auth_service import ServiceError

recuperacion_bp = Blueprint('recuperacion', __name__)


def _handle(method):
    try:
        mensaje = method(request.get_json(silent=True))
    except ServiceError as exc:
        return jsonify({'success': False, 'message': exc.message}), exc.status
    return jsonify({'success': True, 'message': mensaje})


@recuperacion_bp.post('/auth/recuperacion/solicitar')
def solicitar():
    return _handle(svc.solicitar)


@recuperacion_bp.post('/auth/recuperacion/confirmar')
def confirmar():
    return _handle(svc.confirmar)
