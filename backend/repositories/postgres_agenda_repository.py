"""Consultas PostgreSQL para la agenda de Manos Amigas (módulo aislado)."""
from datetime import date, datetime, time


def _all(cursor):
    columns = [item[0] for item in cursor.description]
    output = []
    for row in cursor.fetchall():
        item = dict(zip(columns, row))
        for field, value in list(item.items()):
            if isinstance(value, datetime):
                item[field] = value.isoformat(timespec="minutes")
            elif isinstance(value, (date, time)):
                item[field] = value.isoformat()
        output.append(item)
    return output


def listar(cursor, rol, id_usuario):
    # Las expresiones son constantes controladas por el backend, nunca del usuario.
    filters = {
        "UNIVERSITARIO": "p.id_universitario = %s",
        "ADULTO_MAYOR": "s.id_adulto_mayor = %s",
        "FAMILIAR": """
            EXISTS (
                SELECT 1
                FROM public."FamiliarAdultoMayor" f
                JOIN public."Usuarios" adulto
                  ON adulto.id_usuario = f.id_adulto_mayor
                WHERE f.id_adulto_mayor = s.id_adulto_mayor
                  AND f.id_familiar = %s
                  AND f.activo = TRUE AND adulto.estado = 'ACTIVO'
            )
        """,
    }
    if rol not in filters:
        raise ValueError("Rol no admitido para consultar la agenda.")
    cursor.execute(f"""
        SELECT s.id_solicitud AS id, sv.nombre AS servicio,
               s.fecha_solicitada, s.duracion_horas, s.estado
        FROM public."Solicitudes" s
        JOIN public."Servicios" sv ON sv.id_servicio = s.id_servicio
        JOIN public."Postulaciones" p
          ON p.id_solicitud = s.id_solicitud AND p.estado = 'ACEPTADA'
        WHERE s.estado IN ('ASIGNADA', 'EN_CURSO', 'FINALIZADA')
          AND s.fecha_solicitada >= (CURRENT_TIMESTAMP - INTERVAL '90 days')
          AND {filters[rol]}
        ORDER BY
          CASE WHEN s.estado IN ('ASIGNADA', 'EN_CURSO') THEN 0 ELSE 1 END,
          ABS(EXTRACT(EPOCH FROM (s.fecha_solicitada - CURRENT_TIMESTAMP))),
          s.id_solicitud
        LIMIT 100
    """, (id_usuario,))
    return _all(cursor)


def conflicto_de_aceptacion(cursor, id_solicitud, id_postulacion):
    """Bloquea la fila del estudiante dentro de la transacción del llamador.

    SERIALIZAR aceptaciones de un estudiante requiere que TODAS las rutas de
    aceptación utilicen este mismo bloqueo antes de comprobar el solapamiento.
    """
    cursor.execute("""
        SELECT u.id_usuario
        FROM public."Postulaciones" p
        JOIN public."Usuarios" u ON u.id_usuario = p.id_universitario
        WHERE p.id_solicitud = %s AND p.id_postulacion = %s
        FOR UPDATE OF u
    """, (id_solicitud, id_postulacion))
    row = cursor.fetchone()
    if row is None:
        return {"no_disponible": True}
    student_id = int(row[0])
    cursor.execute("""
        SELECT otra.id_solicitud
        FROM public."Solicitudes" nueva
        JOIN public."Solicitudes" otra
          ON otra.id_solicitud <> nueva.id_solicitud
        JOIN public."Postulaciones" p ON p.id_solicitud = otra.id_solicitud
        WHERE nueva.id_solicitud = %s
          AND p.id_universitario = %s
          AND p.estado = 'ACEPTADA'
          AND otra.estado IN ('ASIGNADA', 'EN_CURSO')
          AND otra.fecha_solicitada <
              nueva.fecha_solicitada +
              (COALESCE(nueva.duracion_horas, 3) * INTERVAL '1 hour')
          AND otra.fecha_solicitada +
              (COALESCE(otra.duracion_horas, 3) * INTERVAL '1 hour')
              > nueva.fecha_solicitada
        LIMIT 1
    """, (id_solicitud, student_id))
    conflict = cursor.fetchone()
    return {"id": int(conflict[0])} if conflict else None
