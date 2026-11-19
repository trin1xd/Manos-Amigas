"""Persistencia de franjas semanales; se modifica solo el usuario del JWT."""

def listar(cursor, id_universitario):
    cursor.execute('''
        SELECT dia_semana, TO_CHAR(hora_inicio, 'HH24:MI') AS hora_inicio,
               TO_CHAR(hora_fin, 'HH24:MI') AS hora_fin
        FROM public."DisponibilidadUniversitario"
        WHERE id_universitario = %s ORDER BY dia_semana, hora_inicio
    ''', (id_universitario,))
    return [dict(zip((c[0] for c in cursor.description), row)) for row in cursor.fetchall()]


def reemplazar(cursor, id_universitario, franjas):
    # Bloqueo por cuenta para impedir dos reemplazos concurrentes del mismo estudiante.
    cursor.execute('SELECT id_usuario FROM public."Usuarios"  WHERE id_usuario = %s FOR UPDATE', (id_universitario,))
    if cursor.fetchone() is None:
        raise RuntimeError('Cuenta de estudiante inexistente.')
    cursor.execute('DELETE FROM public."DisponibilidadUniversitario" WHERE id_universitario = %s', (id_universitario,))
    for franja in franjas:
        cursor.execute('''
            INSERT INTO public."DisponibilidadUniversitario"
                (id_universitario, dia_semana, hora_inicio, hora_fin)
            VALUES (%s, %s, %s, %s)
        ''', (id_universitario, franja['dia_semana'], franja['hora_inicio'], franja['hora_fin']))
