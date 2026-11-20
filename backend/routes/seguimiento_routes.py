"""Rutas JWT de seguimiento de servicios para los tres perfiles."""
from flask import Blueprint, g, jsonify, request, current_app
import segno
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


@seguimiento_bp.post('/seguimiento/solicitudes/<int:id_solicitud>/qr-llegada')
@require_role(ADULTO_MAYOR, FAMILIAR)
def mostrar_qr_llegada(id_solicitud):
    # Nunca generar enlaces a orígenes arbitrarios: solo previews autorizados.
    origin = request.headers.get('Origin', '').rstrip('/')
    if origin not in current_app.config['CORS_ORIGINS']:
        return jsonify({'success': False, 'message': 'El origen no está autorizado.'}), 403
    try:
        token = svc.generar_qr_llegada(g.current_user, id_solicitud)
    except ServiceError as err:
        return jsonify({'success': False, 'message': err.message}), err.status
    url = origin + '/#/llegada/' + token
    qr = segno.make_qr(url, error='m')
    return jsonify({
        'success': True,
        'qr_svg': qr.svg_data_uri(scale=5, border=2),
        'expira_en_segundos': svc.QR_MAX_AGE_SEGUNDOS,
    })


@seguimiento_bp.post('/seguimiento/llegada/qr')
@require_role(UNIVERSITARIO)
def confirmar_qr_llegada():
    data = request.get_json(silent=True)
    try:
        if not isinstance(data, dict) or set(data) != {'token'}:
            raise ServiceError('El código QR es obligatorio.', 400)
        result = svc.registrar_llegada_desde_qr(g.current_user, data['token'])
    except ServiceError as err:
        return jsonify({'success': False, 'message': err.message}), err.status
    return jsonify({'success': True, 'seguimiento': result})
