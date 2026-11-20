"""Habilitación explícita de decisiones administrativas solo en el piloto PostgreSQL.

No activa Flask debug ni altera autenticación/autorización de rutas.
Los despliegues normales mantienen la aprobación desactivada por defecto.
"""
import os


def habilitado():
    return (
        os.getenv("ADMIN_VERIFICACION_PRUEBAS", "").strip().lower() == "true"
        and os.getenv("ADMIN_ENTORNO_PRUEBAS", "").strip().lower() == "true"
        and os.getenv("DB_ENGINE", "").strip().lower() == "postgres"
    )
