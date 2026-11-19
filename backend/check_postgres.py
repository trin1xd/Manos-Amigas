"""Diagnóstico de conexión PostgreSQL sin exponer datos personales.

Ejecutar solo en entorno de pruebas con DB_ENGINE=postgres y DATABASE_URL.
"""
from database.backend import engine
from database.connection import get_connection


def main():
    if engine() != "postgres":
        raise SystemExit("Configura DB_ENGINE=postgres antes del diagnóstico.")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM public."Roles"')
            roles = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM public."Servicios" WHERE activo = TRUE')
            servicios = cur.fetchone()[0]
        print(f"Conexión PostgreSQL correcta: roles={roles}, servicios_activos={servicios}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
