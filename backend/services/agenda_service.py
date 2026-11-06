"""Agenda de servicios autorizada por usuario autenticado."""
from database.connection import get_connection
from repositories import agenda_repository as repo
from services.auth_service import ServiceError

ROLES = ('UNIVERSITARIO', 'ADULTO_MAYOR', 'FAMILIAR')


def mia(usuario):
    if usuario.get('rol') not in ROLES:
        raise ServiceError('No tienes acceso a esta agenda.', 403)
    conn = get_connection()
    try:
        return repo.listar(conn.cursor(), usuario['rol'], usuario['id'])
    finally:
        conn.close()
