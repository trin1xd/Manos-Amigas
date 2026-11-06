"""Validación y gestión de disponibilidad semanal informativa en horario local."""
import re
from database.connection import get_connection
from repositories import disponibilidad_repository as repo
from services.auth_service import ServiceError


def validar(payload):
    if not isinstance(payload, dict) or set(payload) != {'franjas'}:
        raise ServiceError('Se espera únicamente el campo franjas.', 400)
    items = payload['franjas']
    if not isinstance(items, list) or len(items) > 21:
        raise ServiceError('Envía una lista de hasta 21 franjas por semana.', 400)
    grupos = {dia: [] for dia in range(7)}
    limpios = []
    for item in items:
        if not isinstance(item, dict) or set(item) != {'dia_semana', 'hora_inicio', 'hora_fin'}:
            raise ServiceError('Cada franja debe tener día, inicio y fin.', 400)
        dia = item['dia_semana']
        if type(dia) is not int or not 0 <= dia <= 6:
            raise ServiceError('El día debe estar entre 0 (lunes) y 6 (domingo).', 400)
        inicio, fin = item['hora_inicio'], item['hora_fin']
        if not all(isinstance(h, str) and re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', h)
                   for h in (inicio, fin)):
            raise ServiceError('Usa horas válidas HH:MM (24 horas).', 400)
        minutos_i = int(inicio[:2])*60 + int(inicio[3:])
        minutos_f = int(fin[:2])*60 + int(fin[3:])
        if minutos_f - minutos_i < 30:
            raise ServiceError('Cada franja debe durar al menos 30 minutos y terminar el mismo día.', 400)
        grupos[dia].append((minutos_i, minutos_f))
        limpios.append({'dia_semana': dia, 'hora_inicio': inicio, 'hora_fin': fin})
    for franjas in grupos.values():
        orden = sorted(franjas)
        if any(orden[i][0] < orden[i-1][1] for i in range(1, len(orden))):
            raise ServiceError('Hay franjas que se superponen en el mismo día.', 400)
    return sorted(limpios, key=lambda f: (f['dia_semana'], f['hora_inicio']))


def mia(usuario):
    conn = get_connection()
    try:
        return repo.listar(conn.cursor(), usuario['id'])
    finally:
        conn.close()


def guardar(usuario, payload):
    franjas = validar(payload)
    conn = get_connection()
    try:
        repo.reemplazar(conn.cursor(), usuario['id'], franjas)
        conn.commit()
        return franjas
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
