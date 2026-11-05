"""SQL Server: seguimiento de servicios y auditoría, consultas parametrizadas."""
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
        FROM dbo.Postulaciones p
        INNER JOIN dbo.Solicitudes s ON s.id_solicitud = p.id_solicitud
        INNER JOIN dbo.Servicios sv ON sv.id_servicio = s.id_servicio
        LEFT JOIN dbo.SeguimientoServicios seg ON seg.id_solicitud = s.id_solicitud
        WHERE p.id_universitario = ? AND p.estado = 'ACEPTADA'
        ORDER BY s.fecha_solicitada DESC, s.id_solicitud DESC
    ''', (id_usuario,))
    return _all(cursor)


def listar_para_adulto(cursor, id_usuario):
    cursor.execute('''
        SELECT s.id_solicitud AS id, sv.nombre AS servicio, s.fecha_solicitada,
               s.estado, es.nombre_completo AS estudiante_nombre,
               seg.fecha_llegada_utc, seg.fecha_inicio_utc,
               seg.fecha_termino_utc, seg.fecha_confirmacion_utc
        FROM dbo.Solicitudes s
        INNER JOIN dbo.Servicios sv ON sv.id_servicio = s.id_servicio
        LEFT JOIN dbo.Postulaciones p ON p.id_solicitud = s.id_solicitud AND p.estado = 'ACEPTADA'
        LEFT JOIN dbo.Usuarios es ON es.id_usuario = p.id_universitario
        LEFT JOIN dbo.SeguimientoServicios seg ON seg.id_solicitud = s.id_solicitud
        WHERE s.id_adulto_mayor = ?
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
        FROM dbo.Solicitudes s
        INNER JOIN dbo.FamiliarAdultoMayor v ON v.id_adulto_mayor = s.id_adulto_mayor
            AND v.id_familiar = ? AND v.activo = 1
        INNER JOIN dbo.Usuarios ad ON ad.id_usuario = s.id_adulto_mayor AND ad.estado = 'ACTIVO'
        INNER JOIN dbo.Servicios sv ON sv.id_servicio = s.id_servicio
        LEFT JOIN dbo.Postulaciones p ON p.id_solicitud = s.id_solicitud AND p.estado = 'ACEPTADA'
        LEFT JOIN dbo.Usuarios es ON es.id_usuario = p.id_universitario
        LEFT JOIN dbo.SeguimientoServicios seg ON seg.id_solicitud = s.id_solicitud
        ORDER BY s.fecha_solicitada DESC, s.id_solicitud DESC
    ''', (id_usuario,))
    return _all(cursor)


def bloquear_solicitud(cursor, id_solicitud):
    """Bloquea una solicitud durante la transición (dos clicks no compiten)."""
    cursor.execute('''
        SELECT s.id_solicitud, s.id_adulto_mayor, s.estado, p.id_universitario
        FROM dbo.Solicitudes s WITH (UPDLOCK, HOLDLOCK)
        LEFT JOIN dbo.Postulaciones p ON p.id_solicitud = s.id_solicitud
            AND p.estado = 'ACEPTADA'
        WHERE s.id_solicitud = ?
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
        FROM dbo.SeguimientoServicios WHERE id_solicitud = ?
    ''', (id_solicitud,))
    row = cursor.fetchone()
    return None if row is None else {
        'llegada': row[0], 'inicio': row[1],
        'termino': row[2], 'confirmacion': row[3],
    }


def registrar_accion(cursor, id_solicitud, actor_id, accion):
    if accion == 'LLEGADA':
        cursor.execute('''
            INSERT INTO dbo.SeguimientoServicios(id_solicitud, fecha_llegada_utc)
            VALUES (?, SYSUTCDATETIME())
        ''', (id_solicitud,))
    elif accion == 'INICIO':
        cursor.execute('''
            UPDATE dbo.SeguimientoServicios SET fecha_inicio_utc = SYSUTCDATETIME()
            WHERE id_solicitud = ? AND fecha_llegada_utc IS NOT NULL AND fecha_inicio_utc IS NULL
        ''', (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('No se pudo registrar el inicio del servicio.')
        cursor.execute("UPDATE dbo.Solicitudes SET estado = 'EN_CURSO' WHERE id_solicitud = ? AND estado = 'ASIGNADA'", (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('La solicitud cambió de estado inesperadamente.')
    elif accion == 'TERMINO':
        cursor.execute('''
            UPDATE dbo.SeguimientoServicios SET fecha_termino_utc = SYSUTCDATETIME()
            WHERE id_solicitud = ? AND fecha_inicio_utc IS NOT NULL AND fecha_termino_utc IS NULL
        ''', (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('No se pudo registrar el término.')
    elif accion == 'CONFIRMAR':
        cursor.execute('''
            UPDATE dbo.SeguimientoServicios
            SET fecha_confirmacion_utc = SYSUTCDATETIME(), id_confirmador = ?
            WHERE id_solicitud = ? AND fecha_termino_utc IS NOT NULL
              AND fecha_confirmacion_utc IS NULL
        ''', (actor_id, id_solicitud))
        if cursor.rowcount != 1:
            raise RuntimeError('No se pudo confirmar el servicio.')
        cursor.execute("UPDATE dbo.Solicitudes SET estado = 'FINALIZADA' WHERE id_solicitud = ? AND estado = 'EN_CURSO'", (id_solicitud,))
        if cursor.rowcount != 1:
            raise RuntimeError('La solicitud cambió de estado inesperadamente.')
    cursor.execute('''
        INSERT INTO dbo.HistorialSeguimiento(id_solicitud, id_actor, accion)
        VALUES (?, ?, ?)
    ''', (id_solicitud, actor_id, accion))
