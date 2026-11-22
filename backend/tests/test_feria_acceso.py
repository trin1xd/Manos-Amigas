"""Entrada sin formularios para visitantes, probada solo con DB ficticia."""
import sys
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from services import auth_service
from tests.test_auth_jwt import JwtFakeRepo
from tests.test_auth import FakeConnection, FakeDb
from utils.rut import is_valid_rut


class FeriaRepo(JwtFakeRepo):
    def habilitar_universitario_para_feria(self, db, id_usuario):
        perfil = next((p for p in db.profiles if p['id_usuario'] == id_usuario), None)
        if not perfil or perfil['estado_verificacion'] != 'PENDIENTE_VERIFICACION':
            raise RuntimeError('Perfil de prueba inválido.')
        perfil['estado_verificacion'] = 'VERIFICADO'


@pytest.fixture
def contexto(monkeypatch):
    fake = FakeDb()
    monkeypatch.setattr(auth_service, 'get_connection', lambda: FakeConnection(fake))
    monkeypatch.setattr(auth_service, 'repo', FeriaRepo())
    monkeypatch.setenv('DB_ENGINE', 'postgres')
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client(), fake


def test_entrada_sin_flag_no_esta_disponible(contexto, monkeypatch):
    client, db = contexto
    monkeypatch.delenv('FERIA_REGISTRO_LIBRE', raising=False)
    response = client.post('/api/auth/demo', json={'rol': 'UNIVERSITARIO'})
    assert response.status_code == 404
    assert len(db.users) == 0


@pytest.mark.parametrize('rol', ['ADULTO_MAYOR', 'UNIVERSITARIO'])
def test_visitante_ingresa_directamente_y_consulta_su_perfil(contexto, monkeypatch, rol):
    client, db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    response = client.post('/api/auth/demo', json={'rol': rol})
    assert response.status_code == 201, response.get_json()
    body = response.get_json()
    assert body['user']['rol'] == rol
    assert body['access_token']
    assert not any(k in body for k in ('password', 'password_hash'))
    assert is_valid_rut(db.users[0]['rut'])
    assert db.users[0]['email'].endswith('@demo.invalid')
    me = client.get('/api/auth/me', headers={
        'Authorization': 'Bearer ' + body['access_token']
    })
    assert me.status_code == 200, me.get_json()
    assert me.get_json()['user']['rol'] == rol
    if rol == 'UNIVERSITARIO':
        assert body['user']['estado_verificacion'] == 'VERIFICADO'
        assert db.profiles[0]['estado_verificacion'] == 'VERIFICADO'


def test_registro_publico_universitario_espera_codigo(contexto, monkeypatch):
    client, db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    datos = {
        'nombre_completo': 'Universitaria ficticia',
        'rut': '12345678-5',
        'fecha_nacimiento': '2002-03-10',
        'telefono': '+56911112222',
        'email': 'universitaria@gmail.com',
        'password': 'clave-demostracion-123',
        'universidad': 'Universidad de prueba',
        'carrera': 'Enfermería',
        'anio_cursa': 2,
        'contacto_emergencia_nombre': 'Contacto de ejemplo',
        'contacto_emergencia_telefono': '+56911112222',
    }
    response = client.post('/api/auth/register/universitario', json=datos)
    assert response.status_code == 201, response.get_json()
    assert response.get_json()['user']['estado_verificacion'] == 'PENDIENTE_VERIFICACION'
    assert response.get_json()['user']['acceso_feria'] is True
    assert db.profiles[0]['correo_institucional'].startswith('feria-registro-')
    assert db.profiles[0]['correo_institucional'].endswith('@demo.invalid')
    assert db.users[0]['email'] == 'universitaria@gmail.com'
    assert db.profiles[0]['estado_verificacion'] == 'PENDIENTE_VERIFICACION'


def test_entrada_invalida_no_crea_usuarios(contexto, monkeypatch):
    client, db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    for data in ({'rol': 'ADMIN'}, {'rol': 'FAMILIAR'}, {}, {'rol': 'UNIVERSITARIO', 'id': 1}):
        response = client.post('/api/auth/demo', json=data)
        assert response.status_code == 400
    assert len(db.users) == 0


def test_registro_duplicado_identifica_correo_y_rut(contexto, monkeypatch):
    """No obligar a buscar qué dato fue rechazado."""
    client, _db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    datos = {
        'nombre_completo': 'Persona de ejemplo',
        'rut': '12345678-5',
        'fecha_nacimiento': '2002-01-01',
        'telefono': '+56912345678',
        'email': 'prueba.correo@gmail.com',
        'password': 'clave-de-ejemplo-123',
        'universidad': 'Universidad de ejemplo',
        'carrera': 'Carrera de ejemplo',
        'anio_cursa': 2,
        'contacto_emergencia_nombre': 'Persona de ejemplo',
        'contacto_emergencia_telefono': '+56912345678',
    }
    primero = client.post('/api/auth/register/universitario', json=datos)
    assert primero.status_code == 201
    segundo = client.post('/api/auth/register/universitario', json=datos)
    assert segundo.status_code == 409
    errores = segundo.get_json().get('errors', {})
    assert 'rut' in errores
    assert 'email' in errores
    # La referencia institucional de feria es única por registro,
    # por lo que el duplicado corresponde al correo de acceso y al RUT.
    assert 'correo_institucional' not in errores


def test_correo_uss_ocupado_por_prueba_no_impide_nuevo_registro(contexto, monkeypatch):
    """Un email reservado en otro perfil no supone cuenta creada por su dueño."""
    client, db = contexto
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    correo_uss = 'persona.real@correo.uss.cl'
    # Simula un perfil antiguo distinto que reservó el correo institucional.
    db.profiles.append({'id_usuario': 9999,
                        'correo_institucional': correo_uss,
                        'tipo': 'UNIVERSITARIO',
                        'estado_verificacion': 'PENDIENTE_VERIFICACION'})
    datos = {
        'nombre_completo': 'Estudiante de prueba',
        'rut': '12345678-5',
        'fecha_nacimiento': '2002-03-10',
        'telefono': '+56911112222',
        'email': correo_uss,
        'password': 'clave-demostracion-123',
        'universidad': 'Universidad San Sebastián',
        'carrera': 'Enfermería',
        'anio_cursa': 2,
        'contacto_emergencia_nombre': 'Contacto de prueba',
        'contacto_emergencia_telefono': '+56933334444',
    }
    response = client.post('/api/auth/register/universitario', json=datos)
    assert response.status_code == 201, response.get_json()
    assert db.users[0]['email'] == correo_uss
    assert db.profiles[0]['correo_institucional'] == correo_uss
    assert db.profiles[1]['correo_institucional'].endswith('@demo.invalid')
    assert db.profiles[1]['estado_verificacion'] == 'PENDIENTE_VERIFICACION'


def test_feria_acceso_universitario_pendiente_sin_confirmacion(contexto, monkeypatch):
    from services import operations_service as ops
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    assert auth_service._acceso_feria('PENDIENTE_VERIFICACION')
    assert ops._perfil_utilizable({'estado_verificacion': 'PENDIENTE_VERIFICACION'})
    assert auth_service._acceso_feria('VERIFICADO')
    for estado in ('RECHAZADO', 'SUSPENDIDO', None):
        assert not auth_service._acceso_feria(estado)
        assert not ops._perfil_utilizable({'estado_verificacion': estado})
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'false')
    assert not auth_service._acceso_feria('PENDIENTE_VERIFICACION')
    assert not ops._perfil_utilizable({'estado_verificacion': 'PENDIENTE_VERIFICACION'})


def test_feria_codigo_clausurado_sin_acceso_a_bd_ni_mail(contexto, monkeypatch):
    from services import verificacion_institucional_service as verification
    from services.auth_service import ServiceError
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    monkeypatch.setattr(verification, 'get_connection',
                        lambda: pytest.fail('No debe consultar la base para enviar códigos'))
    monkeypatch.setattr(verification, '_smtp_lista',
                        lambda: pytest.fail('No debe consultar proveedores de correo'))
    usuario = {'id': 21, 'rol': 'UNIVERSITARIO'}
    for llamar in (
        lambda: verification.solicitar_codigo(usuario),
        lambda: verification.confirmar_codigo(usuario, {'codigo': '123456'}),
    ):
        with pytest.raises(ServiceError) as ex:
            llamar()
        assert ex.value.status == 410
        assert 'pausada' in ex.value.message


def test_operaciones_feria_exigen_estudiante_activo_y_pendiente(contexto, monkeypatch):
    from services import operations_service as ops
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    estados = []
    class RepoFalso:
        def estudiante_pendiente_feria(self, _cursor, uid):
            estados.append(uid)
            return {'id': uid}
        def estudiante_verificado(self, _cursor, uid):
            return {'id': uid}
    monkeypatch.setattr(ops, 'repo', RepoFalso())
    assert ops._estudiante_habilitado(None, {
        'id': 21, 'estado_verificacion': 'PENDIENTE_VERIFICACION'})
    assert estados == [21]
    for estado in ('RECHAZADO', 'SUSPENDIDO'):
        assert not ops._estudiante_habilitado(None, {
            'id': 21, 'estado_verificacion': estado})
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'false')
    assert not ops._estudiante_habilitado(None, {
        'id': 21, 'estado_verificacion': 'PENDIENTE_VERIFICACION'})
