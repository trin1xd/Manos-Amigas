"""Revisión administrativa de cuentas universitarias en entorno de PRUEBAS.

No constituye validación real de identidad, antecedentes o documentos.
"""
from database.connection import get_connection
from repositories import verificacion_repository as repo
from services.auth_service import ServiceError


def listado():
    conn = get_connection()
    try:
        return repo.listar_universitarios(conn.cursor())
    finally:
        conn.close()


def decidir(admin, id_universitario, datos):
    if isinstance(id_universitario, bool) or not isinstance(id_universitario, int) or id_universitario < 1:
        raise ServiceError('Identificador de universitario inválido.', 400)
    if not isinstance(datos, dict):
        raise ServiceError('Se esperaba un objeto JSON.', 400)
    accion = datos.get('accion')
    if accion not in ('APROBAR', 'RECHAZAR'):
        raise ServiceError('La acción debe ser APROBAR o RECHAZAR.', 400)
    observacion = datos.get('observacion')
    if not isinstance(observacion, str) or not 12 <= len(observacion.strip()) <= 500:
        raise ServiceError('Explica la decisión en 12 a 500 caracteres.', 400)
    observacion = observacion.strip()
    if accion == 'APROBAR' and datos.get('confirmacion_pruebas') is not True:
        raise ServiceError('Debes confirmar que esta habilitación es solo para pruebas.', 400)
    nuevo = 'VERIFICADO' if accion == 'APROBAR' else 'RECHAZADO'

    conn = get_connection()
    try:
        cursor = conn.cursor()
        actual = repo.bloquear_universitario(cursor, id_universitario)
        if actual is None:
            raise ServiceError('Universitario no encontrado o cuenta inactiva.', 404)
        if actual['estado'] != 'PENDIENTE_VERIFICACION':
            raise ServiceError('Solo se pueden revisar cuentas pendientes. Ya existe una decisión.', 409)
        if not repo.aplicar_decision(cursor, id_universitario, admin['id'], actual['estado'], nuevo, observacion):
            raise ServiceError('La cuenta cambió de estado; actualiza la lista.', 409)
        conn.commit()
        return {'id': id_universitario, 'estado_verificacion': nuevo}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
