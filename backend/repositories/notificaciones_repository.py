"""Avisos privados en SQL Server. Todas las consultas parametrizadas y por usuario.

Los emisores reciben el cursor de la misma transacción que cambia el estado del servicio.
Nunca se incluyen teléfono, dirección, RUT o datos privados en títulos/detalles.
"""
from datetime import datetime


def _lista(cursor):
    cols = [x[0] for x in cursor.description]
    resultado = []
    for fila in cursor.fetchall():
        item = dict(zip(cols, fila))
        for k, v in list(item.items()):
            if isinstance(v, datetime):
                item[k] = v.isoformat(timespec='seconds') + 'Z'
        resultado.append(item)
    return resultado


def listar(cursor, id_usuario):
    cursor.execute('''
        SELECT TOP (100) n.id_notificacion AS id, n.id_solicitud, n.tipo,
            n.titulo, n.detalle, n.creada_utc, n.leida_utc
        FROM dbo.Notificaciones AS n
        WHERE n.id_usuario = ?
        ORDER BY n.creada_utc DESC, n.id_notificacion DESC
    ''', (id_usuario,))
    return _lista(cursor)


def marcar_leida(cursor, id_usuario, id_notificacion):
    cursor.execute('''
        UPDATE dbo.Notificaciones SET leida_utc = SYSUTCDATETIME()
        WHERE id_notificacion = ? AND id_usuario = ? AND leida_utc IS NULL
    ''', (id_notificacion, id_usuario))
    return cursor.rowcount == 1


def marcar_todas(cursor, id_usuario):
    cursor.execute('''
        UPDATE dbo.Notificaciones SET leida_utc = SYSUTCDATETIME()
        WHERE id_usuario = ? AND leida_utc IS NULL
    ''', (id_usuario,))
    return cursor.rowcount


def _texto(id_solicitud, evento):
    titulos = {
        'POSTULACION': 'Nueva postulación',
        'ASIGNACION': 'Universitario asignado',
        'RECHAZO': 'Postulación no seleccionada',
        'CANCELACION': 'Solicitud cancelada',
        'LLEGADA': 'Universitario informó su llegada',
        'INICIO': 'Servicio iniciado',
        'TERMINO': 'Estudiante informó el término',
        'CONFIRMACION': 'Servicio confirmado',
    }
    return titulos[evento], f'Actualización de la solicitud #{id_solicitud}. Revisa su estado en Manos Amigas.'


def avisar_adulto_y_familia(cursor, id_solicitud, evento, id_actor):
    titulo, detalle = _texto(id_solicitud, evento)
    cursor.execute('''
        INSERT INTO dbo.Notificaciones(id_usuario, id_solicitud, tipo, titulo, detalle)
        SELECT objetivo.id_usuario, ?, ?, ?, ?
        FROM (
            SELECT s.id_adulto_mayor AS id_usuario
            FROM dbo.Solicitudes s WHERE s.id_solicitud = ?
            UNION
            SELECT v.id_familiar
            FROM dbo.Solicitudes s
            JOIN dbo.FamiliarAdultoMayor v ON v.id_adulto_mayor = s.id_adulto_mayor
                AND v.activo = 1
            WHERE s.id_solicitud = ?
        ) objetivo
        JOIN dbo.Usuarios u ON u.id_usuario = objetivo.id_usuario AND u.estado = 'ACTIVO'
        WHERE objetivo.id_usuario <> ?
    ''', (id_solicitud, evento, titulo, detalle, id_solicitud, id_solicitud, id_actor))


def avisar_postulante(cursor, id_solicitud, id_postulacion, evento, id_actor):
    titulo, detalle = _texto(id_solicitud, evento)
    cursor.execute('''
        INSERT INTO dbo.Notificaciones(id_usuario, id_solicitud, tipo, titulo, detalle)
        SELECT p.id_universitario, ?, ?, ?, ?
        FROM dbo.Postulaciones p
        JOIN dbo.Usuarios u ON u.id_usuario = p.id_universitario AND u.estado = 'ACTIVO'
        WHERE p.id_solicitud = ? AND p.id_postulacion = ?
          AND p.id_universitario <> ?
    ''', (id_solicitud, evento, titulo, detalle, id_solicitud, id_postulacion, id_actor))


def avisar_postulantes_no_seleccionados(cursor, id_solicitud, id_postulacion, id_actor):
    titulo, detalle = _texto(id_solicitud, 'RECHAZO')
    cursor.execute('''
        INSERT INTO dbo.Notificaciones(id_usuario, id_solicitud, tipo, titulo, detalle)
        SELECT p.id_universitario, ?, N'RECHAZO', ?, ?
        FROM dbo.Postulaciones p
        JOIN dbo.Usuarios u ON u.id_usuario = p.id_universitario AND u.estado = 'ACTIVO'
        WHERE p.id_solicitud = ? AND p.id_postulacion <> ? AND p.estado = 'RECHAZADA'
          AND p.id_universitario <> ?
    ''', (id_solicitud, titulo, detalle, id_solicitud, id_postulacion, id_actor))


def avisar_cancelacion(cursor, id_solicitud, id_actor):
    titulo, detalle = _texto(id_solicitud, 'CANCELACION')
    cursor.execute('''
        INSERT INTO dbo.Notificaciones(id_usuario, id_solicitud, tipo, titulo, detalle)
        SELECT DISTINCT p.id_universitario, ?, N'CANCELACION', ?, ?
        FROM dbo.Postulaciones p
        JOIN dbo.Usuarios u ON u.id_usuario = p.id_universitario AND u.estado = 'ACTIVO'
        WHERE p.id_solicitud = ? AND p.id_universitario <> ?
    ''', (id_solicitud, titulo, detalle, id_solicitud, id_actor))


def avisar_seguimiento(cursor, id_solicitud, accion, id_actor):
    if accion == 'CONFIRMAR':
        titulo, detalle = _texto(id_solicitud, 'CONFIRMACION')
        cursor.execute('''
            INSERT INTO dbo.Notificaciones(id_usuario, id_solicitud, tipo, titulo, detalle)
            SELECT p.id_universitario, ?, N'CONFIRMACION', ?, ?
            FROM dbo.Postulaciones p
            JOIN dbo.Usuarios u ON u.id_usuario = p.id_universitario AND u.estado = 'ACTIVO'
            WHERE p.id_solicitud = ? AND p.estado = 'ACEPTADA'
              AND p.id_universitario <> ?
        ''', (id_solicitud, titulo, detalle, id_solicitud, id_actor))
    else:
        avisar_adulto_y_familia(cursor, id_solicitud, accion, id_actor)
