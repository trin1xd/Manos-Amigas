"""Configuración global de fixtures y entorno para pytest."""
import os

# Clave secreta dedicada para pruebas automatizadas (aislada de .env)
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-para-pruebas-en-memoria-123456789")

