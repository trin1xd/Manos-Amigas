"""Consultas PostgreSQL para solicitudes, postulaciones y vínculos (módulo inactivo).

Todas las escrituras reciben un cursor y su transacción se controla en services.
No se devuelven direcciones, teléfonos ni datos de contacto privados.
"""
from datetime import date, datetime


def _serialize(value):
    if isinstance(value, datetime):
        return value.isoformat(timespec='minutes')
    if isinstance(value, date):
        return value.isoformat()
    return value


def _one(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    keys = [column[0] for column in cursor.description]
    return {key: _serialize(value) for key, value in zip(keys, row)}


def _all(cursor):
    keys = [column[0] for column in cursor.description]
    return [{key: _serialize(value) for key, value in zip(keys, row)}
            for row in cursor.fetchall()]


def servicios(cursor):
    cursor.execute('''
        SELECT id_servicio AS id, nombre, descripcion
        FROM public."Servicios" WHERE activo = TRUE ORDER BY nombre
    ''')
    return _all(cursor)


def servicio_activo(cursor, service_id):
    cursor.execute('SELECT id_servicio AS id FROM public."Servicios" WHERE id_servicio = %s AND activo = TRUE', (service_id,))
    return _one(cursor)


def familiar_por_correo(cursor, email):
    cursor.execute('''
        SELECT u.id_usuario AS id, u.nombre_completo AS nombre
        FROM public."Usuarios" u
        INNER JOIN public."PerfilFamiliar" f ON f.id_usuario = u.id_usuario
        INNER JOIN public."Roles" r ON r.id_rol = u.id_rol
        WHERE u.email = %s AND u.estado = 'ACTIVO' AND r.nombre = 'FAMILIAR'
    ''', (email,))
    return _one(cursor)


def vinculo(cursor, id_familiar, id_adulto, lock=False):
    locking = 'FOR UPDATE' if lock else ''
    cursor.execute(f'''
        SELECT id_relacion AS id, activo
        FROM public."FamiliarAdultoMayor"
        WHERE id_familiar = %s AND id_adulto_mayor = %s
        {locking}
    ''', (id_familiar, id_adulto))
    return _one(cursor)


def crear_vinculo(cursor, id_familiar, id_adulto, parentesco):
    cursor.execute('''
        INSERT INTO public."FamiliarAdultoMayor"(id_familiar, id_adulto_mayor, parentesco, activo)
        VALUES (%s, %s, %s, TRUE)
        RETURNING id_relacion AS id
    ''', (id_familiar, id_adulto, parentesco))
    return _one(cursor)


def activar_vinculo(cursor, id_relacion, parentesco):
    cursor.execute('''UPDATE public."FamiliarAdultoMayor"
        SET activo = TRUE, parentesco = %s WHERE id_relacion = %s''', (parentesco, id_relacion))


def desactivar_vinculo(cursor, id_relacion):
    cursor.execute('UPDATE public."FamiliarAdultoMayor" SET activo = FALSE WHERE id_relacion = %s', (id_relacion,))


def familiares_vinculados(cursor, id_adulto):
    """Lista de familiares autorizados; no expone teléfonos ni datos de terceros."""
    cursor.execute('''
        SELECT u.id_usuario AS id, u.nombre_completo AS nombre,
               u.email, v.parentesco
        FROM public."FamiliarAdultoMayor" AS v
        INNER JOIN public."Usuarios" AS u ON u.id_usuario = v.id_familiar
        INNER JOIN public."Roles" AS r ON r.id_rol = u.id_rol
        WHERE v.id_adulto_mayor = %s AND v.activo = TRUE
          AND u.estado = 'ACTIVO' AND r.nombre = 'FAMILIAR'
        ORDER BY u.nombre_completo, u.id_usuario
    ''', (id_adulto,))
    return _all(cursor)


def adultos_vinculados(cursor, id_familiar):
    cursor.execute('''
        SELECT u.id_usuario AS id, u.nombre_completo AS nombre, v.parentesco
        FROM public."FamiliarAdultoMayor" v
        INNER JOIN public."Usuarios" u ON u.id_usuario = v.id_adulto_mayor
        INNER JOIN public."Roles" r ON r.id_rol = u.id_rol
        WHERE v.id_familiar = %s AND v.activo = TRUE AND u.estado = 'ACTIVO'
          AND r.nombre = 'ADULTO_MAYOR'
        ORDER BY u.nombre_completo
    ''', (id_familiar,))
    return _all(cursor)


def crear_solicitud(cursor, solicitante, adulto, servicio, fecha, duracion, descripcion):
    cursor.execute('''
        INSERT INTO public."Solicitudes"
            (id_solicitante, id_adulto_mayor, id_servicio,
             fecha_solicitada, duracion_horas, descripcion, estado)
        VALUES (%s, %s, %s, %s, %s, %s, 'PENDIENTE')
        RETURNING id_solicitud AS id
    ''', (solicitante, adulto, servicio, fecha, duracion, descripcion))
    return _one(cursor)


def solicitudes_adulto(cursor, id_adulto):
    cursor.execute('''
        SELECT s.id_solicitud AS id, s.id_adulto_mayor, s.id_solicitante,
               sv.nombre AS servicio, s.fecha_solicitada, s.duracion_horas,
               s.descripcion, s.estado
        FROM public."Solicitudes" s
        JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        WHERE s.id_adulto_mayor = %s
        ORDER BY s.fecha_creacion DESC, s.id_solicitud DESC
    ''', (id_adulto,))
    return _all(cursor)


def solicitudes_familiar(cursor, id_familiar):
    cursor.execute('''
        SELECT s.id_solicitud AS id, s.id_adulto_mayor,
               u.nombre_completo AS adulto_nombre,
               sv.nombre AS servicio, s.fecha_solicitada, s.duracion_horas,
               s.descripcion, s.estado
        FROM public."Solicitudes" s
        INNER JOIN public."FamiliarAdultoMayor" v
            ON v.id_adulto_mayor = s.id_adulto_mayor
            AND v.id_familiar = %s AND v.activo = TRUE
        INNER JOIN public."Usuarios" u ON u.id_usuario = s.id_adulto_mayor
        INNER JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        WHERE u.estado = 'ACTIVO'
        ORDER BY s.fecha_creacion DESC, s.id_solicitud DESC
    ''', (id_familiar,))
    return _all(cursor)


def solicitudes_disponibles(cursor):
    # El nombre identifica al beneficiario; no se exponen teléfono, RUT ni dirección.
    cursor.execute('''
        SELECT s.id_solicitud AS id, sv.nombre AS servicio,
               adulto.nombre_completo AS adulto_nombre,
               s.fecha_solicitada, s.duracion_horas, s.estado
        FROM public."Solicitudes" s
        INNER JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        INNER JOIN public."Usuarios" adulto ON adulto.id_usuario = s.id_adulto_mayor
        WHERE s.estado = 'PENDIENTE' AND s.fecha_solicitada > CURRENT_TIMESTAMP
          AND s.id_adulto_mayor IS NOT NULL AND sv.activo = TRUE
          AND adulto.estado = 'ACTIVO'
        ORDER BY s.fecha_solicitada, s.id_solicitud
        LIMIT 100
    ''')
    return _all(cursor)


def solicitud(cursor, id_solicitud, lock=False):
    locking = 'FOR UPDATE' if lock else ''
    cursor.execute(f'''
        SELECT s.id_solicitud AS id, s.id_adulto_mayor,
               s.estado, s.fecha_solicitada
        FROM public."Solicitudes" s
        WHERE s.id_solicitud = %s
        {locking}
    ''', (id_solicitud,))
    return _one(cursor)


def estudiante_verificado(cursor, student_id):
    cursor.execute('''
        SELECT u.id_usuario AS id
        FROM public."PerfilUniversitario" p
        INNER JOIN public."Usuarios" u ON u.id_usuario = p.id_usuario
        INNER JOIN public."Roles" r ON r.id_rol = u.id_rol
        WHERE p.id_usuario = %s AND u.estado = 'ACTIVO'
          AND r.nombre = 'UNIVERSITARIO'
          AND p.estado_verificacion = 'VERIFICADO'
        LIMIT 1
    ''', (student_id,))
    return _one(cursor)


def estudiante_pendiente_feria(cursor, student_id):
    """En la feria admite acceso temporal solo a estudiantes activos pendientes."""
    cursor.execute('''
        SELECT u.id_usuario AS id
        FROM public."PerfilUniversitario" p
        JOIN public."Usuarios" u ON u.id_usuario=p.id_usuario
        JOIN public."Roles" r ON r.id_rol=u.id_rol
        WHERE p.id_usuario=%s AND u.estado='ACTIVO'
          AND r.nombre='UNIVERSITARIO'
          AND p.estado_verificacion='PENDIENTE_VERIFICACION'
        LIMIT 1
    ''', (student_id,))
    return _one(cursor)


def postulacion_existente(cursor, solicitud_id, student_id):
    cursor.execute('''
        SELECT id_postulacion AS id FROM public."Postulaciones"
        WHERE id_solicitud = %s AND id_universitario = %s
    ''', (solicitud_id, student_id))
    return _one(cursor)


def crear_postulacion(cursor, solicitud_id, student_id):
    cursor.execute('''
        INSERT INTO public."Postulaciones"(id_solicitud, id_universitario)
        VALUES (%s, %s)
        RETURNING id_postulacion AS id
    ''', (solicitud_id, student_id))
    return _one(cursor)


def mis_postulaciones(cursor, student_id):
    cursor.execute('''
        SELECT p.id_postulacion AS id, p.id_solicitud,
               sv.nombre AS servicio, adulto.nombre_completo AS adulto_nombre,
               s.fecha_solicitada,
               p.estado, s.estado AS estado_solicitud,
               p.fecha_creacion
        FROM public."Postulaciones" p
        JOIN public."Solicitudes" s ON s.id_solicitud = p.id_solicitud
        JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        JOIN public."Usuarios" adulto ON adulto.id_usuario = s.id_adulto_mayor
        WHERE p.id_universitario = %s
        ORDER BY p.fecha_creacion DESC, p.id_postulacion DESC
    ''', (student_id,))
    return _all(cursor)


def postulaciones_solicitud(cursor, solicitud_id):
    # Ficha del estudiante para quien decide: solo universidad, carrera, año de estudios
    # y estado de verificación. No se exponen RUT, correo, teléfono ni contacto de emergencia.
    cursor.execute('''
        SELECT p.id_postulacion AS id, p.id_universitario,
               u.nombre_completo AS estudiante_nombre, p.estado,
               p.fecha_creacion,
               pu.universidad AS estudiante_universidad,
               pu.carrera AS estudiante_carrera,
               pu.anio_cursa AS estudiante_anio,
               pu.estado_verificacion AS estudiante_verificacion,
               notas.promedio AS estudiante_calificacion_promedio,
               notas.total AS estudiante_calificaciones_total
        FROM public."Postulaciones" p
        JOIN public."Usuarios" u ON u.id_usuario = p.id_universitario
        LEFT JOIN public."PerfilUniversitario" pu ON pu.id_usuario = p.id_universitario
        LEFT JOIN LATERAL (
            SELECT ROUND(AVG(c.puntaje)::numeric, 1)::double precision AS promedio,
                   COUNT(*)::integer AS total
            FROM public."Calificaciones" c
            WHERE c.id_evaluado = p.id_universitario
              AND c.tipo = 'ADULTO_A_UNIVERSITARIO'
        ) notas ON TRUE
        WHERE p.id_solicitud = %s
        ORDER BY p.fecha_creacion, p.id_postulacion
    ''', (solicitud_id,))
    return _all(cursor)


def postulacion_aceptable(cursor, solicitud_id, post_id):
    cursor.execute('''
        SELECT p.id_postulacion AS id, p.estado
        FROM public."Postulaciones" p
        JOIN public."PerfilUniversitario" u ON u.id_usuario = p.id_universitario
        JOIN public."Usuarios" cuenta ON cuenta.id_usuario = p.id_universitario
        JOIN public."Roles" rol ON rol.id_rol = cuenta.id_rol
        WHERE p.id_solicitud = %s AND p.id_postulacion = %s
          AND u.estado_verificacion = 'VERIFICADO'
          AND cuenta.estado = 'ACTIVO' AND rol.nombre = 'UNIVERSITARIO'
    ''', (solicitud_id, post_id))
    return _one(cursor)


def postulacion_aceptable_feria(cursor, solicitud_id, post_id):
    """Permite aceptar cuentas pendientes en la demo; no las verifica."""
    cursor.execute('''
        SELECT p.id_postulacion AS id, p.estado
        FROM public."Postulaciones" p
        JOIN public."PerfilUniversitario" u ON u.id_usuario = p.id_universitario
        JOIN public."Usuarios" cuenta ON cuenta.id_usuario = p.id_universitario
        JOIN public."Roles" rol ON rol.id_rol = cuenta.id_rol
        WHERE p.id_solicitud = %s AND p.id_postulacion = %s
          AND u.estado_verificacion IN ('VERIFICADO', 'PENDIENTE_VERIFICACION')
          AND cuenta.estado = 'ACTIVO' AND rol.nombre = 'UNIVERSITARIO'
    ''', (solicitud_id, post_id))
    return _one(cursor)


def aceptar_postulacion(cursor, solicitud_id, post_id):
    cursor.execute('''
        UPDATE public."Postulaciones" SET estado = 'ACEPTADA'
        WHERE id_postulacion = %s AND id_solicitud = %s AND estado = 'PENDIENTE'
    ''', (post_id, solicitud_id))
    if cursor.rowcount != 1:
        return False
    cursor.execute('''
        UPDATE public."Postulaciones" SET estado = 'RECHAZADA'
        WHERE id_solicitud = %s AND id_postulacion <> %s AND estado = 'PENDIENTE'
    ''', (solicitud_id, post_id))
    cursor.execute("UPDATE public.\"Solicitudes\" SET estado = 'ASIGNADA' WHERE id_solicitud = %s", (solicitud_id,))
    return True


def cancelar_solicitud(cursor, solicitud_id):
    cursor.execute("UPDATE public.\"Solicitudes\" SET estado = 'CANCELADA' WHERE id_solicitud = %s", (solicitud_id,))
    cursor.execute('''
        UPDATE public."Postulaciones" SET estado = 'RECHAZADA'
        WHERE id_solicitud = %s AND estado IN ('PENDIENTE', 'ACEPTADA')
    ''', (solicitud_id,))


def adulto_activo(cursor, adult_id):
    cursor.execute('''
        SELECT a.id_usuario AS id
        FROM public."PerfilAdultoMayor" a
        INNER JOIN public."Usuarios" u ON u.id_usuario = a.id_usuario
        INNER JOIN public."Roles" r ON r.id_rol = u.id_rol
        WHERE a.id_usuario = %s AND u.estado = 'ACTIVO' AND r.nombre = 'ADULTO_MAYOR'
        LIMIT 1
    ''', (adult_id,))
    return _one(cursor)
