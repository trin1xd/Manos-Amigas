"""Recuperación por correo con token aleatorio de un solo uso (20 minutos).

Sin un servidor SMTP con TLS configurado no se envían correos ni se emiten
vínculos visibles públicamente. El resultado de solicitud es siempre genérico.
"""
import hashlib
import logging
import os
import re
import secrets
import smtplib
import ssl
from email.message import EmailMessage

from werkzeug.security import generate_password_hash
from database.connection import get_connection
from repositories import recuperacion_repository as repo
from services.auth_service import ServiceError
from utils import validators as v

LOG = logging.getLogger(__name__)
RESPUESTA = 'Si existe una cuenta activa con ese correo y el servicio de correo está configurado, recibirás instrucciones.'
TOKEN_RE = re.compile(r'^[A-Za-z0-9_-]{40,64}$')


def _smtp_configurada():
    return all(os.getenv(c, '').strip() for c in
               ('MAIL_SMTP_HOST', 'MAIL_SMTP_USER', 'MAIL_SMTP_PASSWORD', 'MAIL_FROM'))


def _url_recuperacion(token):
    base = os.getenv('MAIL_FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    if not (base.startswith('https://') or base.startswith('http://localhost:')
            or base.startswith('http://127.0.0.1:')):
        raise RuntimeError('MAIL_FRONTEND_URL debe usar HTTPS fuera de localhost.')
    return f'{base}/#/recuperar/{token}'


def _enviar_correo(destino, token):
    # Mensaje solo texto para evitar HTML e inyecciones de contenido.
    message = EmailMessage()
    message['Subject'] = 'Manos Amigas: recuperar contraseña'
    message['From'] = os.environ['MAIL_FROM']
    message['To'] = destino
    message.set_content(
        'Se solicitó recuperar tu contraseña de Manos Amigas.\n\n'
        f'Abre este enlace (vence en 20 minutos, se puede usar una sola vez):\n{_url_recuperacion(token)}\n\n'
        'Si no realizaste esta solicitud, ignora el mensaje.\n')
    host = os.environ['MAIL_SMTP_HOST']
    port = int(os.getenv('MAIL_SMTP_PORT', '465'))
    mode = os.getenv('MAIL_SMTP_MODE', 'SSL').strip().upper()
    ctx = ssl.create_default_context()
    if mode == 'SSL':
        smtp = smtplib.SMTP_SSL(host, port, timeout=12, context=ctx)
    elif mode == 'STARTTLS':
        smtp = smtplib.SMTP(host, port, timeout=12)
    else:
        raise RuntimeError('MAIL_SMTP_MODE debe ser SSL o STARTTLS.')
    with smtp:
        if mode == 'STARTTLS':
            smtp.ehlo()
            smtp.starttls(context=ctx)
            smtp.ehlo()
        smtp.login(os.environ['MAIL_SMTP_USER'], os.environ['MAIL_SMTP_PASSWORD'])
        smtp.send_message(message)


def solicitar(datos):
    if not isinstance(datos, dict) or set(datos) != {'email'} or not isinstance(datos['email'], str):
        raise ServiceError('Ingresa un correo electrónico válido.', 400)
    email = v.normalize_email(datos['email'])
    if v.check_email(email):
        raise ServiceError('Ingresa un correo electrónico válido.', 400)

    # No crear tokens que no pueden entregarse a su titular.
    if not _smtp_configurada():
        LOG.warning('Recuperación no disponible: configura MAIL_SMTP_HOST/USER/PASSWORD/FROM.')
        return RESPUESTA

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode('ascii')).digest()
    conn = get_connection()
    destino = None
    try:
        cur = conn.cursor()
        usuario = repo.usuario_activo(cur, email)
        if usuario and not repo.reciente(cur, usuario['id']):
            repo.crear(cur, usuario['id'], token_hash)
            destino = usuario['email']
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    if destino:
        try:
            _enviar_correo(destino, token)
        except Exception:
            # No registrar token, enlace ni credenciales en logs.
            LOG.warning('No fue posible entregar un correo de recuperación (sin datos sensibles).')
            try:
                conn = get_connection()
                try:
                    repo.invalidar(conn.cursor(), token_hash)
                    conn.commit()
                finally:
                    conn.close()
            except Exception:
                LOG.warning('No fue posible invalidar un token de recuperación fallido.')
    return RESPUESTA


def confirmar(datos):
    if not isinstance(datos, dict) or set(datos) != {'token', 'password'}:
        raise ServiceError('Solicitud de recuperación inválida.', 400)
    token = datos['token']
    password = datos['password']
    if not isinstance(token, str) or not TOKEN_RE.fullmatch(token):
        raise ServiceError('Enlace inválido o vencido. Solicita uno nuevo.', 400)
    if not isinstance(password, str):
        raise ServiceError('La contraseña es obligatoria.', 400)
    password_error = v.check_password(password)
    if password_error:
        raise ServiceError(password_error, 400)

    hashed = hashlib.sha256(token.encode('ascii')).digest()
    password_hash = generate_password_hash(password)
    conn = get_connection()
    try:
        cur = conn.cursor()
        uid = repo.validar_y_bloquear(cur, hashed)
        if uid is None:
            raise ServiceError('Enlace inválido o vencido. Solicita uno nuevo.', 400)
        repo.actualizar_clave(cur, uid, password_hash)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return 'Contraseña actualizada. Ya puedes iniciar sesión.'
