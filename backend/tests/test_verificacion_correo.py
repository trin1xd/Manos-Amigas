"""Megaparche 5: seguridad y flujos, sin SQL Server ni SMTP real."""
import sys
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app
from services import auth_service
from services import verificacion_institucional_service as svc
from services import verificacion_service as review
from services.auth_service import ServiceError

ALUMNO = {'id': 7, 'rol': 'UNIVERSITARIO', 'estado': 'ACTIVO', 'nombre': 'Estudiante',
          'estado_verificacion': 'PENDIENTE_VERIFICACION'}
ADMIN = {'id': 8, 'rol': 'ADMIN', 'estado': 'ACTIVO', 'nombre': 'Admin'}
FAMILIAR = {'id': 9, 'rol': 'FAMILIAR', 'estado': 'ACTIVO', 'nombre': 'Familiar'}


class Conn:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0
    def cursor(self): return object()
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1
    def close(self): pass


@pytest.fixture
def app(monkeypatch):
    users = {7: ALUMNO, 8: ADMIN, 9: FAMILIAR}
    monkeypatch.setattr(auth_service, 'get_user_by_id', lambda id_: users[int(id_)].copy())
    application = create_app()
    application.config['TESTING'] = True
    return application


def headers(app, uid):
    with app.app_context():
        key = create_access_token(identity=str(uid))
    return {'Authorization': f'Bearer {key}'}


def test_rutas_requieren_autenticacion_y_rol(app):
    client = app.test_client()
    assert client.get('/api/verificacion-institucional/mia').status_code == 401
    assert client.post('/api/verificacion-institucional/enviar-codigo').status_code == 401
    assert client.post('/api/verificacion-institucional/confirmar-codigo', json={}).status_code == 401
    assert client.get('/api/verificacion-institucional/mia', headers=headers(app, 9)).status_code == 403


def test_estado_solo_consulta_usuario_autenticado(app, monkeypatch):
    vistos = []
    def fake_estado(user):
        vistos.append(user['id'])
        return {'correo_confirmado': False}
    monkeypatch.setattr(svc, 'estado', fake_estado)
    res = app.test_client().get('/api/verificacion-institucional/mia', headers=headers(app, 7))
    assert res.status_code == 200
    assert vistos == [7]
    assert res.get_json()['data']['correo_confirmado'] is False


def test_dominio_institucional_uss_exacto(monkeypatch):
    assert svc._permitido('alumno@correo.uss.cl') is True
    assert svc._permitido('ALUMNO@CORREO.USS.CL') is True
    for correo in ('alumno@uss.cl', 'alumno@gmail.com', 'alumno@sub.correo.uss.cl',
                   'alumno@correo.uss.cl.ejemplo', 'alumno@otrocorreo.uss.cl',
                   'alumno@correo.uss.cl@ejemplo.com', ''):
        assert svc._permitido(correo) is False
    # Incluso si una variable antigua contiene otro dominio, NO se habilita.
    monkeypatch.setenv('VERIFICACION_DOMINIOS_INSTITUCIONALES', 'ejemplo.com')
    assert svc._permitido('alumno@ejemplo.com') is False


def test_registro_exige_correo_uss(monkeypatch):
    # Aislar las validaciones de correo para probar el rechazo antes de tocar SQL.
    monkeypatch.setitem(auth_service.FIELDS_BY_ROLE, auth_service.UNIVERSITARIO, [
        ('email', 'email', True, 255),
        ('correo_institucional', 'email', True, 255),
    ])
    datos = {'email': 'personal@gmail.com', 'correo_institucional': 'ALUMNO@CORREO.USS.CL'}
    limpio = auth_service._validate(datos, auth_service.UNIVERSITARIO)
    assert limpio['correo_institucional'] == 'alumno@correo.uss.cl'
    for invalido in ('alumno@gmail.com', 'alumno@uss.cl', 'alumno@otrocorreo.uss.cl'):
        with pytest.raises(ServiceError) as error:
            auth_service._validate({**datos, 'correo_institucional': invalido}, auth_service.UNIVERSITARIO)
        assert error.value.status == 400
        assert '@correo.uss.cl' in error.value.errors['correo_institucional']


def test_codigo_malformado_no_consulta_sql(monkeypatch):
    monkeypatch.setattr(svc, 'get_connection', lambda: pytest.fail('No debe consultar BD'))
    for payload in (None, [], {}, {'codigo': 'abc123'}, {'codigo': '12345'},
                    {'codigo': '123456', 'id_universitario': 8}):
        with pytest.raises(ServiceError) as error:
            svc.confirmar_codigo(ALUMNO, payload)
        assert error.value.status == 400


def test_sin_smtp_no_crea_codigo(monkeypatch):
    monkeypatch.delenv('MAIL_SMTP_HOST', raising=False)
    monkeypatch.setattr(svc, 'get_connection', lambda: pytest.fail('No debe consultar BD'))
    with pytest.raises(ServiceError) as error:
        svc.solicitar_codigo(ALUMNO)
    assert error.value.status == 503


def test_reenvio_bloqueado(monkeypatch):
    from datetime import timedelta
    c = Conn()
    monkeypatch.setattr(svc, 'get_connection', lambda: c)
    monkeypatch.setattr(svc, '_smtp_lista', lambda: True)
    monkeypatch.setattr(svc, '_permitido', lambda _: True)
    monkeypatch.setenv('JWT_SECRET_KEY', 'clave-de-test-no-produccion')
    monkeypatch.setattr(svc.repo, 'perfil', lambda *_args, **kwargs: {
        'correo': 'alumno@institucion.cl', 'estado': 'PENDIENTE_VERIFICACION', 'verificado': False})
    monkeypatch.setattr(svc.repo, 'codigo', lambda *_args, **kwargs: {
        'ultimo': svc._utc()-timedelta(seconds=20), 'dia': svc._utc().date(), 'envios': 1})
    monkeypatch.setattr(svc, '_mandar_codigo', lambda *_: pytest.fail('No enviar'))
    with pytest.raises(ServiceError) as error:
        svc.solicitar_codigo(ALUMNO)
    assert error.value.status == 429
    assert c.commits == 0


def test_intento_fallido_se_persiste(monkeypatch):
    from datetime import timedelta
    c = Conn()
    fallos = []
    monkeypatch.setattr(svc, 'get_connection', lambda: c)
    monkeypatch.setenv('JWT_SECRET_KEY', 'clave-de-test-no-produccion')
    monkeypatch.setattr(svc.repo, 'perfil', lambda *_args, **kwargs: {'estado': 'PENDIENTE_VERIFICACION', 'verificado': False})
    monkeypatch.setattr(svc.repo, 'codigo', lambda *_args, **kwargs: {
        'hash': b'x' * 32, 'vence': svc._utc()+timedelta(minutes=10), 'intentos': 0})
    monkeypatch.setattr(svc.repo, 'fallo_codigo', lambda *_args: fallos.append('intento'))
    with pytest.raises(ServiceError) as error:
        svc.confirmar_codigo(ALUMNO, {'codigo': '123456'})
    assert error.value.status == 400
    assert fallos == ['intento']
    assert c.commits == 1


def test_confirmacion_valida_no_aprueba_automaticamente(monkeypatch):
    from datetime import timedelta
    c = Conn()
    events = []
    monkeypatch.setenv('JWT_SECRET_KEY', 'clave-de-test-no-produccion')
    digest = svc._hash_codigo(ALUMNO['id'], '012345')
    monkeypatch.setattr(svc, 'get_connection', lambda: c)
    monkeypatch.setattr(svc.repo, 'perfil', lambda *_args, **kwargs: {'estado': 'PENDIENTE_VERIFICACION', 'verificado': False})
    monkeypatch.setattr(svc.repo, 'codigo', lambda *_args, **kwargs: {
        'hash': digest, 'vence': svc._utc() + timedelta(minutes=10), 'intentos': 0})
    monkeypatch.setattr(svc.repo, 'confirmar_correo', lambda *_args: True)
    monkeypatch.setattr(svc.repo, 'auditar', lambda *_args: events.append(_args[-1]))
    assert svc.confirmar_codigo(ALUMNO, {'codigo': '012345'}) == {'correo_confirmado': True}
    assert c.commits == 1
    assert events == ['CORREO_CONFIRMADO']



def test_admin_de_pruebas_exige_correo_si_configurado(monkeypatch):
    c = Conn()
    monkeypatch.setenv('VERIFICACION_CORREO_OBLIGATORIA', 'true')
    monkeypatch.setattr(review, 'get_connection', lambda: c)
    monkeypatch.setattr(review.repo, 'bloquear_universitario',
                        lambda *_: {'estado': 'PENDIENTE_VERIFICACION', 'id': 7})
    monkeypatch.setattr(review.inst_repo, 'correo_confirmado', lambda *_: False)
    monkeypatch.setattr(review.repo, 'aplicar_decision', lambda *_: pytest.fail('No debe aprobar'))
    with pytest.raises(ServiceError) as e:
        review.decidir(ADMIN, 7, {'accion': 'APROBAR',
            'observacion': 'Aprobación de prueba con email pendiente', 'confirmacion_pruebas': True})
    assert e.value.status == 409
    assert c.commits == 0


def test_admin_aprueba_tras_confirmar_correo(monkeypatch):
    c = Conn()
    monkeypatch.setenv('VERIFICACION_CORREO_OBLIGATORIA', 'true')
    monkeypatch.setattr(review, 'get_connection', lambda: c)
    monkeypatch.setattr(review.repo, 'bloquear_universitario',
                        lambda *_: {'estado': 'PENDIENTE_VERIFICACION', 'id': 7})
    monkeypatch.setattr(review.inst_repo, 'correo_confirmado', lambda *_: True)
    monkeypatch.setattr(review.repo, 'aplicar_decision', lambda *_: True)
    out = review.decidir(ADMIN, 7, {'accion': 'APROBAR',
        'observacion': 'Aprobación demo tras correo confirmado', 'confirmacion_pruebas': True})
    assert out['estado_verificacion'] == 'VERIFICADO'
    assert c.commits == 1
