"""API operativa para adultos mayores, universitarios y familiares."""
from flask import Blueprint, g, jsonify, request

from services import operations_service as ops
from services.auth_service import ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO, ServiceError
from utils.auth_decorators import require_role

ops_bp = Blueprint('operaciones', __name__)


def _payload():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ServiceError('Se esperaba un objeto JSON.', 400)
    return body


def _call(func, *args):
    try:
        return func(*args)
    except ServiceError as error:
        data = {'success': False, 'message': error.message}
        if error.errors:
            data['errors'] = error.errors
        return jsonify(data), error.status


def _ok(result, status=200, field=None):
    return jsonify({'success': True, (field or 'data'): result}), status


@ops_bp.get('/catalogo/servicios')
@require_role(ADULTO_MAYOR, FAMILIAR, UNIVERSITARIO)
def servicios():
    return _ok(ops.catalogo(), field='servicios')


@ops_bp.post('/solicitudes')
@require_role(ADULTO_MAYOR, FAMILIAR)
def crear_solicitud():
    try:
        body = _payload()
    except ServiceError as error:
        return jsonify({'success': False, 'message': error.message}), error.status
    result = _call(ops.crear_solicitud, g.current_user, body)
    if isinstance(result, tuple):
        return result
    return _ok(result, 201, 'solicitud')


@ops_bp.get('/solicitudes/mias')
@require_role(ADULTO_MAYOR, FAMILIAR)
def mis_solicitudes():
    return _ok(ops.mis_solicitudes(g.current_user), field='solicitudes')


@ops_bp.get('/solicitudes/disponibles')
@require_role(UNIVERSITARIO)
def solicitudes_disponibles():
    result = _call(ops.disponibles, g.current_user)
    return result if isinstance(result, tuple) else _ok(result, field='solicitudes')


@ops_bp.post('/solicitudes/<int:solicitud_id>/postular')
@require_role(UNIVERSITARIO)
def postular(solicitud_id):
    result = _call(ops.postular, g.current_user, solicitud_id)
    return result if isinstance(result, tuple) else _ok(result, 201, 'postulacion')


@ops_bp.get('/postulaciones/mias')
@require_role(UNIVERSITARIO)
def mis_postulaciones():
    return _ok(ops.mis_postulaciones(g.current_user), field='postulaciones')


@ops_bp.get('/solicitudes/<int:solicitud_id>/postulaciones')
@require_role(ADULTO_MAYOR, FAMILIAR)
def postulantes(solicitud_id):
    result = _call(ops.ver_postulantes, g.current_user, solicitud_id)
    return result if isinstance(result, tuple) else _ok(result, field='postulaciones')


@ops_bp.post('/solicitudes/<int:solicitud_id>/postulaciones/<int:postulacion_id>/aceptar')
@require_role(ADULTO_MAYOR, FAMILIAR)
def aceptar(solicitud_id, postulacion_id):
    result = _call(ops.aceptar, g.current_user, solicitud_id, postulacion_id)
    return result if isinstance(result, tuple) else _ok(result, field='solicitud')


@ops_bp.post('/solicitudes/<int:solicitud_id>/cancelar')
@require_role(ADULTO_MAYOR, FAMILIAR)
def cancelar(solicitud_id):
    result = _call(ops.cancelar, g.current_user, solicitud_id)
    return result if isinstance(result, tuple) else _ok(result, field='solicitud')


@ops_bp.post('/familiares/vincular')
@require_role(ADULTO_MAYOR)
def vincular():
    try:
        body = _payload()
    except ServiceError as error:
        return jsonify({'success': False, 'message': error.message}), error.status
    result = _call(ops.vincular_familiar, g.current_user, body)
    return result if isinstance(result, tuple) else _ok(result, 201, 'vinculo')


@ops_bp.delete('/familiares/<int:id_familiar>/vinculo')
@require_role(ADULTO_MAYOR)
def desvincular(id_familiar):
    result = _call(ops.desvincular_familiar, g.current_user, id_familiar)
    return result if isinstance(result, tuple) else _ok(result, field='vinculo')


@ops_bp.get('/familiares/adultos')
@require_role(FAMILIAR)
def adultos_vinculados():
    return _ok(ops.mis_adultos(g.current_user), field='adultos')
