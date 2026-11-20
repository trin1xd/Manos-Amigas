"""Pruebas del interruptor de aprobación administrativa en entorno piloto."""
from pathlib import Path
import os
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.admin_test_gate import habilitado


def test_desactivado_por_defecto():
    with patch.dict(os.environ, {}, clear=True):
        assert habilitado() is False


def test_ambos_interruptores_y_postgres_son_obligatorios():
    base = {
        "ADMIN_VERIFICACION_PRUEBAS": "true",
        "ADMIN_ENTORNO_PRUEBAS": "true",
        "DB_ENGINE": "postgres",
    }
    with patch.dict(os.environ, base, clear=True):
        assert habilitado() is True
    for nombre in base:
        sin_una = {**base, nombre: "false" if nombre != "DB_ENGINE" else "sqlserver"}
        with patch.dict(os.environ, sin_una, clear=True):
            assert habilitado() is False


def test_no_depende_de_debug_flask():
    with patch.dict(os.environ, {"FLASK_DEBUG": "true"}, clear=True):
        assert habilitado() is False
