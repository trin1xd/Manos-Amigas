"""Pruebas del selector de base de datos, sin acceso a internet ni credenciales."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.backend import engine, repository
from database import connection


def test_sqlserver_es_predeterminado(monkeypatch):
    monkeypatch.delenv("DB_ENGINE", raising=False)
    assert engine() == "sqlserver"
    assert repository("user").__name__ == "repositories.user_repository"


def test_postgres_selecciona_repositorios_correctos(monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "postgres")
    assert repository("user").__name__ == "repositories.postgres_user_repository"
    assert repository("notificaciones").__name__ == "repositories.postgres_notificaciones_repository"
    assert repository("verificacion_institucional").__name__ == "repositories.postgres_verificacion_institucional_repository"


def test_motor_desconocido_rechazado(monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "sqlite")
    with pytest.raises(RuntimeError):
        engine()


def test_repositorio_desconocido_rechazado():
    with pytest.raises(ValueError):
        repository("../../secretos")


def test_postgres_no_funciona_sin_variable_privada(monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "postgres")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        connection.get_connection()


def test_postgres_redirecciona_a_conexion_aislada(monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "postgres")
    from database import postgres_connection
    marker = object()
    monkeypatch.setattr(postgres_connection, "get_postgres_connection", lambda: marker)
    assert connection.get_connection() is marker
