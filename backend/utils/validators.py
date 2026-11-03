"""Validaciones reutilizables. Cada funcion devuelve un mensaje de error o None."""
from __future__ import annotations
import re
from datetime import date, datetime

from utils.rut import is_valid_rut

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def clean_text(value) -> str:
    """Convierte a texto y quita espacios sobrantes. None -> ''."""
    if value is None:
        return ""
    return str(value).strip()


def normalize_email(value) -> str:
    return clean_text(value).lower()


def check_email(value) -> str | None:
    if len(value) > 255 or not EMAIL_RE.match(value):
        return "El correo electrónico no es válido."
    return None


def check_phone(value) -> str | None:
    digits = re.sub(r"\D", "", value)
    if not re.fullmatch(r"\+?[\d\s\-()]+", value) or not 8 <= len(digits) <= 15:
        return "El teléfono no es válido."
    return None


def check_rut(value) -> str | None:
    if not is_valid_rut(value):
        return "El RUT no es válido."
    return None


def check_password(value) -> str | None:
    if len(value) < MIN_PASSWORD_LENGTH:
        return f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres."
    if len(value) > 128:
        return "La contraseña es demasiado larga."
    return None


def parse_birth_date(value) -> date | None:
    """Convierte 'YYYY-MM-DD' en date. None si es invalida, futura o irreal."""
    try:
        parsed = datetime.strptime(clean_text(value), "%Y-%m-%d").date()
    except ValueError:
        return None
    today = date.today()
    if parsed >= today or (today.year - parsed.year) > 120:
        return None
    return parsed


def parse_study_year(value) -> int | None:
    """Año de la carrera: entero entre 1 y 10."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if 1 <= number <= 10 else None
