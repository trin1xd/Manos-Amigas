"""Acceso libre de demostración para la feria: desactivado por defecto.

Sólo habilitar sobre la base PostgreSQL de pruebas, nunca como verificación
institucional o de identidad para personas reales.
"""
import os


def activa():
    return (
        os.getenv("FERIA_REGISTRO_LIBRE", "").strip().lower() == "true"
        and os.getenv("DB_ENGINE", "").strip().lower() == "postgres"
    )
