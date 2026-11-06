"""Rutas JWT de notificaciones; no acepta id_usuario desde el navegador."""
from flask import Blueprint, g, jsonify
from services import notificaciones_service as servicio
from services.auth_service import ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO, ServiceError
from utils.auth_decorators import require_role

notificaciones_bp = Blueprint('notificaciones', __name__)
ROLES = (ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO)


@notificaciones_bp.get('/notificaciones/mias')
@require_role(*ROLES)
def mias():
    return jsonify({'success': True, **servicio.mias(g.current_user)})


@notificaciones_bp.post('/notificaciones/<int:id_notificacion>/leer')
@require_role(*ROLES)
def leer(id_notificacion):
    try:
        resultado = servicio.leer(g.current_user, id_notificacion)
    except ServiceError as error:
        return jsonify({'success': False, 'message': error.message}), error.status
    return jsonify({'success': True, **resultado})


@notificaciones_bp.post('/notificaciones/leer-todas')
@require_role(*ROLES)
def leer_todas():
    return jsonify({'success': True, **servicio.leer_todas(g.current_user)})
