"""Consultas parametrizadas: control del correo institucional; sin archivos."""

def perfil(cur, user_id, lock=False):
    locking = 'FOR UPDATE OF p' if lock else ''
    cur.execute(f'''
        SELECT p.correo_institucional, p.correo_institucional_verificado,
               p.estado_verificacion, u.email AS correo_cuenta
        FROM public."PerfilUniversitario" p
        JOIN public."Usuarios" u ON u.id_usuario=p.id_usuario
        JOIN public."Roles" r ON r.id_rol=u.id_rol
        WHERE p.id_usuario=%s AND u.estado='ACTIVO' AND r.nombre='UNIVERSITARIO'
        {locking}
    ''', (user_id,))
    row = cur.fetchone()
    return {'correo': row[0], 'verificado': bool(row[1]),
            'estado': row[2], 'correo_cuenta': row[3]} if row else None


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
    # Solo si sigue vigente ESTE código: reembolsar el envío que nunca fue
    # aceptado por el proveedor. Un envío posterior no debe perder su cupo.
    # El último intento conserva su fecha para exigir 90 s entre solicitudes.
    cur.execute('''UPDATE public."CodigosCorreoInstitucional"
        SET codigo_hash=NULL,vence_utc=NULL,
            envios_dia=GREATEST(envios_dia-1,0)
        WHERE id_universitario=%s AND codigo_hash=%s''', (user_id, digest))


def recuperar_un_intento_fallido_anterior(cur, user_id, hoy):
    """Recuperación acotada para errores anteriores a la corrección.

    Solo cuentas pendientes de feria con código ya invalidado por un error
    anterior. Bajo bloqueo de fila se devuelve un único cupo antes de
    reemplazarlo por la nueva solicitud. No altera cuentas aprobadas.
    """
    cur.execute('''UPDATE public."CodigosCorreoInstitucional"
        SET envios_dia=envios_dia-1
        WHERE id_universitario=%s AND dia_envios_utc=%s
          AND codigo_hash IS NULL AND vence_utc IS NULL
          AND envios_dia=5''', (user_id, hoy))
    return cur.rowcount == 1


def fallo_codigo(cur, user_id):
    cur.execute('''UPDATE public."CodigosCorreoInstitucional" SET intentos=intentos+1
        WHERE id_universitario=%s AND intentos<5''', (user_id,))


def confirmar_correo(cur, user_id, habilitar=False):
    # La aprobación por correo solo se aplica si el servicio ya validó
    # un código vigente, de un solo uso y del usuario autenticado.
    estado = 'VERIFICADO' if habilitar else 'PENDIENTE_VERIFICACION'
    cur.execute('''UPDATE public."PerfilUniversitario"
        SET correo_institucional_verificado=TRUE, estado_verificacion=%s
        WHERE id_usuario=%s AND estado_verificacion='PENDIENTE_VERIFICACION'
          AND correo_institucional_verificado=FALSE''', (estado, user_id))
    if cur.rowcount != 1:
        return False
    cur.execute('''UPDATE public."CodigosCorreoInstitucional"
        SET codigo_hash=NULL,vence_utc=NULL,fecha_confirmacion_utc=(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        WHERE id_universitario=%s''', (user_id,))
    return True


def correo_confirmado(cur, user_id):
    # Un administrador revisa el perfil bloqueado dentro de la misma transaccion.
    cur.execute('''SELECT correo_institucional_verificado
        FROM public."PerfilUniversitario"
        WHERE id_usuario = %s FOR UPDATE''', (user_id,))
    fila = cur.fetchone()
    return bool(fila and fila[0])


def auditar(cur, user_id, actor_id, evento):
    cur.execute('''INSERT INTO public."AuditoriaVerificacionInstitucional"
        (id_universitario,id_actor,evento) VALUES(%s,%s,%s)''', (user_id, actor_id, evento))
