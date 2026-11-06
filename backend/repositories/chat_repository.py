"""SQL parametrizado para conversaciones ligadas a un servicio asignado."""
from datetime import datetime


def _messages(rows):
    resultado = []
    for mid, uid, nombre, texto, fecha in rows:
        resultado.append({'id': int(mid), 'id_remitente': uid,
                          'remitente': nombre, 'mensaje': texto,
                          'fecha_utc': fecha.isoformat(timespec='milliseconds') + 'Z'
                          if isinstance(fecha, datetime) else str(fecha)})
    return resultado


def conversaciones(cursor, id_usuario):
    cursor.execute('''
        SELECT TOP (70) s.id_solicitud, sv.nombre, s.estado,
            a.nombre_completo, u.nombre_completo
        FROM dbo.Solicitudes s
        JOIN dbo.Postulaciones p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN dbo.Servicios sv ON sv.id_servicio=s.id_servicio
        JOIN dbo.Usuarios a ON a.id_usuario=s.id_adulto_mayor AND a.estado='ACTIVO'
        JOIN dbo.Usuarios u ON u.id_usuario=p.id_universitario AND u.estado='ACTIVO'
        WHERE s.estado IN ('ASIGNADA', 'EN_CURSO', 'FINALIZADA')
          AND (s.id_adulto_mayor=? OR p.id_universitario=? OR EXISTS (
              SELECT 1 FROM dbo.FamiliarAdultoMayor f
              WHERE f.id_adulto_mayor=s.id_adulto_mayor
                AND f.id_familiar=? AND f.activo=1))
        ORDER BY s.id_solicitud DESC
    ''', (id_usuario, id_usuario, id_usuario))
    return [{'id': row[0], 'servicio': row[1], 'estado': row[2],
             'adulto': row[3], 'universitario': row[4]}
            for row in cursor.fetchall()]


def contexto(cursor, solicitud_id, bloquear=False):
    hint = 'WITH (UPDLOCK, HOLDLOCK)' if bloquear else ''
    cursor.execute(f'''
        SELECT s.id_adulto_mayor, p.id_universitario, s.estado
        FROM dbo.Solicitudes s {hint}
        JOIN dbo.Postulaciones p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN dbo.Usuarios a ON a.id_usuario=s.id_adulto_mayor AND a.estado='ACTIVO'
        JOIN dbo.Usuarios u ON u.id_usuario=p.id_universitario AND u.estado='ACTIVO'
        WHERE s.id_solicitud = ? AND s.estado IN ('ASIGNADA','EN_CURSO','FINALIZADA')
    ''', (solicitud_id,))
    row = cursor.fetchone()
    return None if row is None else {'id_adulto': row[0], 'id_universitario': row[1], 'estado': row[2]}


def listar_mensajes(cursor, solicitud_id):
    cursor.execute('''
        SELECT id_mensaje, id_remitente, nombre_completo, mensaje, fecha_utc FROM (
            SELECT TOP (80) m.id_mensaje, m.id_remitente, u.nombre_completo,
                   m.mensaje, m.fecha_utc
            FROM dbo.MensajesServicio m
            JOIN dbo.Usuarios u ON u.id_usuario=m.id_remitente
            WHERE m.id_solicitud=? ORDER BY m.id_mensaje DESC
        ) ultimos ORDER BY id_mensaje ASC
    ''', (solicitud_id,))
    return _messages(cursor.fetchall())


def limite_rapidez(cursor, solicitud_id, remitente_id):
    cursor.execute('''
        SELECT TOP (1) 1 FROM dbo.MensajesServicio
        WHERE id_solicitud=? AND id_remitente=?
          AND fecha_utc > DATEADD(SECOND, -3, SYSUTCDATETIME())
        ORDER BY id_mensaje DESC
    ''', (solicitud_id, remitente_id))
    return cursor.fetchone() is not None


def guardar(cursor, solicitud_id, remitente_id, mensaje):
    cursor.execute('''
        INSERT INTO dbo.MensajesServicio(id_solicitud,id_remitente,mensaje)
        OUTPUT INSERTED.id_mensaje
        VALUES (?,?,?)
    ''', (solicitud_id, remitente_id, mensaje))
    return int(cursor.fetchone()[0])
