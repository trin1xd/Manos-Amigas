"""Envío por HTTPS a Google Apps Script usando la cuenta Gmail del proyecto.

El servidor firma cada solicitud con HMAC-SHA256; la clave compartida
vive solo en las variables de entorno de Render y las propiedades del script.
No se expone en frontend ni en la URL.
"""
import hashlib
import hmac
import json
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class AppsScriptDeliveryError(RuntimeError):
    """Diagnóstico controlado: ningún motivo incluye correo, clave ni código."""
    def __init__(self, motivo):
        self.motivo = motivo
        super().__init__(motivo)


def _motivo_http(status):
    if status in (401, 403):
        return "acceso_denegado"
    if status == 404:
        return "url_no_encontrada"
    if status == 405:
        return "metodo_no_permitido"
    return "error_http"



def configurado():
    return bool(os.getenv("MAIL_APPS_SCRIPT_URL", "").strip()
                and os.getenv("MAIL_APPS_SCRIPT_SECRET", "").strip())


def enviar(destino, asunto, contenido):
    if not configurado():
        raise AppsScriptDeliveryError("configuracion_incompleta")
    url = os.environ["MAIL_APPS_SCRIPT_URL"].strip()
    parsed = urlparse(url)
    if (parsed.scheme != "https"
            or parsed.hostname != "script.google.com"
            or not re.fullmatch(r"/macros/s/[A-Za-z0-9_-]+/exec", parsed.path)
            or parsed.query or parsed.fragment):
        raise AppsScriptDeliveryError("url_invalida")

    # La firma cubre cada campo, incluyendo el código del mensaje, y caduca
    # a los dos minutos. Google verifica la misma firma antes de enviar.
    timestamp = int(time.time())
    firmado = f"{timestamp}\n{destino}\n{asunto}\n{contenido}"
    clave_bytes = os.environ["MAIL_APPS_SCRIPT_SECRET"].encode("utf-8")
    firma = hmac.new(clave_bytes, firmado.encode("utf-8"), hashlib.sha256).hexdigest()
    # Identificador no reversible de una clave aleatoria de 256 bits:
    # detecta si Render y Google tienen claves distintas, incluso cuando
    # ambos verificadores de HMAC devuelven "firma_invalida".
    # Este marcador no reemplaza ni evita la comprobación HMAC.
    huella_clave = hashlib.sha256(clave_bytes).hexdigest()[:16]
    datos = json.dumps({
        "timestamp": timestamp,
        "to": destino,
        "subject": asunto,
        "body": contenido,
        "signature": firma,
        "key_fingerprint": huella_clave,
    }, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=datos,
                  headers={"Content-Type": "application/json",
                           "Accept": "application/json"}, method="POST")
    # Apps Script redirige la respuesta JSON a script.googleusercontent.com.
    # urllib sigue esa redirección; comprobar que Google respondió ok:true.
    try:
        with urlopen(req, timeout=25) as respuesta:
            if respuesta.status != 200:
                raise AppsScriptDeliveryError(_motivo_http(respuesta.status))
            final_url = urlparse(respuesta.url)
            if final_url.scheme != "https" or final_url.hostname not in (
                    "script.google.com", "script.googleusercontent.com"):
                raise AppsScriptDeliveryError("origen_inesperado")
            try:
                resultado = json.loads(respuesta.read(8192))
            except (ValueError, UnicodeDecodeError):
                raise AppsScriptDeliveryError("respuesta_no_json") from None
            if not isinstance(resultado, dict):
                raise AppsScriptDeliveryError("respuesta_no_json")
            if resultado.get("ok") is not True:
                causas = {
                    "clave_ausente": "clave_script_ausente",
                    "solicitud_invalida": "solicitud_invalida",
                    "hora_desincronizada": "hora_desincronizada",
                    "firma_invalida": "firma_invalida",
                    "clave_distinta": "clave_distinta",
                    "solicitud_duplicada": "solicitud_duplicada",
                    "cuota_agotada": "cuota_agotada",
                    "error_gmail": "error_gmail",
                    "error_interno": "error_interno",
                }
                motivo = resultado.get("motivo")
                motivo_seguro = causas.get(motivo, "solicitud_rechazada") if isinstance(motivo, str) else "solicitud_rechazada"
                raise AppsScriptDeliveryError(motivo_seguro)
    except HTTPError as error:
        raise AppsScriptDeliveryError(_motivo_http(error.code)) from None
    except (URLError, TimeoutError, OSError):
        raise AppsScriptDeliveryError("fallo_conexion") from None
