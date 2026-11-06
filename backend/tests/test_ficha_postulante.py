"""La lista de postulantes incluye una ficha mínima y nunca datos privados."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repositories import operations_repository as repo


class CursorFalso:
    """Registra la consulta y devuelve una fila con las columnas pedidas."""

    def __init__(self):
        self.sql = ''
        self.parametros = None
        self.description = []
        self._filas = []

    def execute(self, sql, parametros=()):
        self.sql = sql
        self.parametros = parametros
        columnas = ['id', 'id_universitario', 'estudiante_nombre', 'estado', 'fecha_creacion',
                    'estudiante_universidad', 'estudiante_carrera', 'estudiante_anio',
                    'estudiante_verificacion']
        self.description = [(c,) for c in columnas]
        self._filas = [(7, 4, 'Sofía Estudiante', 'PENDIENTE', None,
                        'Universidad San Sebastián', 'Enfermería', 3, 'VERIFICADO')]

    def fetchall(self):
        return self._filas


def test_ficha_incluye_universidad_carrera_anio_y_verificacion():
    cursor = CursorFalso()
    postulantes = repo.postulaciones_solicitud(cursor, 12)
    assert cursor.parametros == (12,)
    ficha = postulantes[0]
    assert ficha['estudiante_universidad'] == 'Universidad San Sebastián'
    assert ficha['estudiante_carrera'] == 'Enfermería'
    assert ficha['estudiante_anio'] == 3
    assert ficha['estudiante_verificacion'] == 'VERIFICADO'


def test_consulta_no_pide_datos_privados_y_es_parametrizada():
    cursor = CursorFalso()
    repo.postulaciones_solicitud(cursor, 12)
    consulta = cursor.sql.lower()
    for prohibido in ('rut', 'telefono', 'correo', 'email', 'contacto_emergencia', 'password'):
        assert prohibido not in consulta
    assert 'where p.id_solicitud = ?' in consulta
    assert 'left join dbo.perfiluniversitario' in consulta
