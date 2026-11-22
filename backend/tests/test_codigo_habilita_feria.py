"""Pruebas del código real como único requisito en la feria; sin red ni SMTP."""
from datetime import timedelta
from pathlib import Path
import sys
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services import verificacion_institucional_service as svc
from repositories import postgres_verificacion_institucional_repository as db_repo
from tests.test_verificacion_correo import ALUMNO, Conn
from services.auth_service import ServiceError


@pytest.fixture
def feria(monkeypatch):
    monkeypatch.setenv("DB_ENGINE", "postgres")
    monkeypatch.setenv("FERIA_REGISTRO_LIBRE", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", "clave-solo-tests")
    conexion = Conn()
    monkeypatch.setattr(svc, "get_connection", lambda: conexion)
    return conexion


def test_feria_acepta_correos_personales_reales_sin_uss(feria):
    assert svc._permitido("participante@gmail.com")
    assert svc._permitido("amiga@outlook.com")
    assert svc._permitido("estudiante@correo.uss.cl")
    assert not svc._permitido("no-es-correo")
    assert not svc._permitido("prueba@demo.invalid")
    assert not svc._permitido("prueba@example.com")


def test_codigo_correcto_habilita_sin_intervencion_administradora(feria, monkeypatch):
    token = "012345"
    hash_correcto = svc._hash_codigo(ALUMNO["id"], token)
    recibido = []
    eventos = []
    monkeypatch.setattr(svc.repo, "perfil", lambda *args, **kw: {
        "estado": "PENDIENTE_VERIFICACION", "verificado": False})
    monkeypatch.setattr(svc.repo, "codigo", lambda *args, **kw: {
        "hash": hash_correcto, "vence": svc._utc() + timedelta(minutes=15),
        "intentos": 0})
    monkeypatch.setattr(svc.repo, "confirmar_correo", lambda cur, user_id, habilitar: (
        recibido.append((user_id, habilitar)) or True))
    monkeypatch.setattr(svc.repo, "auditar", lambda cur, uid, actor, evt: eventos.append(evt))
    out = svc.confirmar_codigo(ALUMNO, {"codigo": token})
    assert out == {"correo_confirmado": True, "estado_verificacion": "VERIFICADO"}
    assert recibido == [(ALUMNO["id"], True)]
    assert eventos == ["CORREO_CONFIRMADO"]
    assert feria.commits == 1


def test_codigo_ajeno_o_incorrecto_no_habilita(feria, monkeypatch):
    hash_correcto = svc._hash_codigo(ALUMNO["id"], "123456")
    llamados = []
    monkeypatch.setattr(svc.repo, "perfil", lambda *args, **kw: {
        "estado": "PENDIENTE_VERIFICACION", "verificado": False})
    monkeypatch.setattr(svc.repo, "codigo", lambda *args, **kw: {
        "hash": hash_correcto, "vence": svc._utc() + timedelta(minutes=10),
        "intentos": 0})
    monkeypatch.setattr(svc.repo, "confirmar_correo", lambda *a: llamados.append("APROBADO"))
    monkeypatch.setattr(svc.repo, "fallo_codigo", lambda *a: llamados.append("FALLO"))
    with pytest.raises(ServiceError) as exc:
        svc.confirmar_codigo(ALUMNO, {"codigo": "987654"})
    assert exc.value.status == 400
    assert llamados == ["FALLO"]
    assert feria.commits == 1
    assert svc._hash_codigo(1234567, "123456") != hash_correcto


def test_codigo_vencido_no_habilita(feria, monkeypatch):
    hash_correcto = svc._hash_codigo(ALUMNO["id"], "123456")
    monkeypatch.setattr(svc.repo, "perfil", lambda *args, **kw: {
        "estado": "PENDIENTE_VERIFICACION", "verificado": False})
    monkeypatch.setattr(svc.repo, "codigo", lambda *args, **kw: {
        "hash": hash_correcto, "vence": svc._utc() - timedelta(seconds=1),
        "intentos": 0})
    monkeypatch.setattr(svc.repo, "confirmar_correo", lambda *a: pytest.fail("No aprobar"))
    monkeypatch.setattr(svc.repo, "fallo_codigo", lambda *a: None)
    with pytest.raises(ServiceError):
        svc.confirmar_codigo(ALUMNO, {"codigo": "123456"})


class Cursor:
    rowcount = 1
    def __init__(self):
        self.queries = []
    def execute(self, query, params):
        self.queries.append((query, params))


def test_repo_actualiza_correo_y_estado_juntos():
    cur = Cursor()
    assert db_repo.confirmar_correo(cur, 35, True)
    assert len(cur.queries) == 2
    query, params = cur.queries[0]
    assert "correo_institucional_verificado=TRUE" in query
    assert "estado_verificacion=%s" in query
    assert params == ("VERIFICADO", 35)
    assert "codigo_hash=NULL" in cur.queries[1][0]


def test_solo_correo_real_del_usuario_recibe_codigo(feria, monkeypatch):
    enviados = []
    cuenta = 'estudiante.real@correo.uss.cl'
    perfil = {
        'correo': 'feria-registro-prueba@demo.invalid',
        'correo_cuenta': cuenta,
        'estado': 'PENDIENTE_VERIFICACION',
        'verificado': False,
    }
    monkeypatch.setattr(svc, '_smtp_lista', lambda: True)
    monkeypatch.setattr(svc.repo, 'perfil', lambda *args, **kwargs: perfil)
    monkeypatch.setattr(svc.repo, 'codigo', lambda *args, **kwargs: None)
    monkeypatch.setattr(svc.repo, 'emitir_codigo', lambda *args, **kwargs: None)
    monkeypatch.setattr(svc.repo, 'auditar', lambda *args, **kwargs: None)
    monkeypatch.setattr(svc, '_mandar_codigo',
                        lambda correo, numero: enviados.append((correo, numero)))
    estado = svc.estado(ALUMNO)
    assert estado['correo_institucional'] == cuenta
    assert estado['dominio_admitido'] is True
    resultado = svc.solicitar_codigo(ALUMNO)
    assert '15 minutos' in resultado['message']
    assert len(enviados) == 1
    assert enviados[0][0] == cuenta
    assert len(enviados[0][1]) == 6
    assert enviados[0][1].isdigit()


def test_firma_otp_fuera_de_feria_conserva_destino_institucional(feria, monkeypatch):
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'false')
    perfil = {'correo': 'alumno@correo.uss.cl', 'correo_cuenta': 'personal@gmail.com'}
    assert svc._correo_para_confirmar(perfil) == 'alumno@correo.uss.cl'
    monkeypatch.setenv('FERIA_REGISTRO_LIBRE', 'true')
    assert svc._correo_para_confirmar(perfil) == 'personal@gmail.com'
