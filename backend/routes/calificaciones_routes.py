"""Rutas protegidas de calificaciones de servicios finalizados."""
from flask import Blueprint, g, jsonify, request
from services import calificaciones_service as servicio
from services.auth_service import ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO, ServiceError
from utils.auth_decorators import require_role

calificaciones_bp = Blueprint('calificaciones', __name__)


@calificaciones_bp.get('/calificaciones/mias')
@require_role(ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO)
def mias():
    return jsonify({'success': True, 'servicios': servicio.listar(g.current_user)})


@calificaciones_bp.post('/calificaciones/solicitudes/<int:id_solicitud>')
@require_role(ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO)
def evaluar(id_solicitud):
    try:
        resultado = servicio.evaluar(g.current_user, id_solicitud, request.get_json(silent=True))
    except ServiceError as err:
        return jsonify({'success': False, 'message': err.message}), err.status
    return jsonify({'success': True, 'calificacion': resultado}), 201
