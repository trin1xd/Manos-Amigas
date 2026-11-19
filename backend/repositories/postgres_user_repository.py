"""Repositorio PostgreSQL para autenticación (fase de migración).

Replica la interfaz de user_repository.py sin tocar la versión SQL Server.
Las tablas usan nombres entre comillas para conservar mayúsculas.
Todos los valores se pasan como parámetros (nunca concatenar datos de usuario).
"""


def _fetch_user(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    names = [col[0] for col in cursor.description]
    return dict(zip(names, row))


def get_role_id(cursor, role_name):
    cursor.execute('SELECT id_rol FROM public."Roles" WHERE nombre = %s', (role_name,))
    row = cursor.fetchone()
    return row[0] if row else None


def rut_exists(cursor, rut):
    cursor.execute('SELECT 1 FROM public."Usuarios" WHERE rut = %s', (rut,))
    return cursor.fetchone() is not None


def email_exists(cursor, email):
    cursor.execute('SELECT 1 FROM public."Usuarios" WHERE email = %s', (email,))
    return cursor.fetchone() is not None


def institutional_email_exists(cursor, email):
    cursor.execute(
        'SELECT 1 FROM public."PerfilUniversitario" WHERE correo_institucional = %s',
        (email,),
    )
    return cursor.fetchone() is not None


def insert_user(cursor, *, nombre_completo, rut, email, telefono,
                fecha_nacimiento, password_hash, id_rol):
    cursor.execute(
        """
        INSERT INTO public."Usuarios"
            (nombre_completo, rut, email, telefono, fecha_nacimiento,
             password_hash, id_rol)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id_usuario
        """,
        (nombre_completo, rut, email, telefono, fecha_nacimiento,
         password_hash, id_rol),
    )
    return cursor.fetchone()[0]


def insert_adulto_mayor_profile(cursor, id_usuario, *,
                                direccion, contacto_confianza_nombre,
                                contacto_confianza_telefono, indicaciones_acceso):
    cursor.execute(
        """
        INSERT INTO public."PerfilAdultoMayor"
            (id_usuario, direccion, contacto_confianza_nombre,
             contacto_confianza_telefono, indicaciones_acceso)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (id_usuario, direccion, contacto_confianza_nombre,
         contacto_confianza_telefono, indicaciones_acceso),
    )


def insert_universitario_profile(cursor, id_usuario, *,
                                 universidad, carrera, anio_cursa,
                                 correo_institucional, contacto_emergencia_nombre,
                                 contacto_emergencia_telefono):
    cursor.execute(
        """
        INSERT INTO public."PerfilUniversitario"
            (id_usuario, universidad, carrera, anio_cursa,
             correo_institucional, contacto_emergencia_nombre,
             contacto_emergencia_telefono)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (id_usuario, universidad, carrera, anio_cursa,
         correo_institucional, contacto_emergencia_nombre,
         contacto_emergencia_telefono),
    )


def insert_familiar_profile(cursor, id_usuario, *, parentesco, telefono_alternativo):
    cursor.execute(
        """
        INSERT INTO public."PerfilFamiliar"
            (id_usuario, parentesco, telefono_alternativo)
        VALUES (%s, %s, %s)
        """,
        (id_usuario, parentesco, telefono_alternativo),
    )


_USER_FIELDS = """
    SELECT u.id_usuario, u.nombre_completo, u.email, u.password_hash,
           u.estado, u.password_version, r.nombre AS rol, pu.estado_verificacion
    FROM public."Usuarios" u
    JOIN public."Roles" r ON r.id_rol = u.id_rol
    LEFT JOIN public."PerfilUniversitario" pu ON pu.id_usuario = u.id_usuario
"""


def find_user_by_email(cursor, email):
    cursor.execute(_USER_FIELDS + ' WHERE u.email = %s', (email,))
    return _fetch_user(cursor)


def find_user_by_id(cursor, user_id):
    cursor.execute(_USER_FIELDS + ' WHERE u.id_usuario = %s', (user_id,))
    return _fetch_user(cursor)
