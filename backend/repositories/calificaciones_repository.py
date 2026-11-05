"""Persistencia parametrizada de calificaciones, sin datos privados."""
from datetime import datetime


def listar(cursor, usuario):
    """Solo trabajos finalizados del universitario, adulto o familiar con vínculo vigente."""
    rol = usuario['rol']
    if rol == 'UNIVERSITARIO':
        filtro = "p.id_universitario = ?"
        params = (usuario['id'],)
    elif rol == 'ADULTO_MAYOR':
        filtro = "s.id_adulto_mayor = ?"
        params = (usuario['id'],)
    elif rol == 'FAMILIAR':
        filtro = """EXISTS (SELECT 1 FROM dbo.FamiliarAdultoMayor v
            JOIN dbo.Usuarios a ON a.id_usuario = v.id_adulto_mayor AND a.estado='ACTIVO'
            WHERE v.id_adulto_mayor=s.id_adulto_mayor AND v.id_familiar=? AND v.activo=1)"""
        params = (usuario['id'],)
    else:
        return []

    # 'filtro' solo contiene literales definidos en este módulo, no texto del usuario.
    cursor.execute(f'''
        SELECT TOP (100) s.id_solicitud AS id, sv.nombre AS servicio,
               s.fecha_solicitada, seg.fecha_confirmacion_utc,
               a.nombre_completo AS adulto_nombre,
               u.nombre_completo AS universitario_nombre,
               ca.puntaje AS nota_adulto, ca.comentario AS comentario_adulto,
               cu.puntaje AS nota_universitario, cu.comentario AS comentario_universitario
        FROM dbo.Solicitudes s
        JOIN dbo.Servicios sv ON sv.id_servicio=s.id_servicio
        JOIN dbo.Postulaciones p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN dbo.SeguimientoServicios seg ON seg.id_solicitud=s.id_solicitud
            AND seg.fecha_confirmacion_utc IS NOT NULL
        JOIN dbo.Usuarios a ON a.id_usuario=s.id_adulto_mayor
        JOIN dbo.Usuarios u ON u.id_usuario=p.id_universitario
        LEFT JOIN dbo.Calificaciones ca ON ca.id_solicitud=s.id_solicitud
            AND ca.tipo='ADULTO_A_UNIVERSITARIO'
        LEFT JOIN dbo.Calificaciones cu ON cu.id_solicitud=s.id_solicitud
            AND cu.tipo='UNIVERSITARIO_A_ADULTO'
        WHERE s.estado='FINALIZADA' AND {filtro}
        ORDER BY seg.fecha_confirmacion_utc DESC, s.id_solicitud DESC
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
        FROM dbo.Solicitudes s WITH (UPDLOCK, HOLDLOCK)
        JOIN dbo.Postulaciones p ON p.id_solicitud=s.id_solicitud AND p.estado='ACEPTADA'
        JOIN dbo.SeguimientoServicios seg ON seg.id_solicitud=s.id_solicitud
            AND seg.fecha_confirmacion_utc IS NOT NULL
        WHERE s.id_solicitud=? AND s.estado='FINALIZADA'
    ''', (id_solicitud,))
    row = cursor.fetchone()
    return None if row is None else {'id_adulto': row[0], 'id_universitario': row[1]}


def existe(cursor, id_solicitud, tipo):
    cursor.execute('''SELECT TOP (1) id_calificacion FROM dbo.Calificaciones WITH (UPDLOCK, HOLDLOCK)
                      WHERE id_solicitud=? AND tipo=?''', (id_solicitud, tipo))
    return cursor.fetchone() is not None


def registrar(cursor, id_solicitud, id_evaluador, id_evaluado, tipo, puntaje, comentario):
    cursor.execute('''
        INSERT INTO dbo.Calificaciones
          (id_solicitud, id_evaluador, id_evaluado, tipo, puntaje, comentario)
        OUTPUT INSERTED.id_calificacion
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (id_solicitud, id_evaluador, id_evaluado, tipo, puntaje, comentario))
    return cursor.fetchone()[0]
