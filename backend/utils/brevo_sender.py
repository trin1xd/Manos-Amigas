"""Enviar correos transaccionales por HTTPS en Render Free, sin exponer claves.

La autenticación se realiza mediante MAIL_BREVO_API_KEY, configurada en Render.
No se imprime información de correos, tokens ni secretos en logs.
"""
import json
import os
from urllib.request import Request, urlopen


URL_BREVO = "https://api.brevo.com/v3/smtp/email"


def configurado():
    return bool(os.getenv("MAIL_BREVO_API_KEY", "").strip()
                and os.getenv("MAIL_FROM", "").strip())


def enviar(destino, asunto, contenido):
    """Envía solo mensajes de texto. Requiere remitente registrado en Brevo."""
    if not configurado():
        raise RuntimeError("Servicio de correo HTTPS sin configurar.")
    # Se envía solo al destinatario solicitado por el flujo autenticado.
    payload = {
        "sender": {
            "name": os.getenv("MAIL_FROM_NAME", "Manos Amigas"),
            "email": os.environ["MAIL_FROM"].strip(),
        },
        "to": [{"email": destino}],
        "subject": asunto,
        "textContent": contenido,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        URL_BREVO,
        data=data,
        headers={
            "api-key": os.environ["MAIL_BREVO_API_KEY"].strip(),
            "accept": "application/json",
            "content-type": "application/json",
        },
        method="POST",
    )
    # Si Brevo no acepta el envío, urllib eleva excepción; el llamador
    # invalida el código/token pendiente sin revelar datos privados.
    with urlopen(req, timeout=12) as respuesta:
        if respuesta.status not in (200, 201, 202):
            raise RuntimeError("Proveedor de correo rechazó el envío.")
