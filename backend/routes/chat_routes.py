"""Chat de servicios asignados: JWT y autorización por conversación."""
from flask import Blueprint, g, jsonify, request
from services import chat_service as svc
from services.auth_service import ADULTO_MAYOR, UNIVERSITARIO, FAMILIAR, ServiceError
from utils.auth_decorators import require_role

chat_bp = Blueprint('chat', __name__)
ROLES = (ADULTO_MAYOR, UNIVERSITARIO, FAMILIAR)


def _error(error):
    return jsonify({'success': False, 'message': error.message}), error.status


@chat_bp.get('/chat/conversaciones')
@require_role(*ROLES)
def conversaciones():
    return jsonify({'success': True, 'conversaciones': svc.conversaciones(g.current_user)})


@chat_bp.get('/chat/solicitudes/<int:id_solicitud>/mensajes')
@require_role(*ROLES)
def mensajes(id_solicitud):
    try:
        datos = svc.mensajes(g.current_user, id_solicitud)
    except ServiceError as exc:
        return _error(exc)
    return jsonify({'success': True, 'mensajes': datos})


@chat_bp.post('/chat/solicitudes/<int:id_solicitud>/mensajes')
@require_role(*ROLES)
def enviar(id_solicitud):
    try:
        dato = svc.enviar(g.current_user, id_solicitud, request.get_json(silent=True))
    except ServiceError as exc:
        return _error(exc)
    return jsonify({'success': True, 'mensaje': dato}), 201
