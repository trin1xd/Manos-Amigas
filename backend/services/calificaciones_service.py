"""Reglas de negocio para evaluaciones posteriores a la confirmación del servicio."""
import pyodbc
from database.connection import get_connection
from repositories import calificaciones_repository as repo
from repositories import operations_repository as ops_repo
from services.auth_service import ServiceError


def listar(usuario):
    conn = get_connection()
    try:
        return repo.listar(conn.cursor(), usuario)
    finally:
        conn.close()


def evaluar(usuario, id_solicitud, datos):
    if type(id_solicitud) is not int or id_solicitud <= 0:
        raise ServiceError('Solicitud inválida.', 400)
    if not isinstance(datos, dict) or set(datos) - {'puntaje', 'comentario'}:
        raise ServiceError('Solo se permiten puntaje y comentario.', 400)
    puntaje = datos.get('puntaje')
    if type(puntaje) is not int or not 1 <= puntaje <= 5:
        raise ServiceError('El puntaje debe ser un entero entre 1 y 5.', 400)
    comentario = datos.get('comentario', '')
    if not isinstance(comentario, str) or len(comentario.strip()) > 300:
        raise ServiceError('El comentario debe tener máximo 300 caracteres.', 400)
    comentario = comentario.strip() or None

    conn = get_connection()
    try:
        cur = conn.cursor()
        sol = repo.solicitud_finalizada(cur, id_solicitud)
        if not sol:
            raise ServiceError('Solo se pueden calificar servicios finalizados y confirmados.', 409)
        rol = usuario['rol']
        if rol == 'UNIVERSITARIO' and usuario['id'] == sol['id_universitario']:
            tipo = 'UNIVERSITARIO_A_ADULTO'
            evaluado = sol['id_adulto']
        elif rol == 'ADULTO_MAYOR' and usuario['id'] == sol['id_adulto']:
            tipo = 'ADULTO_A_UNIVERSITARIO'
            evaluado = sol['id_universitario']
        elif rol == 'FAMILIAR':
            vinculo = ops_repo.vinculo(cur, usuario['id'], sol['id_adulto'], lock=True)
            if not vinculo or not vinculo['activo'] or not ops_repo.adulto_activo(cur, sol['id_adulto']):
                raise ServiceError('No tienes autorización para evaluar este servicio.', 403)
            tipo = 'ADULTO_A_UNIVERSITARIO'
            evaluado = sol['id_universitario']
        else:
            raise ServiceError('No tienes autorización para evaluar este servicio.', 403)

        if repo.existe(cur, id_solicitud, tipo):
            raise ServiceError('Este servicio ya tiene una calificación desde tu perfil.', 409)
        id_calificacion = repo.registrar(cur, id_solicitud, usuario['id'], evaluado,
                                         tipo, puntaje, comentario)
        conn.commit()
        return {'id': id_calificacion, 'id_solicitud': id_solicitud, 'puntaje': puntaje}
    except pyodbc.IntegrityError as exc:
        conn.rollback()
        raise ServiceError('Este servicio ya fue calificado o no pudo guardarse.', 409) from exc
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
