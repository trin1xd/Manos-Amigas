"""Pruebas del puente seguro entre Render y Google Apps Script, sin Internet."""
import hashlib
import hmac
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
import sys

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import recuperacion_service as recovery
from services import verificacion_institucional_service as verification
from utils import apps_script_sender as sender


class Respuesta:
    status = 200
    url = "https://script.googleusercontent.com/macros/echo?x=prueba"

    def __init__(self, ok=True):
        self.ok = ok

    def read(self, *_):
        return json.dumps({"ok": self.ok}).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@pytest.fixture
def configuracion(monkeypatch):
    monkeypatch.setenv("MAIL_APPS_SCRIPT_URL",
                       "https://script.google.com/macros/s/AKfycbTEST_123/exec")
    monkeypatch.setenv("MAIL_APPS_SCRIPT_SECRET", "clave-ficticia-segura-prueba")
    monkeypatch.delenv("MAIL_BREVO_API_KEY", raising=False)
    monkeypatch.delenv("MAIL_SMTP_HOST", raising=False)
    return monkeypatch


def test_correo_firmado_y_compatible_con_gmail(configuracion):
    envios = []

    def api_falsa(req, timeout):
        assert timeout == 25
        assert req.full_url.startswith("https://script.google.com/macros/s/")
        assert req.get_method() == "POST"
        assert req.get_header("Content-type") == "application/json"
        datos = json.loads(req.data)
        firmado = (f"{datos['timestamp']}\n{datos['to']}\n"
                   f"{datos['subject']}\n{datos['body']}")
        firma = hmac.new(
            b"clave-ficticia-segura-prueba", firmado.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        assert hmac.compare_digest(firma, datos["signature"])
        envios.append(datos)
        return Respuesta()

    configuracion.setattr(sender, "urlopen", api_falsa)
    assert verification._smtp_lista() is True
    assert recovery._smtp_configurada() is True
    verification._mandar_codigo("persona@gmail.com", "012345")
    assert envios[0]["to"] == "persona@gmail.com"
    assert "012345" in envios[0]["body"]
    assert "15 minutos" in envios[0]["body"]
    assert "MANOS_AMIGAS_SECRET" not in str(envios)

    configuracion.setenv("MAIL_FRONTEND_URL", "https://manos-amigas-feria-2026.onrender.com")
    recovery._enviar_correo("usuario@outlook.com", "token-prueba")
    assert len(envios) == 2
    assert "/#/recuperar/token-prueba" in envios[1]["body"]


def test_error_de_google_no_se_considera_correo_enviado(configuracion):
    configuracion.setattr(sender, "urlopen", lambda *a, **kw: Respuesta(ok=False))
    with pytest.raises(sender.AppsScriptDeliveryError) as exc:
        sender.enviar("persona@gmail.com", "Asunto", "Contenido")
    assert exc.value.motivo == "solicitud_rechazada"


def test_rechaza_url_no_oficial(configuracion):
    configuracion.setenv("MAIL_APPS_SCRIPT_URL", "https://sitio-falso.example/recibir")
    configuracion.setattr(sender, "urlopen", lambda *a, **kw:
                          pytest.fail("No enviar datos a dominio ajeno"))
    with pytest.raises(sender.AppsScriptDeliveryError) as exc:
        sender.enviar("persona@gmail.com", "Asunto", "Contenido")
    assert exc.value.motivo == "url_invalida"


def test_incompleto_no_se_activa(configuracion):
    configuracion.delenv("MAIL_APPS_SCRIPT_SECRET")
    assert not sender.configurado()
    configuracion.setenv("MAIL_APPS_SCRIPT_SECRET", "prueba")
    configuracion.delenv("MAIL_APPS_SCRIPT_URL")
    assert not sender.configurado()


@pytest.mark.parametrize("status,motivo", [
    (403, "acceso_denegado"),
    (404, "url_no_encontrada"),
    (405, "metodo_no_permitido"),
    (500, "error_http"),
])
def test_errores_http_sin_filtrar_informacion(configuracion, status, motivo):
    def google_rechaza(req, timeout):
        raise HTTPError(req.full_url, status, "Error de prueba", {}, None)
    configuracion.setattr(sender, "urlopen", google_rechaza)
    with pytest.raises(sender.AppsScriptDeliveryError) as error:
        sender.enviar("persona@gmail.com", "asunto", "mensaje")
    assert error.value.motivo == motivo
    assert "persona@gmail.com" not in str(error.value)


def test_error_de_conexion_seguro(configuracion):
    def sin_red(*args, **kwargs):
        raise URLError("Google no responde")
    configuracion.setattr(sender, "urlopen", sin_red)
    with pytest.raises(sender.AppsScriptDeliveryError) as error:
        sender.enviar("persona@gmail.com", "asunto", "mensaje")
    assert error.value.motivo == "fallo_conexion"
