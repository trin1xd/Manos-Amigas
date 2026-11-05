"""Rutas JWT de seguimiento de servicios para los tres perfiles."""
from flask import Blueprint, g, jsonify, request
from services import seguimiento_service as svc
from services.auth_service import ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO, ServiceError
from utils.auth_decorators import require_role

seguimiento_bp = Blueprint('seguimiento', __name__)


@seguimiento_bp.get('/seguimiento/mios')
@require_role(ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO)
def mios():
    return jsonify({'success': True, 'servicios': svc.listar(g.current_user)})


@seguimiento_bp.post('/seguimiento/solicitudes/<int:id_solicitud>/accion')
@require_role(ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO)
def accion(id_solicitud):
    try:
        result = svc.realizar(g.current_user, id_solicitud, request.get_json(silent=True))
    except ServiceError as err:
        return jsonify({'success': False, 'message': err.message}), err.status
    return jsonify({'success': True, 'seguimiento': result})
