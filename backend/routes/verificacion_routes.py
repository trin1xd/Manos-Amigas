"""API exclusiva de ADMIN para habilitar cuentas ficticias de demostración."""
import os
from flask import Blueprint, g, jsonify, request
from services import verificacion_service as svc
from services.auth_service import ServiceError
from utils.auth_decorators import require_role

verificacion_bp = Blueprint('verificacion_admin', __name__)


def _error(error):
    return jsonify({'success': False, 'message': error.message}), error.status


@verificacion_bp.get('/universitarios')
@require_role('ADMIN')
def universitarios():
    return jsonify({'success': True, 'universitarios': svc.listado()})


@verificacion_bp.post('/universitarios/<int:id_universitario>/decision')
@require_role('ADMIN')
def decision(id_universitario):
    # El ADMIN puede habilitar cuentas de demostración en Render sin activar Flask debug.
    # El modo debe habilitarse expresamente en el entorno de evaluación.
    habilitado = os.getenv('ADMIN_VERIFICACION_PRUEBAS', '').lower() == 'true'
    if not habilitado:
        return jsonify({'success': False, 'message': 'La habilitación administrativa de pruebas está desactivada.'}), 403
    datos = request.get_json(silent=True)
    try:
        resultado = svc.decidir(g.current_user, id_universitario, datos)
    except ServiceError as error:
        return _error(error)
    return jsonify({'success': True, 'universitario': resultado})
