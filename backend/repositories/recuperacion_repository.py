"""Tokens de recuperación: solo SHA-256 en SQL Server, nunca texto sin hash."""


def usuario_activo(cursor, email):
    cursor.execute('''
        SELECT id_usuario, email FROM dbo.Usuarios WITH (UPDLOCK, HOLDLOCK)
        WHERE email=? AND estado='ACTIVO'
    ''', (email,))
    row = cursor.fetchone()
    return None if row is None else {'id': row[0], 'email': row[1]}


def reciente(cursor, uid):
    cursor.execute('''
        SELECT TOP (1) 1 FROM dbo.RecuperacionContrasena
        WHERE id_usuario=? AND creado_utc > DATEADD(MINUTE, -5, SYSUTCDATETIME())
        ORDER BY creado_utc DESC
    ''', (uid,))
    return cursor.fetchone() is not None


def crear(cursor, uid, token_hash):
    # La anterior queda invalidada: un único enlace válido por cuenta.
    cursor.execute('''
        UPDATE dbo.RecuperacionContrasena SET usado_utc=SYSUTCDATETIME()
        WHERE id_usuario=? AND usado_utc IS NULL
    ''', (uid,))
    cursor.execute('''
        INSERT INTO dbo.RecuperacionContrasena(id_usuario, token_hash, vence_utc)
        VALUES (?, ?, DATEADD(MINUTE, 20, SYSUTCDATETIME()))
    ''', (uid, token_hash))


def invalidar(cursor, token_hash):
    cursor.execute('''
        UPDATE dbo.RecuperacionContrasena SET usado_utc=SYSUTCDATETIME()
        WHERE token_hash=? AND usado_utc IS NULL
    ''', (token_hash,))


def validar_y_bloquear(cursor, token_hash):
    cursor.execute('''
        SELECT TOP (1) r.id_usuario
        FROM dbo.RecuperacionContrasena r WITH (UPDLOCK, HOLDLOCK)
        JOIN dbo.Usuarios u ON u.id_usuario=r.id_usuario AND u.estado='ACTIVO'
        WHERE r.token_hash=? AND r.usado_utc IS NULL
          AND r.vence_utc > SYSUTCDATETIME()
    ''', (token_hash,))
    row = cursor.fetchone()
    return None if row is None else row[0]


def actualizar_clave(cursor, uid, password_hash):
    cursor.execute('UPDATE dbo.Usuarios SET password_hash=?, password_version=password_version+1 WHERE id_usuario=? AND estado=\'ACTIVO\'',
                   (password_hash, uid))
    if cursor.rowcount != 1:
        raise RuntimeError('No se pudo actualizar la contraseña.')
    cursor.execute('''
        UPDATE dbo.RecuperacionContrasena SET usado_utc=SYSUTCDATETIME()
        WHERE id_usuario=? AND usado_utc IS NULL
    ''', (uid,))
