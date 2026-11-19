"""Conexión PostgreSQL para la migración a Supabase (aún no activada).

No sustituye database/connection.py hasta adaptar todas las consultas del
backend, que actualmente usan sintaxis T-SQL y cursores pyodbc.
"""

import os


def get_postgres_connection():
    """Abre una conexión segura a PostgreSQL desde DATABASE_URL.

    Pensado para el Session pooler IPv4 de Supabase en Render.
    DATABASE_URL debe estar configurada únicamente en variables privadas.
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Falta DATABASE_URL para la conexión PostgreSQL.")

    import psycopg

    return psycopg.connect(database_url, sslmode="require", connect_timeout=10)
