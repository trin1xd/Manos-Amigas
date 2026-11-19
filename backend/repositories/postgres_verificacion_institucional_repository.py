"""Consultas parametrizadas: control del correo institucional; sin archivos."""

def perfil(cur, user_id, lock=False):
    locking = 'FOR UPDATE OF p' if lock else ''
    cur.execute(f'''
        SELECT p.correo_institucional, p.correo_institucional_verificado,
               p.estado_verificacion
        FROM public."PerfilUniversitario" p
        JOIN public."Usuarios" u ON u.id_usuario=p.id_usuario
        JOIN public."Roles" r ON r.id_rol=u.id_rol
        WHERE p.id_usuario=%s AND u.estado='ACTIVO' AND r.nombre='UNIVERSITARIO'
        {locking}
    ''', (user_id,))
    row = cur.fetchone()
    return {'correo': row[0], 'verificado': bool(row[1]), 'estado': row[2]} if row else None


def codigo(cur, user_id, lock=False):
    locking = 'FOR UPDATE' if lock else ''
    cur.execute(f'''SELECT codigo_hash, vence_utc, intentos, ultimo_envio_utc,
                   dia_envios_utc, envios_dia
                   FROM public."CodigosCorreoInstitucional" WHERE id_universitario=%s {locking}''', (user_id,))
    row = cur.fetchone()
    return dict(zip(('hash', 'vence', 'intentos', 'ultimo', 'dia', 'envios'), row)) if row else None


def emitir_codigo(cur, user_id, digest, expira, hoy, conteo):
    cur.execute('''UPDATE public."CodigosCorreoInstitucional"
        SET codigo_hash=%s, vence_utc=%s, intentos=0, ultimo_envio_utc=(CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
            dia_envios_utc=%s, envios_dia=%s
        WHERE id_universitario=%s''', (digest, expira, hoy, conteo, user_id))
    if cur.rowcount == 0:
        cur.execute('''INSERT INTO public."CodigosCorreoInstitucional"
            (id_universitario,codigo_hash,vence_utc,ultimo_envio_utc,dia_envios_utc,envios_dia)
            VALUES(%s,%s,%s,(CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),%s,%s)''', (user_id, digest, expira, hoy, conteo))


def invalidar_codigo(cur, user_id, digest):
    cur.execute('''UPDATE public."CodigosCorreoInstitucional"
        SET codigo_hash=NULL,vence_utc=NULL WHERE id_universitario=%s AND codigo_hash=%s''', (user_id, digest))


def fallo_codigo(cur, user_id):
    cur.execute('''UPDATE public."CodigosCorreoInstitucional" SET intentos=intentos+1
        WHERE id_universitario=%s AND intentos<5''', (user_id,))


def confirmar_correo(cur, user_id):
    cur.execute('''UPDATE public."PerfilUniversitario" SET correo_institucional_verificado=TRUE
        WHERE id_usuario=%s AND estado_verificacion='PENDIENTE_VERIFICACION' ''', (user_id,))
    if cur.rowcount != 1:
        return False
    cur.execute('''UPDATE public."CodigosCorreoInstitucional"
        SET codigo_hash=NULL,vence_utc=NULL,fecha_confirmacion_utc=(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        WHERE id_universitario=%s''', (user_id,))
    return True


def correo_confirmado(cur, user_id):
    # Un administrador revisa el perfil bloqueado dentro de la misma transaccion.
    cur.execute('''SELECT correo_institucional_verificado
        FROM public."PerfilUniversitario" WITH (UPDLOCK, HOLDLOCK)
        WHERE id_usuario = %s''', (user_id,))
    fila = cur.fetchone()
    return bool(fila and fila[0])


def auditar(cur, user_id, actor_id, evento):
    cur.execute('''INSERT INTO public."AuditoriaVerificacionInstitucional"
        (id_universitario,id_actor,evento) VALUES(%s,%s,%s)''', (user_id, actor_id, evento))
