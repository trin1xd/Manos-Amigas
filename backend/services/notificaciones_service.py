"""Bandeja de avisos: identidad y propiedad siempre proceden del JWT validado."""
from database.connection import get_connection
from repositories import notificaciones_repository as repo
from services.auth_service import ServiceError


def mias(usuario):
    conn = get_connection()
    try:
        items = repo.listar(conn.cursor(), usuario['id'])
        return {'notificaciones': items,
                'no_leidas': sum(item['leida_utc'] is None for item in items)}
    finally:
        conn.close()


def leer(usuario, id_notificacion):
    if type(id_notificacion) is not int or id_notificacion < 1:
        raise ServiceError('Identificador de notificación inválido.', 400)
    conn = get_connection()
    try:
        cambiado = repo.marcar_leida(conn.cursor(), usuario['id'], id_notificacion)
        conn.commit()
        if not cambiado:
            raise ServiceError('Aviso inexistente o ya leído.', 404)
        return {'id': id_notificacion, 'leida': True}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def leer_todas(usuario):
    conn = get_connection()
    try:
        cantidad = repo.marcar_todas(conn.cursor(), usuario['id'])
        conn.commit()
        return {'marcadas': cantidad}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
