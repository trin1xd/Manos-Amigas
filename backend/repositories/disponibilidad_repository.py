"""Persistencia de franjas semanales; se modifica solo el usuario del JWT."""

def listar(cursor, id_universitario):
    cursor.execute('''
        SELECT dia_semana, CONVERT(VARCHAR(5), hora_inicio, 108) AS hora_inicio,
               CONVERT(VARCHAR(5), hora_fin, 108) AS hora_fin
        FROM dbo.DisponibilidadUniversitario
        WHERE id_universitario = ? ORDER BY dia_semana, hora_inicio
    ''', (id_universitario,))
    return [dict(zip((c[0] for c in cursor.description), row)) for row in cursor.fetchall()]


def reemplazar(cursor, id_universitario, franjas):
    # Bloqueo por cuenta para impedir dos reemplazos concurrentes del mismo estudiante.
    cursor.execute('SELECT id_usuario FROM dbo.Usuarios WITH (UPDLOCK, HOLDLOCK) WHERE id_usuario = ?', (id_universitario,))
    if cursor.fetchone() is None:
        raise RuntimeError('Cuenta de estudiante inexistente.')
    cursor.execute('DELETE FROM dbo.DisponibilidadUniversitario WHERE id_universitario = ?', (id_universitario,))
    for franja in franjas:
        cursor.execute('''
            INSERT INTO dbo.DisponibilidadUniversitario
                (id_universitario, dia_semana, hora_inicio, hora_fin)
            VALUES (?, ?, ?, ?)
        ''', (id_universitario, franja['dia_semana'], franja['hora_inicio'], franja['hora_fin']))
