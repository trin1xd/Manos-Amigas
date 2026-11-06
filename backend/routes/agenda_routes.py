"""Agenda: el cliente no puede escoger id_usuario ni ver servicios de terceros."""
from flask import Blueprint, g, jsonify
from services import agenda_service as agenda
from services.auth_service import ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO
from utils.auth_decorators import require_role

agenda_bp = Blueprint('agenda', __name__)


@agenda_bp.get('/agenda/mia')
@require_role(ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO)
def mi_agenda():
    return jsonify({'success': True, 'servicios': agenda.mia(g.current_user)})
