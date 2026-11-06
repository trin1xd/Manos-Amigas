"""Verificacion del correo institucional: solo universitario autenticado."""
from flask import Blueprint, g, jsonify, request
from services import verificacion_institucional_service as svc
from services.auth_service import ServiceError
from utils.auth_decorators import require_role

institucional_bp = Blueprint('verificacion_institucional', __name__)


def _error(error):
    return jsonify({'success': False, 'message': error.message}), error.status


@institucional_bp.get('/verificacion-institucional/mia')
@require_role('UNIVERSITARIO')
def mi_estado():
    try:
        return jsonify({'success': True, 'data': svc.estado(g.current_user)})
    except ServiceError as error:
        return _error(error)


@institucional_bp.post('/verificacion-institucional/enviar-codigo')
@require_role('UNIVERSITARIO')
def enviar_codigo():
    try:
        return jsonify({'success': True, **svc.solicitar_codigo(g.current_user)})
    except ServiceError as error:
        return _error(error)


@institucional_bp.post('/verificacion-institucional/confirmar-codigo')
@require_role('UNIVERSITARIO')
def confirmar_codigo():
    try:
        return jsonify({'success': True, **svc.confirmar_codigo(g.current_user, request.get_json(silent=True))})
    except ServiceError as error:
        return _error(error)
