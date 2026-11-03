"""Utilidades para RUT chileno.

Decision de formato: el RUT se guarda SIN puntos y CON guion, con la K en
mayuscula. Ejemplo: "12.345.678-5" -> "12345678-5".
"""
from __future__ import annotations

import re


def calculate_dv(body: str) -> str:
    """Calcula el digito verificador (modulo 11) para el cuerpo numerico del RUT."""
    total = 0
    factor = 2
    for digit in reversed(body):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1
    remainder = 11 - (total % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def normalize_rut(raw) -> str | None:
    """Devuelve el RUT en formato '12345678-5', o None si el formato es invalido.

    Acepta puntos, guion y espacios. No valida el digito verificador.
    """
    if not isinstance(raw, str):
        return None
    cleaned = re.sub(r"[.\-\s]", "", raw).upper()
    if not re.fullmatch(r"\d{7,8}[0-9K]", cleaned):
        return None
    return f"{cleaned[:-1]}-{cleaned[-1]}"


def is_valid_rut(raw) -> bool:
    """True si el formato es correcto y el digito verificador coincide."""
    rut = normalize_rut(raw)
    if rut is None:
        return False
    body, dv = rut.split("-")
    return calculate_dv(body) == dv
