"""Consultas parametrizadas para solicitudes, postulaciones y vínculos.

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
        FROM dbo.Servicios WHERE activo = 1 ORDER BY nombre
    ''')
    return _all(cursor)


def servicio_activo(cursor, service_id):
    cursor.execute('SELECT id_servicio AS id FROM dbo.Servicios WHERE id_servicio = ? AND activo = 1', (service_id,))
    return _one(cursor)


def familiar_por_correo(cursor, email):
    cursor.execute('''
        SELECT u.id_usuario AS id, u.nombre_completo AS nombre
        FROM dbo.Usuarios u
        INNER JOIN dbo.PerfilFamiliar f ON f.id_usuario = u.id_usuario
        INNER JOIN dbo.Roles r ON r.id_rol = u.id_rol
        WHERE u.email = ? AND u.estado = 'ACTIVO' AND r.nombre = 'FAMILIAR'
    ''', (email,))
    return _one(cursor)


def vinculo(cursor, id_familiar, id_adulto, lock=False):
    hint = 'WITH (UPDLOCK, HOLDLOCK)' if lock else ''
    cursor.execute(f'''
        SELECT id_relacion AS id, activo
        FROM dbo.FamiliarAdultoMayor {hint}
        WHERE id_familiar = ? AND id_adulto_mayor = ?
    ''', (id_familiar, id_adulto))
    return _one(cursor)


def crear_vinculo(cursor, id_familiar, id_adulto, parentesco):
    cursor.execute('''
        INSERT INTO dbo.FamiliarAdultoMayor(id_familiar, id_adulto_mayor, parentesco, activo)
        OUTPUT INSERTED.id_relacion AS id
        VALUES (?, ?, ?, 1)
    ''', (id_familiar, id_adulto, parentesco))
    return _one(cursor)


def activar_vinculo(cursor, id_relacion, parentesco):
    cursor.execute('''UPDATE dbo.FamiliarAdultoMayor
        SET activo = 1, parentesco = ? WHERE id_relacion = ?''', (parentesco, id_relacion))


def desactivar_vinculo(cursor, id_relacion):
    cursor.execute('UPDATE dbo.FamiliarAdultoMayor SET activo = 0 WHERE id_relacion = ?', (id_relacion,))


def familiares_vinculados(cursor, id_adulto):
    """Lista de familiares autorizados; no expone teléfonos ni datos de terceros."""
    cursor.execute('''
        SELECT u.id_usuario AS id, u.nombre_completo AS nombre,
               u.email, v.parentesco
        FROM dbo.FamiliarAdultoMayor AS v
        INNER JOIN dbo.Usuarios AS u ON u.id_usuario = v.id_familiar
        INNER JOIN dbo.Roles AS r ON r.id_rol = u.id_rol
        WHERE v.id_adulto_mayor = ? AND v.activo = 1
          AND u.estado = 'ACTIVO' AND r.nombre = 'FAMILIAR'
        ORDER BY u.nombre_completo, u.id_usuario
    ''', (id_adulto,))
    return _all(cursor)


def adultos_vinculados(cursor, id_familiar):
    cursor.execute('''
        SELECT u.id_usuario AS id, u.nombre_completo AS nombre, v.parentesco
        FROM dbo.FamiliarAdultoMayor v
        INNER JOIN dbo.Usuarios u ON u.id_usuario = v.id_adulto_mayor
        INNER JOIN dbo.Roles r ON r.id_rol = u.id_rol
        WHERE v.id_familiar = ? AND v.activo = 1 AND u.estado = 'ACTIVO'
          AND r.nombre = 'ADULTO_MAYOR'
        ORDER BY u.nombre_completo
    ''', (id_familiar,))
    return _all(cursor)


def crear_solicitud(cursor, solicitante, adulto, servicio, fecha, duracion, descripcion):
    cursor.execute('''
        INSERT INTO dbo.Solicitudes
            (id_solicitante, id_adulto_mayor, id_servicio,
             fecha_solicitada, duracion_horas, descripcion, estado)
        OUTPUT INSERTED.id_solicitud AS id
        VALUES (?, ?, ?, ?, ?, ?, 'PENDIENTE')
    ''', (solicitante, adulto, servicio, fecha, duracion, descripcion))
    return _one(cursor)


def solicitudes_adulto(cursor, id_adulto):
    cursor.execute('''
        SELECT s.id_solicitud AS id, s.id_adulto_mayor, s.id_solicitante,
               sv.nombre AS servicio, s.fecha_solicitada, s.duracion_horas,
               s.descripcion, s.estado
        FROM dbo.Solicitudes s
        JOIN dbo.Servicios sv ON sv.id_servicio = s.id_servicio
        WHERE s.id_adulto_mayor = ?
        ORDER BY s.fecha_creacion DESC, s.id_solicitud DESC
    ''', (id_adulto,))
    return _all(cursor)


def solicitudes_familiar(cursor, id_familiar):
    cursor.execute('''
        SELECT s.id_solicitud AS id, s.id_adulto_mayor,
               u.nombre_completo AS adulto_nombre,
               sv.nombre AS servicio, s.fecha_solicitada, s.duracion_horas,
               s.descripcion, s.estado
        FROM dbo.Solicitudes s
        INNER JOIN dbo.FamiliarAdultoMayor v
            ON v.id_adulto_mayor = s.id_adulto_mayor
            AND v.id_familiar = ? AND v.activo = 1
        INNER JOIN dbo.Usuarios u ON u.id_usuario = s.id_adulto_mayor
        INNER JOIN dbo.Servicios sv ON sv.id_servicio = s.id_servicio
        WHERE u.estado = 'ACTIVO'
        ORDER BY s.fecha_creacion DESC, s.id_solicitud DESC
    ''', (id_familiar,))
    return _all(cursor)


def solicitudes_disponibles(cursor):
    # No divulgar nombre, dirección, teléfono ni descripción libre del adulto mayor.
    cursor.execute('''
        SELECT TOP (100) s.id_solicitud AS id, sv.nombre AS servicio,
               s.fecha_solicitada, s.duracion_horas, s.estado
        FROM dbo.Solicitudes s
        INNER JOIN dbo.Servicios sv ON sv.id_servicio = s.id_servicio
        WHERE s.estado = 'PENDIENTE' AND s.fecha_solicitada > SYSDATETIME()
          AND s.id_adulto_mayor IS NOT NULL AND sv.activo = 1
        ORDER BY s.fecha_solicitada, s.id_solicitud
    ''')
    return _all(cursor)


def solicitud(cursor, id_solicitud, lock=False):
    hint = 'WITH (UPDLOCK, HOLDLOCK)' if lock else ''
    cursor.execute(f'''
        SELECT s.id_solicitud AS id, s.id_adulto_mayor,
               s.estado, s.fecha_solicitada
        FROM dbo.Solicitudes s {hint}
        WHERE s.id_solicitud = ?
    ''', (id_solicitud,))
    return _one(cursor)


def estudiante_verificado(cursor, student_id):
    cursor.execute('''
        SELECT TOP (1) u.id_usuario AS id
        FROM dbo.PerfilUniversitario p
        INNER JOIN dbo.Usuarios u ON u.id_usuario = p.id_usuario
        INNER JOIN dbo.Roles r ON r.id_rol = u.id_rol
        WHERE p.id_usuario = ? AND u.estado = 'ACTIVO'
          AND r.nombre = 'UNIVERSITARIO'
          AND p.estado_verificacion = 'VERIFICADO'
    ''', (student_id,))
    return _one(cursor)


def postulacion_existente(cursor, solicitud_id, student_id):
    cursor.execute('''
        SELECT id_postulacion AS id FROM dbo.Postulaciones
        WHERE id_solicitud = ? AND id_universitario = ?
    ''', (solicitud_id, student_id))
    return _one(cursor)


def crear_postulacion(cursor, solicitud_id, student_id):
    cursor.execute('''
        INSERT INTO dbo.Postulaciones(id_solicitud, id_universitario)
        OUTPUT INSERTED.id_postulacion AS id
        VALUES (?, ?)
    ''', (solicitud_id, student_id))
    return _one(cursor)


def mis_postulaciones(cursor, student_id):
    cursor.execute('''
        SELECT p.id_postulacion AS id, p.id_solicitud,
               sv.nombre AS servicio, s.fecha_solicitada,
               p.estado, s.estado AS estado_solicitud,
               p.fecha_creacion
        FROM dbo.Postulaciones p
        JOIN dbo.Solicitudes s ON s.id_solicitud = p.id_solicitud
        JOIN dbo.Servicios sv ON sv.id_servicio = s.id_servicio
        WHERE p.id_universitario = ?
        ORDER BY p.fecha_creacion DESC, p.id_postulacion DESC
    ''', (student_id,))
    return _all(cursor)


def postulaciones_solicitud(cursor, solicitud_id):
    cursor.execute('''
        SELECT p.id_postulacion AS id, p.id_universitario,
               u.nombre_completo AS estudiante_nombre, p.estado,
               p.fecha_creacion
        FROM dbo.Postulaciones p
        JOIN dbo.Usuarios u ON u.id_usuario = p.id_universitario
        WHERE p.id_solicitud = ?
        ORDER BY p.fecha_creacion, p.id_postulacion
    ''', (solicitud_id,))
    return _all(cursor)


def postulacion_aceptable(cursor, solicitud_id, post_id):
    cursor.execute('''
        SELECT p.id_postulacion AS id, p.estado
        FROM dbo.Postulaciones p
        JOIN dbo.PerfilUniversitario u ON u.id_usuario = p.id_universitario
        JOIN dbo.Usuarios cuenta ON cuenta.id_usuario = p.id_universitario
        JOIN dbo.Roles rol ON rol.id_rol = cuenta.id_rol
        WHERE p.id_solicitud = ? AND p.id_postulacion = ?
          AND u.estado_verificacion = 'VERIFICADO'
          AND cuenta.estado = 'ACTIVO' AND rol.nombre = 'UNIVERSITARIO'
    ''', (solicitud_id, post_id))
    return _one(cursor)


def aceptar_postulacion(cursor, solicitud_id, post_id):
    cursor.execute('''
        UPDATE dbo.Postulaciones SET estado = 'ACEPTADA'
        WHERE id_postulacion = ? AND id_solicitud = ? AND estado = 'PENDIENTE'
    ''', (post_id, solicitud_id))
    if cursor.rowcount != 1:
        return False
    cursor.execute('''
        UPDATE dbo.Postulaciones SET estado = 'RECHAZADA'
        WHERE id_solicitud = ? AND id_postulacion <> ? AND estado = 'PENDIENTE'
    ''', (solicitud_id, post_id))
    cursor.execute("UPDATE dbo.Solicitudes SET estado = 'ASIGNADA' WHERE id_solicitud = ?", (solicitud_id,))
    return True


def cancelar_solicitud(cursor, solicitud_id):
    cursor.execute("UPDATE dbo.Solicitudes SET estado = 'CANCELADA' WHERE id_solicitud = ?", (solicitud_id,))
    cursor.execute('''
        UPDATE dbo.Postulaciones SET estado = 'RECHAZADA'
        WHERE id_solicitud = ? AND estado IN ('PENDIENTE', 'ACEPTADA')
    ''', (solicitud_id,))


def adulto_activo(cursor, adult_id):
    cursor.execute('''
        SELECT TOP (1) a.id_usuario AS id
        FROM dbo.PerfilAdultoMayor a
        INNER JOIN dbo.Usuarios u ON u.id_usuario = a.id_usuario
        INNER JOIN dbo.Roles r ON r.id_rol = u.id_rol
        WHERE a.id_usuario = ? AND u.estado = 'ACTIVO' AND r.nombre = 'ADULTO_MAYOR'
    ''', (adult_id,))
    return _one(cursor)
