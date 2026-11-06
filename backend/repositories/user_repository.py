"""Consultas a SQL Server para usuarios y perfiles.

Todas las funciones reciben un `cursor` abierto por la capa de servicios (que
controla commit/rollback) y usan consultas parametrizadas (`?`).
"""


def get_role_id(cursor, role_name):
    cursor.execute("SELECT id_rol FROM Roles WHERE nombre = ?", (role_name,))
    row = cursor.fetchone()
    return row[0] if row else None


def rut_exists(cursor, rut):
    cursor.execute("SELECT 1 FROM Usuarios WHERE rut = ?", (rut,))
    return cursor.fetchone() is not None


def email_exists(cursor, email):
    cursor.execute("SELECT 1 FROM Usuarios WHERE email = ?", (email,))
    return cursor.fetchone() is not None


def institutional_email_exists(cursor, email):
    cursor.execute(
        "SELECT 1 FROM PerfilUniversitario WHERE correo_institucional = ?", (email,)
    )
    return cursor.fetchone() is not None


def insert_user(cursor, *, nombre_completo, rut, email, telefono,
                fecha_nacimiento, password_hash, id_rol):
    """Inserta en Usuarios y devuelve el id_usuario generado."""
    cursor.execute(
        """
        INSERT INTO Usuarios
            (nombre_completo, rut, email, telefono, fecha_nacimiento, password_hash, id_rol)
        OUTPUT INSERTED.id_usuario
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (nombre_completo, rut, email, telefono, fecha_nacimiento, password_hash, id_rol),
    )
    return cursor.fetchone()[0]


def insert_adulto_mayor_profile(cursor, id_usuario, *, direccion, contacto_confianza_nombre,
                                contacto_confianza_telefono, indicaciones_acceso):
    cursor.execute(
        """
        INSERT INTO PerfilAdultoMayor
            (id_usuario, direccion, contacto_confianza_nombre,
             contacto_confianza_telefono, indicaciones_acceso)
        VALUES (?, ?, ?, ?, ?)
        """,
        (id_usuario, direccion, contacto_confianza_nombre,
         contacto_confianza_telefono, indicaciones_acceso),
    )


def insert_universitario_profile(cursor, id_usuario, *, universidad, carrera, anio_cursa,
                                 correo_institucional, contacto_emergencia_nombre,
                                 contacto_emergencia_telefono):
    # estado_verificacion y correo_institucional_verificado usan los valores por defecto
    # de la tabla (PENDIENTE_VERIFICACION y 0).
    cursor.execute(
        """
        INSERT INTO PerfilUniversitario
            (id_usuario, universidad, carrera, anio_cursa, correo_institucional,
             contacto_emergencia_nombre, contacto_emergencia_telefono)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (id_usuario, universidad, carrera, anio_cursa, correo_institucional,
         contacto_emergencia_nombre, contacto_emergencia_telefono),
    )


def insert_familiar_profile(cursor, id_usuario, *, parentesco, telefono_alternativo):
    cursor.execute(
        """
        INSERT INTO PerfilFamiliar (id_usuario, parentesco, telefono_alternativo)
        VALUES (?, ?, ?)
        """,
        (id_usuario, parentesco, telefono_alternativo),
    )


def find_user_by_email(cursor, email):
    """Devuelve un dict con los datos de login (incluye password_hash) o None.

    El hash solo se usa dentro del servicio; nunca se envia en una respuesta.
    """
    cursor.execute(
        """
        SELECT u.id_usuario, u.nombre_completo, u.email, u.password_hash, u.estado, u.password_version,
               r.nombre AS rol, pu.estado_verificacion
        FROM Usuarios u
        JOIN Roles r ON r.id_rol = u.id_rol
        LEFT JOIN PerfilUniversitario pu ON pu.id_usuario = u.id_usuario
        WHERE u.email = ?
        """,
        (email,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {
        "id_usuario": row.id_usuario,
        "nombre_completo": row.nombre_completo,
        "email": row.email,
        "password_hash": row.password_hash,
        "password_version": row.password_version,
        "estado": row.estado,
        "rol": row.rol,
        "estado_verificacion": row.estado_verificacion,
    }



def find_user_by_id(cursor, user_id):
    """Devuelve un dict con los datos del usuario por ID o None.

    Usa los mismos JOINs que find_user_by_email para obtener rol y perfil.
    """
    cursor.execute(
        """
        SELECT u.id_usuario, u.nombre_completo, u.email, u.password_hash, u.estado, u.password_version,
               r.nombre AS rol, pu.estado_verificacion
        FROM Usuarios u
        JOIN Roles r ON r.id_rol = u.id_rol
        LEFT JOIN PerfilUniversitario pu ON pu.id_usuario = u.id_usuario
        WHERE u.id_usuario = ?
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return {
        "id_usuario": row.id_usuario,
        "nombre_completo": row.nombre_completo,
        "email": row.email,
        "password_hash": row.password_hash,
        "password_version": row.password_version,
        "estado": row.estado,
        "rol": row.rol,
        "estado_verificacion": row.estado_verificacion,
    }
