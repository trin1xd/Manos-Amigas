"""Selector explícito de repositorios para SQL Server o PostgreSQL.

La opción predeterminada conserva SQL Server para no cambiar producción.
"""
import importlib
import os

SUPPORTED_ENGINES = {"sqlserver", "postgres"}
REPOSITORIES = frozenset({
    "user", "operations", "notificaciones", "agenda", "seguimiento",
    "chat", "calificaciones", "disponibilidad", "verificacion",
    "verificacion_institucional", "recuperacion",
})


def engine():
    chosen = os.environ.get("DB_ENGINE", "sqlserver").strip().lower()
    if chosen not in SUPPORTED_ENGINES:
        raise RuntimeError("DB_ENGINE debe ser 'sqlserver' o 'postgres'.")
    return chosen


def repository(name):
    if name not in REPOSITORIES:
        raise ValueError("Repositorio desconocido.")
    prefix = "postgres_" if engine() == "postgres" else ""
    return importlib.import_module(f"repositories.{prefix}{name}_repository")
