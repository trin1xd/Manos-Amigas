"""Casos de uso de operaciones para los tres perfiles de Manos Amigas.

Las comprobaciones de rol del endpoint se complementan con autorización sobre
cada recurso; los IDs enviados por cliente nunca acreditan propiedad.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta
import re

from database.connection import get_connection
from repositories import operations_repository as repo
from repositories import notificaciones_repository as notif_repo
from repositories import agenda_repository as agenda_repo
from services.auth_service import ServiceError


@contextmanager
def _db(write=False):
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        if write:
            conn.commit()
    except Exception:
        if write:
            conn.rollback()
        raise
    finally:
        conn.close()


def _id(value, nombre='Identificador'):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ServiceError(f'{nombre} debe ser un entero positivo.', 400)
    return value


def _text(value, nombre, min_len, max_len):
    if not isinstance(value, str):
        raise ServiceError(f'{nombre} debe ser texto.', 400)
    result = value.strip()
    if not min_len <= len(result) <= max_len:
        raise ServiceError(f'{nombre} debe tener entre {min_len} y {max_len} caracteres.', 400)
    return result


def _fecha(fecha, hora):
    if not isinstance(fecha, str) or not isinstance(hora, str):
        raise ServiceError('Fecha y hora son obligatorias.', 400)
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', fecha) or not re.fullmatch(r'\d{2}:\d{2}', hora):
        raise ServiceError('Usa fecha AAAA-MM-DD y hora HH:MM.', 400)
    try:
        inicio = datetime.strptime(f'{fecha} {hora}', '%Y-%m-%d %H:%M')
    except ValueError as err:
        raise ServiceError('Fecha u hora inválida.', 400) from err
    # MVP: tiempos de pared en la zona horaria LOCAL del servidor (configurar Chile).
    if not datetime.now() < inicio <= datetime.now() + timedelta(days=366):
        raise ServiceError('La solicitud debe programarse en una fecha futura (máximo 366 días).', 400)
    return inicio


def catalogo():
    with _db() as cursor:
        return repo.servicios(cursor)


def _autorizado_para_adulto(cursor, user, adult_id, lock=False):
    # Se llama solo desde rutas con @require_role(ADULTO_MAYOR, FAMILIAR).
    if user['rol'] == 'ADULTO_MAYOR':
        return user['id'] == adult_id
    if user['rol'] == 'FAMILIAR':
        relacion = repo.vinculo(cursor, user['id'], adult_id, lock=lock)
        return bool(relacion and relacion['activo']) and bool(repo.adulto_activo(cursor, adult_id))
    return False


def crear_solicitud(user, payload):
    service_id = _id(payload.get('id_servicio'), 'id_servicio')
    duracion = _id(payload.get('duracion_horas'), 'duracion_horas')
    if duracion not in (1, 2, 3):
        raise ServiceError('La duración debe ser 1, 2 o 3 horas.', 400)
    fecha = _fecha(payload.get('fecha'), payload.get('hora'))
    descripcion = _text(payload.get('descripcion'), 'La descripción', 10, 500)

    if user['rol'] == 'ADULTO_MAYOR':
        adult_id = user['id']
    else:
        adult_id = _id(payload.get('id_adulto_mayor'), 'id_adulto_mayor')

    with _db(write=True) as cursor:
        if not _autorizado_para_adulto(cursor, user, adult_id, lock=True):
            raise ServiceError('No tienes permiso para solicitar tareas para este adulto mayor.', 403)
        if not repo.servicio_activo(cursor, service_id):
            raise ServiceError('Servicio inexistente o inactivo.', 404)
        created = repo.crear_solicitud(cursor, user['id'], adult_id, service_id,
                                      fecha, duracion, descripcion)
        return {'id': created['id'], 'estado': 'PENDIENTE', 'id_adulto_mayor': adult_id}


def mis_solicitudes(user):
    with _db() as cursor:
        if user['rol'] == 'ADULTO_MAYOR':
            return repo.solicitudes_adulto(cursor, user['id'])
        return repo.solicitudes_familiar(cursor, user['id'])


def disponibles(user):
    if user.get('estado_verificacion') != 'VERIFICADO':
        raise ServiceError('Tu perfil universitario debe estar verificado para consultar tareas.', 403)
    with _db() as cursor:
        # Segunda comprobación en la BD antes de consultar datos de terceros.
        if not repo.estudiante_verificado(cursor, user['id']):
            raise ServiceError('Tu verificación no está vigente.', 403)
        return repo.solicitudes_disponibles(cursor)


def postular(user, solicitud_id):
    solicitud_id = _id(solicitud_id, 'id_solicitud')
    if user.get('estado_verificacion') != 'VERIFICADO':
        raise ServiceError('Solo pueden postular universitarios verificados.', 403)
    with _db(write=True) as cursor:
        if not repo.estudiante_verificado(cursor, user['id']):
            raise ServiceError('Tu verificación no está vigente.', 403)
        sol = repo.solicitud(cursor, solicitud_id, lock=True)
        if not sol:
            raise ServiceError('Solicitud no encontrada.', 404)
        if sol['estado'] != 'PENDIENTE' or datetime.fromisoformat(sol['fecha_solicitada']) <= datetime.now():
            raise ServiceError('Esta solicitud ya no admite postulaciones.', 409)
        if repo.postulacion_existente(cursor, solicitud_id, user['id']):
            raise ServiceError('Ya postulaste a esta solicitud.', 409)
        created = repo.crear_postulacion(cursor, solicitud_id, user['id'])
        notif_repo.avisar_adulto_y_familia(cursor, solicitud_id, 'POSTULACION', user['id'])
        return {'id': created['id'], 'id_solicitud': solicitud_id, 'estado': 'PENDIENTE'}


def mis_postulaciones(user):
    with _db() as cursor:
        return repo.mis_postulaciones(cursor, user['id'])


def _solicitud_autorizada(cursor, user, solicitud_id, lock=False):
    sol = repo.solicitud(cursor, solicitud_id, lock=lock)
    if not sol:
        raise ServiceError('Solicitud no encontrada.', 404)
    if not sol['id_adulto_mayor'] or not _autorizado_para_adulto(cursor, user, sol['id_adulto_mayor'], lock=lock):
        raise ServiceError('No tienes acceso a esta solicitud.', 403)
    return sol


def ver_postulantes(user, solicitud_id):
    with _db() as cursor:
        _solicitud_autorizada(cursor, user, solicitud_id)
        return repo.postulaciones_solicitud(cursor, solicitud_id)


def aceptar(user, solicitud_id, postulacion_id):
    with _db(write=True) as cursor:
        sol = _solicitud_autorizada(cursor, user, solicitud_id, lock=True)
        if sol['estado'] != 'PENDIENTE' or datetime.fromisoformat(sol['fecha_solicitada']) <= datetime.now():
            raise ServiceError('La solicitud ya no está disponible para asignar.', 409)
        post = repo.postulacion_aceptable(cursor, solicitud_id, postulacion_id)
        if not post or post['estado'] != 'PENDIENTE':
            raise ServiceError('La postulación no está disponible o el estudiante ya no está verificado.', 409)
        # El bloqueo de estudiante y la comprobación ocurren bajo esta MISMA transacción.
        # Si hay cruce de horas, no se modifica ni la solicitud ni los avisos.
        if agenda_repo.conflicto_de_aceptacion(cursor, solicitud_id, postulacion_id):
            raise ServiceError('Este universitario ya tiene otro servicio asignado en ese horario.', 409)
        if not repo.aceptar_postulacion(cursor, solicitud_id, postulacion_id):
            raise ServiceError('La postulación ya cambió de estado.', 409)
        notif_repo.avisar_adulto_y_familia(cursor, solicitud_id, 'ASIGNACION', user['id'])
        notif_repo.avisar_postulante(cursor, solicitud_id, postulacion_id, 'ASIGNACION', user['id'])
        notif_repo.avisar_postulantes_no_seleccionados(cursor, solicitud_id, postulacion_id, user['id'])
        return {'id': solicitud_id, 'estado': 'ASIGNADA', 'id_postulacion_aceptada': postulacion_id}


def cancelar(user, solicitud_id):
    with _db(write=True) as cursor:
        sol = _solicitud_autorizada(cursor, user, solicitud_id, lock=True)
        if sol['estado'] not in ('PENDIENTE', 'ASIGNADA'):
            raise ServiceError('No se puede cancelar una solicitud en este estado.', 409)
        repo.cancelar_solicitud(cursor, solicitud_id)
        notif_repo.avisar_adulto_y_familia(cursor, solicitud_id, 'CANCELACION', user['id'])
        notif_repo.avisar_cancelacion(cursor, solicitud_id, user['id'])
        return {'id': solicitud_id, 'estado': 'CANCELADA'}


def vincular_familiar(user, payload):
    email = _text(payload.get('email_familiar'), 'Correo del familiar', 3, 255).lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        raise ServiceError('Correo del familiar inválido.', 400)
    parentesco = _text(payload.get('parentesco'), 'Parentesco', 2, 100)
    with _db(write=True) as cursor:
        family = repo.familiar_por_correo(cursor, email)
        if not family:
            raise ServiceError('No existe una cuenta familiar activa con ese correo.', 404)
        current = repo.vinculo(cursor, family['id'], user['id'], lock=True)
        if current and current['activo']:
            raise ServiceError('Este familiar ya tiene acceso.', 409)
        if current:
            repo.activar_vinculo(cursor, current['id'], parentesco)
            relation_id = current['id']
        else:
            relation_id = repo.crear_vinculo(cursor, family['id'], user['id'], parentesco)['id']
        return {'id': relation_id, 'id_familiar': family['id'], 'activo': True}


def desvincular_familiar(user, id_familiar):
    with _db(write=True) as cursor:
        current = repo.vinculo(cursor, id_familiar, user['id'], lock=True)
        if not current or not current['activo']:
            raise ServiceError('Vínculo no encontrado.', 404)
        repo.desactivar_vinculo(cursor, current['id'])
        return {'id_familiar': id_familiar, 'activo': False}


def mis_familiares(user):
    """Devuelve solo familiares activos autorizados por este adulto mayor."""
    with _db() as cursor:
        return repo.familiares_vinculados(cursor, user['id'])


def mis_adultos(user):
    with _db() as cursor:
        return repo.adultos_vinculados(cursor, user['id'])
