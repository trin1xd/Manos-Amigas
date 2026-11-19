"""Persistencia parametrizada de calificaciones, sin datos privados."""
from datetime import datetime


def listar(cursor, usuario):
    """Solo trabajos finalizados del universitario, adulto o familiar con vínculo vigente."""
    rol = usuario['rol']
    if rol == 'UNIVERSITARIO':
        filtro = "p.id_universitario = %s"
        params = (usuario['id'],)
    elif rol == 'ADULTO_MAYOR':
        filtro = "s.id_adulto_mayor = %s"
        params = (usuario['id'],)
    elif rol == 'FAMILIAR':
        filtro = """EXISTS (SELECT 1 FROM public."FamiliarAdultoMayor" v
            JOIN public."Usuarios" a ON a.id_usuario = v.id_adulto_mayor AND a.estado='ACTIVO'
            WHERE v.id_adulto_mayor=s.id_adulto_mayor AND v.id_familiar=%s AND v.activo=TRUE)"""
        params = (usuario['id'],)
    else:
        return []

    # 'filtro' solo contiene literales definidos en este módulo, no texto del usuario.
    cursor.execute(f'''
        SELECT s.id_solicitud AS id, sv.nombre AS servicio,
               s.fecha_solicitada, seg.fecha_confirmacion_utc,
               a.nombre_completo AS adulto_nombre,
               u.nombre_completo AS universitario_nombre,
               ca.puntaje AS nota_adulto, ca.comentario AS comentario_adulto,
               cu.puntaje AS nota_universitario, cu.comentario AS comentario_universitario
        FROM public."Solicitudes" s
        JOIN public."Servicios" sv ON sv.id_servicio=s.id_servicio
        JOIN public."Postulaciones" p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN public."SeguimientoServicios" seg ON seg.id_solicitud=s.id_solicitud
            AND seg.fecha_confirmacion_utc IS NOT NULL
        JOIN public."Usuarios" a ON a.id_usuario=s.id_adulto_mayor
        JOIN public."Usuarios" u ON u.id_usuario=p.id_universitario
        LEFT JOIN public."Calificaciones" ca ON ca.id_solicitud=s.id_solicitud
            AND ca.tipo='ADULTO_A_UNIVERSITARIO'
        LEFT JOIN public."Calificaciones" cu ON cu.id_solicitud=s.id_solicitud
            AND cu.tipo='UNIVERSITARIO_A_ADULTO'
        WHERE s.estado='FINALIZADA' AND {filtro}
        ORDER BY seg.fecha_confirmacion_utc DESC, s.id_solicitud DESC LIMIT 100
    ''', params)
    keys = [col[0] for col in cursor.description]
    resultado = []
    for row in cursor.fetchall():
        d = dict(zip(keys, row))
        if isinstance(d['fecha_solicitada'], datetime):
            d['fecha_solicitada'] = d['fecha_solicitada'].isoformat(timespec='minutes')
        if isinstance(d['fecha_confirmacion_utc'], datetime):
            d['fecha_confirmacion_utc'] = d['fecha_confirmacion_utc'].isoformat(timespec='seconds') + 'Z'
        soy_uni = rol == 'UNIVERSITARIO'
        dada = ('nota_universitario', 'comentario_universitario') if soy_uni else ('nota_adulto', 'comentario_adulto')
        recibida = ('nota_adulto', 'comentario_adulto') if soy_uni else ('nota_universitario', 'comentario_universitario')
        resultado.append({
            'id': d['id'], 'servicio': d['servicio'],
            'fecha_solicitada': d['fecha_solicitada'],
            'fecha_confirmacion_utc': d['fecha_confirmacion_utc'],
            'persona_evaluada': d['adulto_nombre'] if soy_uni else d['universitario_nombre'],
            'mi_calificacion': None if d[dada[0]] is None else
                {'puntaje': d[dada[0]], 'comentario': d[dada[1]]},
            'calificacion_recibida': None if d[recibida[0]] is None else
                {'puntaje': d[recibida[0]], 'comentario': d[recibida[1]]},
        })
    return resultado


def solicitud_finalizada(cursor, id_solicitud):
    cursor.execute('''
        SELECT s.id_adulto_mayor, p.id_universitario
        FROM public."Solicitudes" s 
        JOIN public."Postulaciones" p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN public."SeguimientoServicios" seg ON seg.id_solicitud=s.id_solicitud
            AND seg.fecha_confirmacion_utc IS NOT NULL
        WHERE s.id_solicitud=%s AND s.estado='FINALIZADA'
        FOR UPDATE OF s
    ''', (id_solicitud,))
    row = cursor.fetchone()
    return None if row is None else {'id_adulto': row[0], 'id_universitario': row[1]}


def existe(cursor, id_solicitud, tipo):
    cursor.execute('''SELECT id_calificacion FROM public."Calificaciones" 
                      WHERE id_solicitud=%s AND tipo=%s''', (id_solicitud, tipo))
    return cursor.fetchone() is not None


def registrar(cursor, id_solicitud, id_evaluador, id_evaluado, tipo, puntaje, comentario):
    cursor.execute('''
        INSERT INTO public."Calificaciones"
          (id_solicitud, id_evaluador, id_evaluado, tipo, puntaje, comentario)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_calificacion
    ''', (id_solicitud, id_evaluador, id_evaluado, tipo, puntaje, comentario))
    return cursor.fetchone()[0]
