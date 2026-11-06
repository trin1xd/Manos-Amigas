"""Consultas SQL Server para la agenda de compromisos y cruce de asignaciones.

Todas las consultas son parametrizadas. No devuelve nombres, teléfonos, RUT ni
ubicaciones de adultos mayores; los destinatarios se derivan del JWT.
"""
from datetime import date, datetime, time


def _all(cursor):
    columnas = [item[0] for item in cursor.description]
    registros = []
    for fila in cursor.fetchall():
        item = dict(zip(columnas, fila))
        for campo, valor in item.items():
            if isinstance(valor, datetime):
                item[campo] = valor.isoformat(timespec='minutes')
            elif isinstance(valor, (date, time)):
                item[campo] = valor.isoformat()
        registros.append(item)
    return registros


def listar(cursor, rol, id_usuario):
    """Compromisos asignados, en curso o finalizados recientemente, con permisos SQL."""
    filtros = {
        'UNIVERSITARIO': 'p.id_universitario = ?',
        'ADULTO_MAYOR': 's.id_adulto_mayor = ?',
        'FAMILIAR': '''EXISTS (
            SELECT 1 FROM dbo.FamiliarAdultoMayor AS f
            INNER JOIN dbo.Usuarios AS adulto ON adulto.id_usuario = f.id_adulto_mayor
            WHERE f.id_adulto_mayor = s.id_adulto_mayor
              AND f.id_familiar = ? AND f.activo = 1 AND adulto.estado = 'ACTIVO'
        )''',
    }
    if rol not in filtros:
        raise ValueError('Rol no admitido para consultar la agenda.')
    # Se muestran servicios con postulación aceptada; un servicio cancelado
    # deja de estar en la agenda y sus avisos permanecen en Notificaciones.
    cursor.execute(f'''
        SELECT TOP (100)
            s.id_solicitud AS id,
            sv.nombre AS servicio,
            s.fecha_solicitada,
            s.duracion_horas,
            s.estado
        FROM dbo.Solicitudes AS s
        INNER JOIN dbo.Servicios AS sv ON sv.id_servicio = s.id_servicio
        INNER JOIN dbo.Postulaciones AS p
            ON p.id_solicitud = s.id_solicitud AND p.estado = 'ACEPTADA'
        WHERE s.estado IN ('ASIGNADA', 'EN_CURSO', 'FINALIZADA')
          AND s.fecha_solicitada >= DATEADD(DAY, -90, SYSDATETIME())
          AND {filtros[rol]}
        ORDER BY
          CASE WHEN s.estado IN ('ASIGNADA', 'EN_CURSO') THEN 0 ELSE 1 END,
          ABS(DATEDIFF(MINUTE, SYSDATETIME(), s.fecha_solicitada)),
          s.id_solicitud
    ''', (id_usuario,))
    return _all(cursor)


def conflicto_de_aceptacion(cursor, id_solicitud, id_postulacion):
    """Serializa por estudiante antes de verificar reservas aceptadas solapadas.

    Debe ejecutarse en la MISMA transacción de la aceptación. El UPDLOCK de
    Usuarios serializa aceptaciones simultáneas de solicitudes diferentes
    para el mismo universitario. [inicio, fin): franjas contiguas se permiten.
    """
    cursor.execute('''
        SELECT TOP (1) u.id_usuario
        FROM dbo.Postulaciones AS p
        INNER JOIN dbo.Usuarios AS u WITH (UPDLOCK, HOLDLOCK)
            ON u.id_usuario = p.id_universitario
        WHERE p.id_solicitud = ? AND p.id_postulacion = ?
    ''', (id_solicitud, id_postulacion))
    fila = cursor.fetchone()
    if fila is None:
        # Fail-closed si la postulación desapareció entre lecturas.
        return {'no_disponible': True}
    id_estudiante = int(fila[0])
    cursor.execute('''
        SELECT TOP (1) otra.id_solicitud
        FROM dbo.Solicitudes AS nueva
        INNER JOIN dbo.Solicitudes AS otra
          ON otra.id_solicitud <> nueva.id_solicitud
        INNER JOIN dbo.Postulaciones AS p
          ON p.id_solicitud = otra.id_solicitud
        WHERE nueva.id_solicitud = ?
          AND p.id_universitario = ?
          AND p.estado = 'ACEPTADA'
          AND otra.estado IN ('ASIGNADA', 'EN_CURSO')
          AND otra.fecha_solicitada < DATEADD(HOUR, COALESCE(nueva.duracion_horas, 3), nueva.fecha_solicitada)
          AND DATEADD(HOUR, COALESCE(otra.duracion_horas, 3), otra.fecha_solicitada) > nueva.fecha_solicitada
    ''', (id_solicitud, id_estudiante))
    otro = cursor.fetchone()
    return {'id': int(otro[0])} if otro else None
