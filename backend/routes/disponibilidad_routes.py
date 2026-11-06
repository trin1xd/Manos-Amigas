"""Disponibilidad semanal. Edición exclusiva del universitario autenticado."""
from flask import Blueprint, g, jsonify, request
from services import disponibilidad_service as servicio
from services.auth_service import UNIVERSITARIO, ServiceError
from utils.auth_decorators import require_role

disponibilidad_bp = Blueprint('disponibilidad', __name__)


@disponibilidad_bp.get('/disponibilidad/mia')
@require_role(UNIVERSITARIO)
def mia():
    return jsonify({'success': True, 'franjas': servicio.mia(g.current_user)})


@disponibilidad_bp.put('/disponibilidad/mia')
@require_role(UNIVERSITARIO)
def guardar():
    try:
        franjas = servicio.guardar(g.current_user, request.get_json(silent=True))
    except ServiceError as error:
        return jsonify({'success': False, 'message': error.message}), error.status
    return jsonify({'success': True, 'franjas': franjas})
