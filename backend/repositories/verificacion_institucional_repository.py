"""Consultas parametrizadas: control del correo institucional; sin archivos."""

def perfil(cur, user_id, lock=False):
    hint = 'WITH (UPDLOCK, HOLDLOCK)' if lock else ''
    cur.execute(f'''
        SELECT p.correo_institucional, p.correo_institucional_verificado,
               p.estado_verificacion
        FROM dbo.PerfilUniversitario p {hint}
        JOIN dbo.Usuarios u ON u.id_usuario=p.id_usuario
        JOIN dbo.Roles r ON r.id_rol=u.id_rol
        WHERE p.id_usuario=? AND u.estado='ACTIVO' AND r.nombre='UNIVERSITARIO'
    ''', (user_id,))
    row = cur.fetchone()
    return {'correo': row[0], 'verificado': bool(row[1]), 'estado': row[2]} if row else None


def codigo(cur, user_id, lock=False):
    hint = 'WITH (UPDLOCK,HOLDLOCK)' if lock else ''
    cur.execute(f'''SELECT codigo_hash, vence_utc, intentos, ultimo_envio_utc,
                   dia_envios_utc, envios_dia
                   FROM dbo.CodigosCorreoInstitucional {hint} WHERE id_universitario=?''', (user_id,))
    row = cur.fetchone()
    return dict(zip(('hash', 'vence', 'intentos', 'ultimo', 'dia', 'envios'), row)) if row else None


def emitir_codigo(cur, user_id, digest, expira, hoy, conteo):
    cur.execute('''UPDATE dbo.CodigosCorreoInstitucional
        SET codigo_hash=?, vence_utc=?, intentos=0, ultimo_envio_utc=SYSUTCDATETIME(),
            dia_envios_utc=?, envios_dia=?
        WHERE id_universitario=?''', (digest, expira, hoy, conteo, user_id))
    if cur.rowcount == 0:
        cur.execute('''INSERT INTO dbo.CodigosCorreoInstitucional
            (id_universitario,codigo_hash,vence_utc,ultimo_envio_utc,dia_envios_utc,envios_dia)
            VALUES(?,?,?,SYSUTCDATETIME(),?,?)''', (user_id, digest, expira, hoy, conteo))


def invalidar_codigo(cur, user_id, digest):
    cur.execute('''UPDATE dbo.CodigosCorreoInstitucional
        SET codigo_hash=NULL,vence_utc=NULL WHERE id_universitario=? AND codigo_hash=?''', (user_id, digest))


def fallo_codigo(cur, user_id):
    cur.execute('''UPDATE dbo.CodigosCorreoInstitucional SET intentos=intentos+1
        WHERE id_universitario=? AND intentos<5''', (user_id,))


def confirmar_correo(cur, user_id):
    cur.execute('''UPDATE dbo.PerfilUniversitario SET correo_institucional_verificado=1
        WHERE id_usuario=? AND estado_verificacion='PENDIENTE_VERIFICACION' ''', (user_id,))
    if cur.rowcount != 1:
        return False
    cur.execute('''UPDATE dbo.CodigosCorreoInstitucional
        SET codigo_hash=NULL,vence_utc=NULL,fecha_confirmacion_utc=SYSUTCDATETIME()
        WHERE id_universitario=?''', (user_id,))
    return True


def correo_confirmado(cur, user_id):
    # Un administrador revisa el perfil bloqueado dentro de la misma transaccion.
    cur.execute('''SELECT correo_institucional_verificado
        FROM dbo.PerfilUniversitario WITH (UPDLOCK, HOLDLOCK)
        WHERE id_usuario = ?''', (user_id,))
    fila = cur.fetchone()
    return bool(fila and fila[0])


def auditar(cur, user_id, actor_id, evento):
    cur.execute('''INSERT INTO dbo.AuditoriaVerificacionInstitucional
        (id_universitario,id_actor,evento) VALUES(?,?,?)''', (user_id, actor_id, evento))
