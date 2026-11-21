"""Pruebas sin red del envío por API HTTPS para Render Free."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils import brevo_sender
from services import verificacion_institucional_service as verif
from services import recuperacion_service as recuperacion


class Respuesta:
    status = 201

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_correo_https_sin_smtp(monkeypatch):
    monkeypatch.setenv("MAIL_BREVO_API_KEY", "clave-ficticia-para-pruebas")
    monkeypatch.setenv("MAIL_FROM", "contacto@ejemplo.test")
    monkeypatch.delenv("MAIL_SMTP_HOST", raising=False)
    monkeypatch.delenv("MAIL_SMTP_USER", raising=False)
    monkeypatch.delenv("MAIL_SMTP_PASSWORD", raising=False)
    assert verif._smtp_lista()
    assert recuperacion._smtp_configurada()
    enviados = []

    def simular_api(req, timeout):
        assert timeout == 12
        assert req.full_url == "https://api.brevo.com/v3/smtp/email"
        assert req.get_header("Api-key") == "clave-ficticia-para-pruebas"
        enviados.append(json.loads(req.data))
        return Respuesta()

    monkeypatch.setattr(brevo_sender, "urlopen", simular_api)
    verif._mandar_codigo("estudiante@correo.uss.cl", "123456")
    assert enviados[0]["to"] == [{"email": "estudiante@correo.uss.cl"}]
    assert "123456" in enviados[0]["textContent"]
    assert "15 minutos" in enviados[0]["textContent"]
    assert "\\n" not in enviados[0]["textContent"]
    assert enviados[0]["sender"]["email"] == "contacto@ejemplo.test"

    monkeypatch.setenv("MAIL_FRONTEND_URL", "https://manos-amigas-feria-2026.onrender.com")
    recuperacion._enviar_correo("persona@example.com", "token-ficticio")
    assert "https://manos-amigas-feria-2026.onrender.com/#/recuperar/token-ficticio" in enviados[1]["textContent"]
    assert "20 minutos" in enviados[1]["textContent"]


def test_no_configurado_si_no_hay_remitente_o_clave(monkeypatch):
    monkeypatch.delenv("MAIL_BREVO_API_KEY", raising=False)
    monkeypatch.setenv("MAIL_FROM", "contacto@ejemplo.test")
    assert not brevo_sender.configurado()
    monkeypatch.setenv("MAIL_BREVO_API_KEY", "clave-ficticia")
    monkeypatch.delenv("MAIL_FROM", raising=False)
    assert not brevo_sender.configurado()
