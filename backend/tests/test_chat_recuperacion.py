"""Pruebas del Megaparche 2 sin conexión a SQL Server ni envío de email real."""
import hashlib
import sys
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import chat_service as chat
from services import recuperacion_service as rec
from services.auth_service import ServiceError

USUARIOS = {
    1: {'id': 1, 'nombre': 'Adulto', 'rol': 'ADULTO_MAYOR', 'estado': 'ACTIVO'},
    2: {'id': 2, 'nombre': 'Estudiante', 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO', 'estado_verificacion': 'VERIFICADO'},
    3: {'id': 3, 'nombre': 'Familiar', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    4: {'id': 4, 'nombre': 'Ajenos', 'rol': 'FAMILIAR', 'estado': 'ACTIVO'},
    5: {'id': 5, 'nombre': 'Admin', 'rol': 'ADMIN', 'estado': 'ACTIVO'},
}


class FakeConn:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0
    def cursor(self):
        return object()
    def commit(self):
        self.commits += 1
    def rollback(self):
        self.rollbacks += 1
    def close(self):
        pass


def token(app, uid):
    with app.app_context():
        t = create_access_token(identity=str(uid))
    return {'Authorization': 'Bearer ' + t}


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda uid: USUARIOS[int(uid)].copy())
    instance = create_app()
    instance.config['TESTING'] = True
    return instance


def test_chat_obliga_jwt_y_rol(app, monkeypatch):
    client = app.test_client()
    assert client.get('/api/chat/conversaciones').status_code == 401
    assert client.get('/api/chat/conversaciones', headers=token(app, 5)).status_code == 403
    monkeypatch.setattr(chat, 'conversaciones', lambda user: [{'id': 7}])
    assert client.get('/api/chat/conversaciones', headers=token(app, 1)).get_json()['conversaciones'][0]['id'] == 7


def contexto(estado='ASIGNADA'):
    return {'id_adulto': 1, 'id_universitario': 2, 'estado': estado}


def configurar_chat(monkeypatch, estado='ASIGNADA', vinculado=True, rapido=False):
    fake = FakeConn()
    events = []
    monkeypatch.setattr(chat, 'get_connection', lambda: fake)
    monkeypatch.setattr(chat.repo, 'contexto', lambda *_args, **_kwargs: contexto(estado))
    monkeypatch.setattr(chat.repo, 'limite_rapidez', lambda *_args: rapido)
    monkeypatch.setattr(chat.repo, 'guardar', lambda _, sid, uid, msg: events.append((sid, uid, msg)) or 80)
    monkeypatch.setattr(chat.repo, 'listar_mensajes', lambda *_args: [{'id': 1}])
    monkeypatch.setattr(chat.ops_repo, 'vinculo', lambda _cur, id_familiar, _adulto: {'activo': True} if vinculado and id_familiar == 3 else None)
    monkeypatch.setattr(chat.ops_repo, 'adulto_activo', lambda *_args: {'id': 1})
    return fake, events


def test_solo_asignados_pueden_leer(monkeypatch):
    fake, _ = configurar_chat(monkeypatch)
    assert chat.mensajes(USUARIOS[1], 7) == [{'id': 1}]
    assert chat.mensajes(USUARIOS[2], 7) == [{'id': 1}]
    assert chat.mensajes(USUARIOS[3], 7) == [{'id': 1}]
    with pytest.raises(ServiceError) as exc:
        chat.mensajes(USUARIOS[4], 7)
    assert exc.value.status == 404
    assert fake.commits == 0


def test_familiar_revocado_no_puede_escribir(monkeypatch):
    fake, events = configurar_chat(monkeypatch, vinculado=False)
    with pytest.raises(ServiceError) as exc:
        chat.enviar(USUARIOS[3], 7, {'mensaje': 'Hola'})
    assert exc.value.status == 404
    assert not events and fake.rollbacks == 1


def test_chat_envia_un_solo_mensaje_y_hace_commit(monkeypatch):
    fake, events = configurar_chat(monkeypatch)
    assert chat.enviar(USUARIOS[2], 7, {'mensaje': ' Hola adulto  '})['id'] == 80
    assert events == [(7, 2, 'Hola adulto')]
    assert fake.commits == 1


def test_chat_finalizado_solo_lectura(monkeypatch):
    fake, events = configurar_chat(monkeypatch, estado='FINALIZADA')
    assert chat.mensajes(USUARIOS[1], 7) == [{'id': 1}]
    with pytest.raises(ServiceError) as exc:
        chat.enviar(USUARIOS[1], 7, {'mensaje': 'Hola'})
    assert exc.value.status == 409
    assert not events and fake.commits == 0


@pytest.mark.parametrize('payload', [None, {}, [], {'mensaje': ''}, {'mensaje': ' '},
                                    {'mensaje': 'x' * 501}, {'mensaje': 'x', 'remitente': 2}])
def test_chat_valida_payload_sin_acceder_bd(monkeypatch, payload):
    monkeypatch.setattr(chat, 'get_connection', lambda: pytest.fail('No debe tocar la base'))
    with pytest.raises(ServiceError) as exc:
        chat.enviar(USUARIOS[2], 7, payload)
    assert exc.value.status == 400


def test_chat_limite_tres_segundos(monkeypatch):
    fake, events = configurar_chat(monkeypatch, rapido=True)
    with pytest.raises(ServiceError) as exc:
        chat.enviar(USUARIOS[2], 7, {'mensaje': 'hola'})
    assert exc.value.status == 429 and not events and fake.commits == 0


def test_recuperacion_sin_smtp_no_expone_token(monkeypatch):
    monkeypatch.setattr(rec, '_smtp_configurada', lambda: False)
    monkeypatch.setattr(rec, 'get_connection', lambda: pytest.fail('Sin correo no se genera token'))
    result = rec.solicitar({'email': 'persona@example.com'})
    assert 'token' not in result.lower()
    assert 'cuenta' in result


def test_recuperacion_correo_desconocido_mismo_mensaje(monkeypatch):
    fake = FakeConn()
    monkeypatch.setattr(rec, '_smtp_configurada', lambda: True)
    monkeypatch.setattr(rec, 'get_connection', lambda: fake)
    monkeypatch.setattr(rec.repo, 'usuario_activo', lambda *_args: None)
    monkeypatch.setattr(rec, '_enviar_correo', lambda *_args: pytest.fail('No debe enviar'))
    result = rec.solicitar({'email': 'desconocido@example.com'})
    assert result == rec.RESPUESTA
    assert fake.commits == 1


def test_recuperacion_token_hasheado_y_no_devuelto(monkeypatch):
    fake = FakeConn()
    hashes = []
    enviados = []
    monkeypatch.setattr(rec, '_smtp_configurada', lambda: True)
    monkeypatch.setattr(rec, 'get_connection', lambda: fake)
    monkeypatch.setattr(rec.repo, 'usuario_activo', lambda *_args: {'id': 1, 'email': 'adulto@example.com'})
    monkeypatch.setattr(rec.repo, 'reciente', lambda *_args: False)
    monkeypatch.setattr(rec.repo, 'crear', lambda _, uid, h: hashes.append(h))
    monkeypatch.setattr(rec, '_enviar_correo', lambda destino, t: enviados.append((destino, t)))
    result = rec.solicitar({'email': 'adulto@example.com'})
    assert fake.commits == 1 and len(hashes) == 1 and len(enviados) == 1
    assert len(hashes[0]) == 32
    assert hashlib.sha256(enviados[0][1].encode('ascii')).digest() == hashes[0]
    assert enviados[0][1] not in result


def test_recuperacion_enlace_uso_unico(monkeypatch):
    fake = FakeConn()
    intentos = [1, None]
    guardados = []
    monkeypatch.setattr(rec, 'get_connection', lambda: fake)
    monkeypatch.setattr(rec.repo, 'validar_y_bloquear', lambda *_args: intentos.pop(0))
    monkeypatch.setattr(rec.repo, 'actualizar_clave', lambda _, uid, h: guardados.append((uid, h)))
    un_token = 'a' * 43
    assert 'actualizada' in rec.confirmar({'token': un_token, 'password': 'UnaClaveSegura-2026'})
    assert guardados[0][0] == 1 and guardados[0][1] != 'UnaClaveSegura-2026'
    with pytest.raises(ServiceError) as exc:
        rec.confirmar({'token': un_token, 'password': 'OtraClaveSegura-2026'})
    assert exc.value.status == 400
    assert fake.commits == 1


def test_recuperacion_valida_longitud_de_clave(monkeypatch):
    monkeypatch.setattr(rec, 'get_connection', lambda: pytest.fail('No debe tocar BD'))
    with pytest.raises(ServiceError) as exc:
        rec.confirmar({'token': 'a' * 43, 'password': '123'})
    assert exc.value.status == 400


def test_endpoint_recuperacion_sin_autenticacion(app, monkeypatch):
    monkeypatch.setattr(rec, 'solicitar', lambda _data: rec.RESPUESTA)
    resp = app.test_client().post('/api/auth/recuperacion/solicitar', json={'email': 'x@example.com'})
    assert resp.status_code == 200
    assert resp.get_json()['message'] == rec.RESPUESTA


def test_jwt_antiguo_se_revoca_al_cambiar_password_version(app, monkeypatch):
    cuenta = dict(USUARIOS[1], _password_version=1)
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda _uid: cuenta.copy())
    client = app.test_client()
    # Un token previo al reseteo tiene version 0 (o no contiene el claim).
    assert client.get('/api/auth/me', headers=token(app, 1)).status_code == 401
    assert client.get('/api/chat/conversaciones', headers=token(app, 1)).status_code == 401
    with app.app_context():
        nuevo = create_access_token(identity='1', additional_claims={'pwd_ver': 1})
    response = client.get('/api/auth/me', headers={'Authorization': 'Bearer ' + nuevo})
    assert response.status_code == 200
    assert '_password_version' not in response.get_json()['user']
