"""Tokens de recuperación: solo SHA-256 en PostgreSQL (módulo aislado), nunca texto sin hash."""


def usuario_activo(cursor, email):
    cursor.execute('''
        SELECT id_usuario, email FROM public."Usuarios" 
        WHERE email=%s AND estado='ACTIVO'
        FOR UPDATE
    ''', (email,))
    row = cursor.fetchone()
    return None if row is None else {'id': row[0], 'email': row[1]}


def reciente(cursor, uid):
    cursor.execute('''
        SELECT 1 FROM public."RecuperacionContrasena"
        WHERE id_usuario=%s AND creado_utc > ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC') - INTERVAL '5 minutes')
        ORDER BY creado_utc DESC LIMIT 1
    ''', (uid,))
    return cursor.fetchone() is not None


def crear(cursor, uid, token_hash):
    # La anterior queda invalidada: un único enlace válido por cuenta.
    cursor.execute('''
        UPDATE public."RecuperacionContrasena" SET usado_utc=(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        WHERE id_usuario=%s AND usado_utc IS NULL
    ''', (uid,))
    cursor.execute('''
        INSERT INTO public."RecuperacionContrasena"(id_usuario, token_hash, vence_utc)
        VALUES (%s, %s, ((CURRENT_TIMESTAMP AT TIME ZONE 'UTC') + INTERVAL '20 minutes'))
    ''', (uid, token_hash))


def invalidar(cursor, token_hash):
    cursor.execute('''
        UPDATE public."RecuperacionContrasena" SET usado_utc=(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        WHERE token_hash=%s AND usado_utc IS NULL
    ''', (token_hash,))


def validar_y_bloquear(cursor, token_hash):
    cursor.execute('''
        SELECT r.id_usuario
        FROM public."RecuperacionContrasena" r 
        JOIN public."Usuarios" u ON u.id_usuario=r.id_usuario AND u.estado='ACTIVO'
        WHERE r.token_hash=%s AND r.usado_utc IS NULL
          AND r.vence_utc > (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        LIMIT 1
        FOR UPDATE OF r
    ''', (token_hash,))
    row = cursor.fetchone()
    return None if row is None else row[0]


def actualizar_clave(cursor, uid, password_hash):
    cursor.execute("UPDATE public.\"Usuarios\" SET password_hash=%s, password_version=password_version+1 WHERE id_usuario=%s AND estado='ACTIVO'",
                   (password_hash, uid))
    if cursor.rowcount != 1:
        raise RuntimeError('No se pudo actualizar la contraseña.')
    cursor.execute('''
        UPDATE public."RecuperacionContrasena" SET usado_utc=(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
        WHERE id_usuario=%s AND usado_utc IS NULL
    ''', (uid,))
