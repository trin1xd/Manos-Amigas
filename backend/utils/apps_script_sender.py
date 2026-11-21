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
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def configurado():
    return bool(os.getenv("MAIL_APPS_SCRIPT_URL", "").strip()
                and os.getenv("MAIL_APPS_SCRIPT_SECRET", "").strip())


def enviar(destino, asunto, contenido):
    if not configurado():
        raise RuntimeError("Apps Script no está configurado.")
    url = os.environ["MAIL_APPS_SCRIPT_URL"].strip()
    parsed = urlparse(url)
    if (parsed.scheme != "https"
            or parsed.hostname != "script.google.com"
            or not re.fullmatch(r"/macros/s/[A-Za-z0-9_-]+/exec", parsed.path)
            or parsed.query or parsed.fragment):
        raise RuntimeError("MAIL_APPS_SCRIPT_URL debe ser el enlace /exec oficial de Google Apps Script.")

    # La firma cubre cada campo, incluyendo el código del mensaje, y caduca
    # a los dos minutos. Google verifica la misma firma antes de enviar.
    timestamp = int(time.time())
    firmado = f"{timestamp}\n{destino}\n{asunto}\n{contenido}"
    firma = hmac.new(
        os.environ["MAIL_APPS_SCRIPT_SECRET"].encode("utf-8"),
        firmado.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    datos = json.dumps({
        "timestamp": timestamp,
        "to": destino,
        "subject": asunto,
        "body": contenido,
        "signature": firma,
    }, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=datos,
                  headers={"Content-Type": "application/json",
                           "Accept": "application/json"}, method="POST")
    # Apps Script redirige la respuesta JSON a script.googleusercontent.com.
    # urllib sigue esa redirección; comprobar que Google respondió ok:true.
    with urlopen(req, timeout=25) as respuesta:
        if respuesta.status != 200:
            raise RuntimeError("Google Apps Script no aceptó la solicitud.")
        final_url = urlparse(respuesta.url)
        if final_url.scheme != "https" or final_url.hostname not in (
                "script.google.com", "script.googleusercontent.com"):
            raise RuntimeError("Respuesta recibida desde un dominio inesperado.")
        resultado = json.loads(respuesta.read(8192))
        if resultado.get("ok") is not True:
            raise RuntimeError("Google Apps Script rechazó el envío.")
