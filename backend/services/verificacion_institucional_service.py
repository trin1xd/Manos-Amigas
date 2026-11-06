"""Verifica el control del buzon universitario; NO acredita identidad ni habilita tareas."""
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import hashlib
import hmac
import os
import re
import secrets
import smtplib
import ssl

from database.connection import get_connection
from repositories import verificacion_institucional_repository as repo
from services.auth_service import ServiceError, correo_institucional_aceptado

MIN_ENVIOS_SEGUNDOS = 90
MAX_ENVIOS_DIA = 5
MAX_INTENTOS = 5
MINUTOS_VIGENCIA = 15


def _utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _hash_codigo(user_id, codigo):
    key = os.environ.get('JWT_SECRET_KEY', '')
    if not key:
        raise RuntimeError('Configura JWT_SECRET_KEY.')
    return hmac.new(key.encode('utf-8'), f'{user_id}:{codigo}'.encode('ascii'), hashlib.sha256).digest()


def _permitido(correo):
    # Política exacta: no se permiten subdominios ni direcciones parecidas.
    return correo_institucional_aceptado(correo)


def _smtp_lista():
    return all(os.getenv(x, '').strip() for x in ('MAIL_SMTP_HOST', 'MAIL_SMTP_USER', 'MAIL_SMTP_PASSWORD', 'MAIL_FROM'))


def _mandar_codigo(correo, codigo):
    mensaje = EmailMessage()
    mensaje['Subject'] = 'Manos Amigas: confirma tu correo institucional'
    mensaje['From'] = os.environ['MAIL_FROM']
    mensaje['To'] = correo
    mensaje.set_content('Tu código de confirmación de Manos Amigas es: ' + codigo +
        '\nCaduca en 15 minutos. No lo compartas con nadie.\n'
        'Si no lo solicitaste, ignora este mensaje.\n')
    modo = os.getenv('MAIL_SMTP_MODE', 'SSL').strip().upper()
    host = os.environ['MAIL_SMTP_HOST']
    puerto = int(os.getenv('MAIL_SMTP_PORT', '465'))
    contexto = ssl.create_default_context()
    if modo == 'SSL':
        server = smtplib.SMTP_SSL(host, puerto, timeout=12, context=contexto)
    elif modo == 'STARTTLS':
        server = smtplib.SMTP(host, puerto, timeout=12)
    else:
        raise RuntimeError('MAIL_SMTP_MODE debe ser SSL o STARTTLS.')
    with server:
        if modo == 'STARTTLS':
            server.ehlo()
            server.starttls(context=contexto)
            server.ehlo()
        server.login(os.environ['MAIL_SMTP_USER'], os.environ['MAIL_SMTP_PASSWORD'])
        server.send_message(mensaje)


def estado(usuario):
    conn = get_connection()
    try:
        cur = conn.cursor()
        perfil = repo.perfil(cur, usuario['id'])
        if not perfil:
            raise ServiceError('Perfil universitario no disponible.', 404)
        return {'correo_institucional': perfil['correo'], 'correo_confirmado': perfil['verificado'],
                'estado_verificacion': perfil['estado'], 'dominio_admitido': _permitido(perfil['correo'])}
    finally:
        conn.close()


def solicitar_codigo(usuario):
    if not _smtp_lista():
        raise ServiceError('El envío de correos no está configurado. Contacta a soporte.', 503)
    uid = usuario['id']
    ahora = _utc()
    numero = f'{secrets.randbelow(1000000):06d}'
    digest = _hash_codigo(uid, numero)
    conn = get_connection()
    try:
        cur = conn.cursor()
        perfil = repo.perfil(cur, uid, lock=True)
        if not perfil:
            raise ServiceError('Perfil universitario no disponible.', 404)
        if perfil['estado'] != 'PENDIENTE_VERIFICACION':
            raise ServiceError('La revisión de la cuenta ya tiene un estado definitivo.', 409)
        if perfil['verificado']:
            raise ServiceError('Este correo ya está confirmado.', 409)
        if not _permitido(perfil['correo']):
            raise ServiceError('El dominio institucional no está habilitado para el piloto.', 403)
        actual = repo.codigo(cur, uid, lock=True)
        if actual and actual['ultimo'] and actual['ultimo'] > ahora - timedelta(seconds=MIN_ENVIOS_SEGUNDOS):
            raise ServiceError('Espera 90 segundos antes de solicitar otro código.', 429)
        conteo = (actual['envios'] if actual and actual['dia'] == ahora.date() else 0) + 1
        if conteo > MAX_ENVIOS_DIA:
            raise ServiceError('Superaste el límite diario de códigos.', 429)
        repo.emitir_codigo(cur, uid, digest, ahora + timedelta(minutes=MINUTOS_VIGENCIA), ahora.date(), conteo)
        repo.auditar(cur, uid, uid, 'CODIGO_SOLICITADO')
        conn.commit()
        destino = perfil['correo']
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    try:
        _mandar_codigo(destino, numero)
    except Exception:
        # No imprimir código ni correo; invalidar el código si falló su entrega.
        rollback = get_connection()
        try:
            repo.invalidar_codigo(rollback.cursor(), uid, digest)
            rollback.commit()
        except Exception:
            rollback.rollback()
        finally:
            rollback.close()
        raise ServiceError('No fue posible entregar el código. Revisa la configuración SMTP.', 503) from None
    return {'message': 'Código enviado al correo institucional registrado; vence en 15 minutos.'}


def confirmar_codigo(usuario, payload):
    if not isinstance(payload, dict) or set(payload) != {'codigo'} or not isinstance(payload['codigo'], str) or not re.fullmatch(r'\d{6}', payload['codigo']):
        raise ServiceError('Ingresa exactamente los seis dígitos del código.', 400)
    uid = usuario['id']
    ahora = _utc()
    digest = _hash_codigo(uid, payload['codigo'])
    conn = get_connection()
    try:
        cur = conn.cursor()
        perfil = repo.perfil(cur, uid, lock=True)
        if not perfil or perfil['estado'] != 'PENDIENTE_VERIFICACION':
            raise ServiceError('Perfil no disponible para verificación.', 409)
        if perfil['verificado']:
            raise ServiceError('El correo ya fue confirmado.', 409)
        actual = repo.codigo(cur, uid, lock=True)
        valido = (actual and actual['hash'] is not None and actual['vence'] is not None
                  and actual['vence'] > ahora and actual['intentos'] < MAX_INTENTOS
                  and hmac.compare_digest(bytes(actual['hash']), digest))
        if not valido:
            if actual and actual['hash'] is not None and actual['intentos'] < MAX_INTENTOS:
                repo.fallo_codigo(cur, uid)
                conn.commit()  # Conservar intentos fallidos incluso cuando se responde 400.
            raise ServiceError('Código inválido, expirado o agotado. Solicita uno nuevo.', 400)
        if not repo.confirmar_correo(cur, uid):
            raise ServiceError('El perfil cambió de estado. Actualiza la página.', 409)
        repo.auditar(cur, uid, uid, 'CORREO_CONFIRMADO')
        conn.commit()
        return {'correo_confirmado': True}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

