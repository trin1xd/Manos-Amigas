"""Flujo de llegada, inicio, término y confirmación; permisos por recurso."""
from database.connection import get_connection
from repositories import seguimiento_repository as repo
from repositories import operations_repository as ops_repo
from services.auth_service import ServiceError

ACCIONES = ('LLEGADA', 'INICIO', 'TERMINO', 'CONFIRMAR')


def _verificar_id(id_solicitud):
    if type(id_solicitud) is not int or id_solicitud <= 0:
        raise ServiceError('Identificador de solicitud inválido.', 400)


def _validar_pedido(accion, payload):
    if not isinstance(payload, dict) or payload.get('accion') != accion or accion not in ACCIONES:
        raise ServiceError('Acción inválida. Usa LLEGADA, INICIO, TERMINO o CONFIRMAR.', 400)
    if set(payload) != {'accion'}:
        raise ServiceError('No envíes campos adicionales; las fechas las registra el servidor.', 400)


def listar(user):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if user['rol'] == 'UNIVERSITARIO':
            return repo.listar_para_universitario(cursor, user['id'])
        if user['rol'] == 'ADULTO_MAYOR':
            return repo.listar_para_adulto(cursor, user['id'])
        if user['rol'] == 'FAMILIAR':
            return repo.listar_para_familiar(cursor, user['id'])
        raise ServiceError('Rol sin permiso.', 403)
    finally:
        conn.close()


def realizar(user, id_solicitud, datos):
    _verificar_id(id_solicitud)
    if not isinstance(datos, dict) or datos.get('accion') not in ACCIONES:
        raise ServiceError('Acción inválida.', 400)
    accion = datos['accion']
    _validar_pedido(accion, datos)
    conn = get_connection()
    try:
        cur = conn.cursor()
        solicitud = repo.bloquear_solicitud(cur, id_solicitud)
        if solicitud is None:
            raise ServiceError('Solicitud no encontrada.', 404)

        if accion in ('LLEGADA', 'INICIO', 'TERMINO'):
            if user['rol'] != 'UNIVERSITARIO' or solicitud['id_estudiante'] != user['id']:
                raise ServiceError('Solo el estudiante asignado puede registrar esta acción.', 403)
            if (user.get('estado_verificacion') != 'VERIFICADO'
                    or not ops_repo.estudiante_verificado(cur, user['id'])):
                raise ServiceError('La verificación del estudiante no está vigente.', 403)
        else:
            if user['rol'] == 'ADULTO_MAYOR':
                autorizado = solicitud['id_adulto_mayor'] == user['id']
            elif user['rol'] == 'FAMILIAR':
                vinculo = ops_repo.vinculo(cur, user['id'], solicitud['id_adulto_mayor'], lock=True)
                autorizado = bool(vinculo and vinculo['activo'] and
                                  ops_repo.adulto_activo(cur, solicitud['id_adulto_mayor']))
            else:
                autorizado = False
            if not autorizado:
                raise ServiceError('No estás autorizado para confirmar este servicio.', 403)

        seguimiento = repo.estado_seguimiento(cur, id_solicitud)
        anterior = seguimiento or {}
        estado = solicitud['estado']
        pasos = {
            'LLEGADA': estado == 'ASIGNADA' and seguimiento is None,
            'INICIO': estado == 'ASIGNADA' and anterior.get('llegada') is not None
                      and anterior.get('inicio') is None,
            'TERMINO': estado == 'EN_CURSO' and anterior.get('inicio') is not None
                       and anterior.get('termino') is None,
            'CONFIRMAR': estado == 'EN_CURSO' and anterior.get('termino') is not None
                         and anterior.get('confirmacion') is None,
        }
        if not pasos[accion]:
            raise ServiceError('La acción no corresponde al estado actual de la solicitud.', 409)

        repo.registrar_accion(cur, id_solicitud, user['id'], accion)
        conn.commit()
        return {'id': id_solicitud, 'accion': accion,
                'estado': 'EN_CURSO' if accion == 'INICIO' else
                          'FINALIZADA' if accion == 'CONFIRMAR' else estado}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
