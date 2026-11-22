"""La lista de postulantes incluye una ficha mínima y nunca datos privados."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repositories import operations_repository as repo
from repositories import postgres_operations_repository as postgres_repo


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
                    'estudiante_verificacion', 'estudiante_calificacion_promedio',
                    'estudiante_calificaciones_total']
        self.description = [(c,) for c in columnas]
        self._filas = [(7, 4, 'Sofía Estudiante', 'PENDIENTE', None,
                        'Universidad San Sebastián', 'Enfermería', 3, 'VERIFICADO',
                        4.5, 2)]

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



def test_promedio_real_sqlserver_filtrado_por_estudiante_y_sentido():
    cursor = CursorFalso()
    postulantes = repo.postulaciones_solicitud(cursor, 12)
    ficha = postulantes[0]
    assert ficha['estudiante_calificacion_promedio'] == 4.5
    assert ficha['estudiante_calificaciones_total'] == 2
    sql = cursor.sql
    assert 'OUTER APPLY' in sql
    assert 'AVG(CAST(c.puntaje AS float))' in sql
    assert 'COUNT(*) AS total' in sql
    assert 'c.id_evaluado = p.id_universitario' in sql
    assert "c.tipo = 'ADULTO_A_UNIVERSITARIO'" in sql
    assert cursor.parametros == (12,)


def test_promedio_postgres_calculado_en_consulta_sin_datos_privados():
    cursor = CursorFalso()
    ficha = postgres_repo.postulaciones_solicitud(cursor, 12)[0]
    assert ficha['estudiante_calificacion_promedio'] == 4.5
    assert ficha['estudiante_calificaciones_total'] == 2
    sql = cursor.sql
    assert 'LEFT JOIN LATERAL' in sql
    assert 'ROUND(AVG(c.puntaje)::numeric, 1)' in sql
    assert 'COUNT(*)::integer AS total' in sql
    assert 'c.id_evaluado = p.id_universitario' in sql
    assert "c.tipo = 'ADULTO_A_UNIVERSITARIO'" in sql
    assert cursor.parametros == (12,)
    for dato in ('correo', 'email', 'telefono', 'rut', 'password', 'contacto_emergencia'):
        assert dato not in sql.lower()


def test_sin_evaluaciones_conserva_nota_nula_y_total_cero():
    cursor = CursorFalso()
    cursor._filas = [(7, 4, 'Sofía Estudiante', 'PENDIENTE', None,
                       'Universidad San Sebastián', 'Enfermería', 3, 'PENDIENTE_VERIFICACION',
                       None, 0)]
    ficha = postgres_repo.postulaciones_solicitud(cursor, 12)[0]
    assert ficha['estudiante_calificacion_promedio'] is None
    assert ficha['estudiante_calificaciones_total'] == 0
