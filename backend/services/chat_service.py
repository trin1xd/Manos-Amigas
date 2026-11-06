"""Permisos por solicitud para el chat interno, sin mensajes entre desconocidos."""
from database.connection import get_connection
from repositories import chat_repository as repo
from repositories import operations_repository as ops_repo
from services.auth_service import ServiceError


def _id(value):
    if type(value) is not int or value <= 0:
        raise ServiceError('Identificador inválido.', 400)


def _autorizado(cur, usuario, contexto):
    if not contexto:
        raise ServiceError('Conversación no disponible.', 404)
    rol = usuario['rol']
    if rol == 'UNIVERSITARIO' and usuario['id'] == contexto['id_universitario']:
        return
    if rol == 'ADULTO_MAYOR' and usuario['id'] == contexto['id_adulto']:
        return
    if rol == 'FAMILIAR':
        vinculo = ops_repo.vinculo(cur, usuario['id'], contexto['id_adulto'])
        if vinculo and vinculo['activo'] and ops_repo.adulto_activo(cur, contexto['id_adulto']):
            return
    # No revelar a ajenos detalles ni siquiera la existencia de la solicitud.
    raise ServiceError('Conversación no disponible.', 404)


def conversaciones(usuario):
    conn = get_connection()
    try:
        return repo.conversaciones(conn.cursor(), usuario['id'])
    finally:
        conn.close()


def mensajes(usuario, solicitud_id):
    _id(solicitud_id)
    conn = get_connection()
    try:
        cur = conn.cursor()
        contexto = repo.contexto(cur, solicitud_id)
        _autorizado(cur, usuario, contexto)
        return repo.listar_mensajes(cur, solicitud_id)
    finally:
        conn.close()


def enviar(usuario, solicitud_id, payload):
    _id(solicitud_id)
    if not isinstance(payload, dict) or set(payload) != {'mensaje'}:
        raise ServiceError('Escribe un mensaje válido.', 400)
    texto = payload['mensaje']
    if not isinstance(texto, str) or not 1 <= len(texto.strip()) <= 500:
        raise ServiceError('El mensaje debe tener entre 1 y 500 caracteres.', 400)
    texto = texto.strip()
    if any((ord(c) < 32 and c not in '\n\t') for c in texto):
        raise ServiceError('El mensaje contiene caracteres no permitidos.', 400)
    conn = get_connection()
    try:
        cur = conn.cursor()
        contexto = repo.contexto(cur, solicitud_id, bloquear=True)
        _autorizado(cur, usuario, contexto)
        if contexto['estado'] not in ('ASIGNADA', 'EN_CURSO'):
            raise ServiceError('La conversación está cerrada para nuevos mensajes.', 409)
        if usuario['rol'] == 'UNIVERSITARIO' and usuario.get('estado_verificacion') != 'VERIFICADO':
            raise ServiceError('El universitario debe mantener su verificación vigente.', 403)
        if repo.limite_rapidez(cur, solicitud_id, usuario['id']):
            raise ServiceError('Espera unos segundos antes de enviar otro mensaje.', 429)
        mensaje_id = repo.guardar(cur, solicitud_id, usuario['id'], texto)
        conn.commit()
        return {'id': mensaje_id, 'id_solicitud': solicitud_id}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
