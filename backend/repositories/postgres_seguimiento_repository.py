"""PostgreSQL (módulo aislado): seguimiento de servicios y auditoría, consultas parametrizadas."""
from datetime import datetime


def _all(cursor):
    keys = [c[0] for c in cursor.description]
    resultado = []
    for row in cursor.fetchall():
        item = dict(zip(keys, row))
        for key, value in list(item.items()):
            if isinstance(value, datetime):
                # Los eventos se almacenan en UTC; el horario solicitado sigue
                # siendo un datetime local definido por la versión anterior.
                item[key] = value.isoformat(timespec='seconds') + (
                    'Z' if key.endswith('_utc') else ''
                )
        resultado.append(item)
    return resultado


def listar_para_universitario(cursor, id_usuario):
    cursor.execute('''
        SELECT s.id_solicitud AS id, sv.nombre AS servicio,
               s.fecha_solicitada, s.estado,
               seg.fecha_llegada_utc, seg.fecha_inicio_utc,
               seg.fecha_termino_utc, seg.fecha_confirmacion_utc
        FROM public."Postulaciones" p
        INNER JOIN public."Solicitudes" s ON s.id_solicitud = p.id_solicitud
        INNER JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        LEFT JOIN public."SeguimientoServicios" seg ON seg.id_solicitud = s.id_solicitud
        WHERE p.id_universitario = %s AND p.estado = 'ACEPTADA'
        ORDER BY s.fecha_solicitada DESC, s.id_solicitud DESC
    ''', (id_usuario,))
    return _all(cursor)


def listar_para_adulto(cursor, id_usuario):
    cursor.execute('''
        SELECT s.id_solicitud AS id, sv.nombre AS servicio, s.fecha_solicitada,
               s.estado, es.nombre_completo AS estudiante_nombre,
               seg.fecha_llegada_utc, seg.fecha_inicio_utc,
               seg.fecha_termino_utc, seg.fecha_confirmacion_utc
        FROM public."Solicitudes" s
        INNER JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        LEFT JOIN public."Postulaciones" p ON p.id_solicitud = s.id_solicitud AND p.estado = 'ACEPTADA'
        LEFT JOIN public."Usuarios" es ON es.id_usuario = p.id_universitario
        LEFT JOIN public."SeguimientoServicios" seg ON seg.id_solicitud = s.id_solicitud
        WHERE s.id_adulto_mayor = %s
        ORDER BY s.fecha_solicitada DESC, s.id_solicitud DESC
    ''', (id_usuario,))
    return _all(cursor)


def listar_para_familiar(cursor, id_usuario):
    cursor.execute('''
        SELECT s.id_solicitud AS id, sv.nombre AS servicio, s.fecha_solicitada,
               s.estado, ad.nombre_completo AS adulto_nombre,
               es.nombre_completo AS estudiante_nombre,
               seg.fecha_llegada_utc, seg.fecha_inicio_utc,
               seg.fecha_termino_utc, seg.fecha_confirmacion_utc
        FROM public."Solicitudes" s
        INNER JOIN public."FamiliarAdultoMayor" v ON v.id_adulto_mayor = s.id_adulto_mayor
            AND v.id_familiar = %s AND v.activo = TRUE
        INNER JOIN public."Usuarios" ad ON ad.id_usuario = s.id_adulto_mayor AND ad.estado = 'ACTIVO'
        INNER JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        LEFT JOIN public."Postulaciones" p ON p.id_solicitud = s.id_solicitud AND p.estado = 'ACEPTADA'
        LEFT JOIN public."Usuarios" es ON es.id_usuario = p.id_universitario
        LEFT JOIN public."SeguimientoServicios" seg ON seg.id_solicitud = s.id_solicitud
        ORDER BY s.fecha_solicitada DESC, s.id_solicitud DESC
    ''', (id_usuario,))
    return _all(cursor)


def bloquear_solicitud(cursor, id_solicitud):
    """Bloquea una solicitud durante la transición (dos clicks no compiten)."""
    cursor.execute('''
        SELECT s.id_solicitud, s.id_adulto_mayor, s.estado, p.id_universitario
        FROM public."Solicitudes" s 
        LEFT JOIN public."Postulaciones" p ON p.id_solicitud = s.id_solicitud
            AND p.estado = 'ACEPTADA'
        WHERE s.id_solicitud = %s
        FOR UPDATE OF s
    ''', (id_solicitud,))
    row = cursor.fetchone()
    return None if row is None else {
        'id': row[0], 'id_adulto_mayor': row[1],
        'estado': row[2], 'id_estudiante': row[3],
    }


def estado_seguimiento(cursor, id_solicitud):
    cursor.execute('''
        SELECT fecha_llegada_utc, fecha_inicio_utc,
               fecha_termino_utc, fecha_confirmacion_utc
        FROM public."SeguimientoServicios" WHERE id_solicitud = %s
    ''', (id_solicitud,))
    row = cursor.fetchone()
    return None if row is None else {
        'llegada': row[0], 'inicio': row[1],
        'termino': row[2], 'confirmacion': row[3],
    }


def registrar_accion(cursor, id_solicitud, actor_id, accion):
    if accion == 'LLEGADA':
        cursor.execute('''
            INSERT INTO public."SeguimientoServicios"(id_solicitud, fecha_llegada_utc)
            VALUES (%s, (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'))
        ''', (id_solicitud,))
    elif accion == 'INICIO':
        cursor.execute('''
            UPDATE public."SeguimientoServicios" SET fecha_inicio_utc = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
            WHERE id_solicitud = %s AND fecha_llegada_utc IS NOT NULL AND fecha_inicio_utc IS NULL
        ''', (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('No se pudo registrar el inicio del servicio.')
        cursor.execute("""UPDATE public."Solicitudes" SET estado = 'EN_CURSO' WHERE id_solicitud = %s AND estado = 'ASIGNADA'""", (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('La solicitud cambió de estado inesperadamente.')
    elif accion == 'TERMINO':
        cursor.execute('''
            UPDATE public."SeguimientoServicios" SET fecha_termino_utc = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
            WHERE id_solicitud = %s AND fecha_inicio_utc IS NOT NULL AND fecha_termino_utc IS NULL
        ''', (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('No se pudo registrar el término.')
    elif accion == 'CONFIRMAR':
        cursor.execute('''
            UPDATE public."SeguimientoServicios"
            SET fecha_confirmacion_utc = (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'), id_confirmador = %s
            WHERE id_solicitud = %s AND fecha_termino_utc IS NOT NULL
              AND fecha_confirmacion_utc IS NULL
        ''', (actor_id, id_solicitud))
        if cursor.rowcount != 1:
            raise RuntimeError('No se pudo confirmar el servicio.')
        cursor.execute("""UPDATE public."Solicitudes" SET estado = 'FINALIZADA' WHERE id_solicitud = %s AND estado = 'EN_CURSO'""", (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('La solicitud cambió de estado inesperadamente.')
    cursor.execute('''
        INSERT INTO public."HistorialSeguimiento"(id_solicitud, id_actor, accion)
        VALUES (%s, %s, %s)
    ''', (id_solicitud, actor_id, accion))
