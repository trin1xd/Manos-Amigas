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
        SELECT s.id_solicitud, sv.nombre, s.estado,
            a.nombre_completo, u.nombre_completo
        FROM public."Solicitudes" s
        JOIN public."Postulaciones" p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN public."Servicios" sv ON sv.id_servicio=s.id_servicio
        JOIN public."Usuarios" a ON a.id_usuario=s.id_adulto_mayor AND a.estado='ACTIVO'
        JOIN public."Usuarios" u ON u.id_usuario=p.id_universitario AND u.estado='ACTIVO'
        WHERE s.estado IN ('ASIGNADA', 'EN_CURSO', 'FINALIZADA')
          AND (s.id_adulto_mayor=%s OR p.id_universitario=%s OR EXISTS (
              SELECT 1 FROM public."FamiliarAdultoMayor" f
              WHERE f.id_adulto_mayor=s.id_adulto_mayor
                AND f.id_familiar=%s AND f.activo=TRUE))
        ORDER BY s.id_solicitud DESC LIMIT 70
    ''', (id_usuario, id_usuario, id_usuario))
    return [{'id': row[0], 'servicio': row[1], 'estado': row[2],
             'adulto': row[3], 'universitario': row[4]}
            for row in cursor.fetchall()]


def contexto(cursor, solicitud_id, bloquear=False):
    locking = 'FOR UPDATE OF s' if bloquear else ''
    cursor.execute(f'''
        SELECT s.id_adulto_mayor, p.id_universitario, s.estado
        FROM public."Solicitudes" s
        JOIN public."Postulaciones" p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN public."Usuarios" a ON a.id_usuario=s.id_adulto_mayor AND a.estado='ACTIVO'
        JOIN public."Usuarios" u ON u.id_usuario=p.id_universitario AND u.estado='ACTIVO'
        WHERE s.id_solicitud = %s AND s.estado IN ('ASIGNADA','EN_CURSO','FINALIZADA')
        {locking}
    ''', (solicitud_id,))
    row = cursor.fetchone()
    return None if row is None else {'id_adulto': row[0], 'id_universitario': row[1], 'estado': row[2]}


def listar_mensajes(cursor, solicitud_id):
    cursor.execute('''
        SELECT id_mensaje, id_remitente, nombre_completo, mensaje, fecha_utc FROM (
            SELECT m.id_mensaje, m.id_remitente, u.nombre_completo,
                   m.mensaje, m.fecha_utc
            FROM public."MensajesServicio" m
            JOIN public."Usuarios" u ON u.id_usuario=m.id_remitente
            WHERE m.id_solicitud=%s ORDER BY m.id_mensaje DESC LIMIT 80
        ) ultimos ORDER BY id_mensaje ASC
    ''', (solicitud_id,))
    return _messages(cursor.fetchall())


def limite_rapidez(cursor, solicitud_id, remitente_id):
    cursor.execute('''
        SELECT 1 FROM public."MensajesServicio"
        WHERE id_solicitud=%s AND id_remitente=%s
          AND fecha_utc > (CURRENT_TIMESTAMP AT TIME ZONE 'UTC') - INTERVAL '3 seconds'
        ORDER BY id_mensaje DESC LIMIT 1
    ''', (solicitud_id, remitente_id))
    return cursor.fetchone() is not None


def guardar(cursor, solicitud_id, remitente_id, mensaje):
    cursor.execute('''
        INSERT INTO public."MensajesServicio"(id_solicitud,id_remitente,mensaje)
        VALUES (%s,%s,%s) RETURNING id_mensaje
    ''', (solicitud_id, remitente_id, mensaje))
    return int(cursor.fetchone()[0])
