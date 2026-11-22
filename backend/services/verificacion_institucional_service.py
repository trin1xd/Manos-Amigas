"""Comprueba un código de correo. En feria, habilita la cuenta tras confirmarlo.

No constituye una comprobación de identidad ni de matrícula.
"""
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
from database.backend import repository
repo = repository('verificacion_institucional')
from services.auth_service import ServiceError, correo_institucional_aceptado
from utils import apps_script_sender, brevo_sender, validators
from utils.feria_demo import activa as feria_activa

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
    # En la feria cualquier participante puede verificar un buzón REAL propio.
    # Nunca enviar a los correos ficticios creados por los botones de demo.
    if feria_activa():
        if not isinstance(correo, str):
            return False
        direccion = correo.strip().lower()
        dominio = direccion.rsplit('@', 1)[-1]
        return (validators.check_email(direccion) is None
                and dominio not in ('demo.invalid', 'example.com', 'example.org',
                                    'example.net', 'test', 'invalid', 'localhost')
                and not dominio.endswith('.invalid'))
    # Fuera de la feria sigue vigente la política USS.
    return correo_institucional_aceptado(correo)


def _smtp_lista():
    return (apps_script_sender.configurado() or brevo_sender.configurado() or all(os.getenv(x, '').strip() for x in ('MAIL_SMTP_HOST', 'MAIL_SMTP_USER', 'MAIL_SMTP_PASSWORD', 'MAIL_FROM')))


def _mandar_codigo(correo, codigo):
    if apps_script_sender.configurado():
        contenido = ('Tu código de confirmación de Manos Amigas es: ' + codigo +
            '\\nCaduca en 15 minutos. No lo compartas con nadie.\\n'
            'Si no lo solicitaste, ignora este mensaje.\\n')
        apps_script_sender.enviar(correo, 'Manos Amigas: confirma tu correo', contenido)
        return
    if brevo_sender.configurado():
        contenido = ('Tu código de confirmación de Manos Amigas es: ' + codigo +
            '\nCaduca en 15 minutos. No lo compartas con nadie.\n'
            'Si no lo solicitaste, ignora este mensaje.\n')
        brevo_sender.enviar(
            correo, 'Manos Amigas: confirma tu correo institucional', contenido)
        return
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


def _correo_para_confirmar(perfil):
    """En feria confirmar el correo de acceso real, no el campo histórico USS.

    Fuera de feria conserva el envío exclusivamente institucional.
    """
    if feria_activa():
        return perfil.get('correo_cuenta') or perfil['correo']
    return perfil['correo']


def estado(usuario):
    conn = get_connection()
    try:
        cur = conn.cursor()
        perfil = repo.perfil(cur, usuario['id'])
        if not perfil:
            raise ServiceError('Perfil universitario no disponible.', 404)
        destino = _correo_para_confirmar(perfil)
        return {'correo_institucional': destino, 'correo_confirmado': perfil['verificado'],
                'estado_verificacion': perfil['estado'], 'dominio_admitido': _permitido(destino)}
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
        destino = _correo_para_confirmar(perfil)
        if not _permitido(destino):
            raise ServiceError('Necesitas un correo válido al que tengas acceso para recibir el código.', 403)
        actual = repo.codigo(cur, uid, lock=True)
        if actual and actual['ultimo'] and actual['ultimo'] > ahora - timedelta(seconds=MIN_ENVIOS_SEGUNDOS):
            raise ServiceError('Espera 90 segundos antes de solicitar otro código.', 429)
        conteo = (actual['envios'] if actual and actual['dia'] == ahora.date() else 0) + 1
        if conteo > MAX_ENVIOS_DIA:
            # El código antiguo contaba los envíos que Google rechazaba.
            # Recuperar UNA solicitud de feria cuando el último código quedó
            # invalidado y sin uso; sin relajar el máximo de cinco entregas.
            anterior_fallido = (feria_activa() and actual
                               and actual.get('hash') is None
                               and actual.get('vence') is None
                               and actual['envios'] == MAX_ENVIOS_DIA
                               and actual['dia'] == ahora.date())
            if (not anterior_fallido
                    or not hasattr(repo, 'recuperar_un_intento_fallido_anterior')
                    or not repo.recuperar_un_intento_fallido_anterior(cur, uid, ahora.date())):
                raise ServiceError('Superaste el límite diario de códigos.', 429)
            conteo = MAX_ENVIOS_DIA
        repo.emitir_codigo(cur, uid, digest, ahora + timedelta(minutes=MINUTOS_VIGENCIA), ahora.date(), conteo)
        repo.auditar(cur, uid, uid, 'CODIGO_SOLICITADO')
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    try:
        _mandar_codigo(destino, numero)
    except Exception as error:
        # No imprimir código, correo, URL ni clave; invalidar el código fallido.
        rollback = get_connection()
        try:
            repo.invalidar_codigo(rollback.cursor(), uid, digest)
            rollback.commit()
        except Exception:
            rollback.rollback()
        finally:
            rollback.close()
        mensajes_google = {
            'configuracion_incompleta': 'Falta configurar el enlace o la clave de Google Apps Script en Render.',
            'url_invalida': 'La URL de Google Apps Script en Render no es válida. Debe terminar en /exec.',
            'url_no_encontrada': 'Google no encontró la aplicación web. Revisa la URL /exec en Render.',
            'acceso_denegado': 'Google Apps Script no permite el acceso. Revisa que la aplicación web esté publicada para Cualquiera.',
            'metodo_no_permitido': 'Google rechazó la solicitud de envío. Revisa la implementación web de Apps Script.',
            'solicitud_rechazada': 'Apps Script recibió el pedido pero lo rechazó. Comprueba que la clave sea la de la última ejecución de prepararConexion.',
            'respuesta_no_json': 'Google devolvió una página en vez de la respuesta de Apps Script. Revisa el enlace /exec y sus permisos.',
            'fallo_conexion': 'Render no logró conectarse con Google Apps Script. Revisa el enlace /exec.',
            'origen_inesperado': 'Google redirigió el envío fuera de los dominios esperados.',
            'error_http': 'Google respondió con un error al intentar enviar el código.',
            'clave_script_ausente': 'La clave interna no está guardada en las propiedades de Google Apps Script.',
            'solicitud_invalida': 'Apps Script rechazó los datos recibidos. Revisa que el código publicado esté actualizado.',
            'hora_desincronizada': 'Los relojes de Render y Google no coinciden. Intenta nuevamente.',
            'firma_invalida': 'La firma enviada no coincide con la calculada en Google Apps Script. Todavía no sabemos si la clave o el contenido causaron la diferencia.',
            'clave_distinta': 'Confirmado: las claves guardadas en Render y Google Apps Script son diferentes. No generes otra; compara ambas configuraciones.',
            'firma_no_coincide': 'Las claves coinciden, pero el texto firmado es diferente entre Render y Google Apps Script. Se necesita corregir la integración.',
            'solicitud_duplicada': 'Apps Script detectó una solicitud repetida. Solicita un código nuevo.',
            'cuota_agotada': 'La cuenta de Gmail alcanzó su límite diario de envíos desde Apps Script.',
            'error_gmail': 'Google recibió el pedido, pero Gmail no pudo enviar el correo. Revisa los permisos de MailApp en Apps Script.',
            'error_interno': 'Google Apps Script tuvo un error interno. Revisa Ejecuciones en el proyecto de Apps Script.',
        }
        if isinstance(error, apps_script_sender.AppsScriptDeliveryError):
            raise ServiceError(mensajes_google.get(error.motivo, 'No fue posible enviar el código.'), 503) from None
        raise ServiceError('No fue posible enviar el código. Revisa la configuración del correo.', 503) from None
    return {'message': 'Código enviado al correo registrado; vence en 15 minutos.'}


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
        habilitar_al_confirmar = feria_activa()
        # En una sola transacción, el código válido habilita la cuenta
        # para postular SIN requerir la cuenta administradora.
        if not repo.confirmar_correo(cur, uid, habilitar_al_confirmar):
            raise ServiceError('El perfil cambió de estado. Actualiza la página.', 409)
        repo.auditar(cur, uid, uid, 'CORREO_CONFIRMADO')
        conn.commit()
        return {
            'correo_confirmado': True,
            'estado_verificacion': 'VERIFICADO' if habilitar_al_confirmar else 'PENDIENTE_VERIFICACION',
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

