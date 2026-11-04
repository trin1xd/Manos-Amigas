"""Acceso SQL parametrizado para revisión administrativa de universitarios."""


def _dict_rows(cursor):
    columnas = [col[0] for col in cursor.description]
    return [dict(zip(columnas, row)) for row in cursor.fetchall()]


def listar_universitarios(cursor):
    # Solo datos necesarios para decidir; nunca RUT, teléfonos, hashes o documentos.
    cursor.execute('''
        SELECT u.id_usuario AS id, u.nombre_completo AS nombre,
               u.email, p.universidad, p.carrera, p.anio_cursa,
               p.correo_institucional, p.correo_institucional_verificado,
               p.estado_verificacion, u.fecha_creacion
        FROM dbo.PerfilUniversitario AS p
        INNER JOIN dbo.Usuarios AS u ON u.id_usuario = p.id_usuario
        INNER JOIN dbo.Roles AS r ON r.id_rol = u.id_rol
        WHERE u.estado = 'ACTIVO' AND r.nombre = 'UNIVERSITARIO'
        ORDER BY CASE WHEN p.estado_verificacion = 'PENDIENTE_VERIFICACION' THEN 0 ELSE 1 END,
                 u.fecha_creacion DESC, u.id_usuario DESC
    ''')
    resultado = _dict_rows(cursor)
    for alumno in resultado:
        alumno['fecha_creacion'] = alumno['fecha_creacion'].isoformat() if alumno['fecha_creacion'] else None
        alumno['correo_institucional_verificado'] = bool(alumno['correo_institucional_verificado'])
    return resultado


def bloquear_universitario(cursor, id_universitario):
    cursor.execute('''
        SELECT p.estado_verificacion, u.id_usuario
        FROM dbo.PerfilUniversitario AS p WITH (UPDLOCK, HOLDLOCK)
        INNER JOIN dbo.Usuarios AS u ON u.id_usuario = p.id_usuario
        INNER JOIN dbo.Roles AS r ON r.id_rol = u.id_rol
        WHERE p.id_usuario = ? AND r.nombre = 'UNIVERSITARIO' AND u.estado = 'ACTIVO'
    ''', (id_universitario,))
    fila = cursor.fetchone()
    return {'estado': fila[0], 'id': fila[1]} if fila else None


def aplicar_decision(cursor, id_universitario, id_admin, anterior, nuevo, observacion):
    cursor.execute('''
        UPDATE dbo.PerfilUniversitario
        SET estado_verificacion = ?
        WHERE id_usuario = ? AND estado_verificacion = ?
    ''', (nuevo, id_universitario, anterior))
    if cursor.rowcount != 1:
        return False
    cursor.execute('''
        INSERT INTO dbo.AuditoriaVerificaciones
           (id_universitario, id_administrador, estado_anterior, estado_nuevo, observacion)
        VALUES (?, ?, ?, ?, ?)
    ''', (id_universitario, id_admin, anterior, nuevo, observacion))
    return True
