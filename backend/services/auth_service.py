"""Reglas de negocio de registro e inicio de sesión."""
import pyodbc
from werkzeug.security import check_password_hash, generate_password_hash

from database.connection import get_connection
from repositories import user_repository as repo
from utils import validators as v
from utils.rut import normalize_rut

ADULTO_MAYOR = "ADULTO_MAYOR"
UNIVERSITARIO = "UNIVERSITARIO"
FAMILIAR = "FAMILIAR"

# Campos por tipo de perfil: (nombre, tipo, obligatorio, largo máximo)
COMMON_FIELDS = [
    ("nombre_completo", "text", True, 150),
    ("rut", "rut", True, 20),
    ("telefono", "phone", True, 20),
    ("email", "email", True, 255),
    ("password", "password", True, 128),
]

FIELDS_BY_ROLE = {
    ADULTO_MAYOR: COMMON_FIELDS + [
        ("fecha_nacimiento", "birth", True, 10),
        ("direccion", "text", True, 255),
        ("contacto_confianza_nombre", "text", True, 150),
        ("contacto_confianza_telefono", "phone", True, 20),
        ("indicaciones_acceso", "text", False, 500),
    ],
    UNIVERSITARIO: COMMON_FIELDS + [
        ("fecha_nacimiento", "birth", True, 10),
        ("universidad", "text", True, 150),
        ("carrera", "text", True, 150),
        ("anio_cursa", "year", True, 2),
        ("correo_institucional", "email", True, 255),
        ("contacto_emergencia_nombre", "text", True, 150),
        ("contacto_emergencia_telefono", "phone", True, 20),
    ],
    FAMILIAR: COMMON_FIELDS + [
        ("parentesco", "text", True, 100),
        ("telefono_alternativo", "phone", False, 20),
    ],
}


class ServiceError(Exception):
    """Error de negocio con código HTTP sugerido y detalle por campo."""

    def __init__(self, message, status=400, errors=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.errors = errors or {}


def _validate(data, role):
    """Valida y normaliza los campos. Devuelve el dict limpio o lanza ServiceError."""
    clean, errors = {}, {}

    for name, kind, required, max_len in FIELDS_BY_ROLE[role]:
        raw = data.get(name)
        # La contraseña no se recorta: los espacios pueden ser parte de ella.
        value = raw if (kind == "password" and isinstance(raw, str)) else v.clean_text(raw)

        if value == "":
            if required:
                errors[name] = "Campo obligatorio."
            else:
                clean[name] = None
            continue
        if len(str(value)) > max_len:
            errors[name] = f"Máximo {max_len} caracteres."
            continue

        if kind == "email":
            value = v.normalize_email(value)
            error = v.check_email(value)
        elif kind == "phone":
            error = v.check_phone(value)
        elif kind == "rut":
            error = v.check_rut(value)
            value = normalize_rut(value) or value
        elif kind == "password":
            error = v.check_password(value)
        elif kind == "birth":
            value = v.parse_birth_date(value)
            error = None if value else "La fecha de nacimiento no es válida (use AAAA-MM-DD)."
        elif kind == "year":
            value = v.parse_study_year(value)
            error = None if value else "El año que cursa debe ser un número entre 1 y 10."
        else:
            error = None

        if error:
            errors[name] = error
        else:
            clean[name] = value

    if (role == UNIVERSITARIO and "correo_institucional" in clean
            and clean["correo_institucional"] == clean.get("email")):
        errors["correo_institucional"] = "Debe ser distinto del correo personal."

    if errors:
        raise ServiceError("Hay errores en los datos enviados.", 400, errors)
    return clean


def _insert_profile(cursor, role, id_usuario, d):
    if role == ADULTO_MAYOR:
        repo.insert_adulto_mayor_profile(
            cursor, id_usuario,
            direccion=d["direccion"],
            contacto_confianza_nombre=d["contacto_confianza_nombre"],
            contacto_confianza_telefono=d["contacto_confianza_telefono"],
            indicaciones_acceso=d["indicaciones_acceso"],
        )
    elif role == UNIVERSITARIO:
        repo.insert_universitario_profile(
            cursor, id_usuario,
            universidad=d["universidad"],
            carrera=d["carrera"],
            anio_cursa=d["anio_cursa"],
            correo_institucional=d["correo_institucional"],
            contacto_emergencia_nombre=d["contacto_emergencia_nombre"],
            contacto_emergencia_telefono=d["contacto_emergencia_telefono"],
        )
    else:
        repo.insert_familiar_profile(
            cursor, id_usuario,
            parentesco=d["parentesco"],
            telefono_alternativo=d["telefono_alternativo"],
        )


def register_user(role, data):
    """Registra Usuario + perfil específico en UNA transacción."""
    d = _validate(data, role)
    password_hash = generate_password_hash(d["password"])

    conn = get_connection()
    try:
        cursor = conn.cursor()

        duplicates = {}
        if repo.rut_exists(cursor, d["rut"]):
            duplicates["rut"] = "Ya existe una cuenta con este RUT."
        if repo.email_exists(cursor, d["email"]):
            duplicates["email"] = "Ya existe una cuenta con este correo."
        if role == UNIVERSITARIO and repo.institutional_email_exists(
                cursor, d["correo_institucional"]):
            duplicates["correo_institucional"] = "Este correo institucional ya está registrado."
        if duplicates:
            raise ServiceError("Los datos ya están registrados.", 409, duplicates)

        id_rol = repo.get_role_id(cursor, role)
        if id_rol is None:
            raise ServiceError(
                "Rol no configurado. Ejecute database/04_datos_iniciales.sql.", 500)

        id_usuario = repo.insert_user(
            cursor,
            nombre_completo=d["nombre_completo"],
            rut=d["rut"],
            email=d["email"],
            telefono=d["telefono"],
            fecha_nacimiento=d.get("fecha_nacimiento"),
            password_hash=password_hash,
            id_rol=id_rol,
        )
        _insert_profile(cursor, role, id_usuario, d)
        conn.commit()
    except ServiceError:
        conn.rollback()
        raise
    except pyodbc.IntegrityError:
        # Respaldo ante duplicados simultáneos (las restricciones UNIQUE de SQL Server).
        conn.rollback()
        raise ServiceError("El RUT o el correo ya están registrados.", 409)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    user = {"id": id_usuario, "nombre": d["nombre_completo"], "rol": role}
    if role == UNIVERSITARIO:
        user["estado_verificacion"] = "PENDIENTE_VERIFICACION"
    return user


def login(email, password):
    """Verifica credenciales y devuelve los datos mínimos del usuario."""
    email = v.normalize_email(email)
    if not email or not isinstance(password, str) or not password:
        raise ServiceError("Correo y contraseña son obligatorios.", 400)

    conn = get_connection()
    try:
        found = repo.find_user_by_email(conn.cursor(), email)
    finally:
        conn.close()

    # Mismo mensaje para correo inexistente o contraseña errada (no revelar cuál falló).
    if found is None or not check_password_hash(found["password_hash"], password):
        raise ServiceError("Correo o contraseña incorrectos.", 401)

    if found["estado"] != "ACTIVO":
        raise ServiceError("La cuenta no está activa.", 403)

    user = {
        "id": found["id_usuario"],
        "nombre": found["nombre_completo"],
        "rol": found["rol"],
        "estado": found["estado"],
    }
    if found["rol"] == UNIVERSITARIO:
        user["estado_verificacion"] = found["estado_verificacion"]
    return user



def get_user_by_id(user_id):
    """Obtiene los datos del usuario por ID y valida que su cuenta esté ACTIVA."""
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise ServiceError("Identificador de usuario inválido.", 401)

    conn = get_connection()
    try:
        found = repo.find_user_by_id(conn.cursor(), user_id)
    finally:
        conn.close()

    if found is None:
        raise ServiceError("Usuario no encontrado.", 401)

    if found["estado"] != "ACTIVO":
        raise ServiceError("La cuenta no está activa.", 403)

    user = {
        "id": found["id_usuario"],
        "nombre": found["nombre_completo"],
        "rol": found["rol"],
        "estado": found["estado"],
    }
    if found["rol"] == UNIVERSITARIO:
        user["estado_verificacion"] = found["estado_verificacion"]
    return user
