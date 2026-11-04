"""Alta LOCAL de una cuenta ADMIN de pruebas, nunca desde una ruta HTTP.

Uso: ejecutar el script desde la carpeta backend con su entorno virtual activo.
"""
import argparse
from getpass import getpass
import os
from pathlib import Path
import re
import secrets
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database.connection import get_connection  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description='Crear administrador SOLO de pruebas')
    parser.add_argument('--confirmo-entorno-local', action='store_true')
    args = parser.parse_args()
    if not args.confirmo_entorno_local or os.getenv('ADMIN_VERIFICACION_PRUEBAS', '').lower() != 'true':
        raise SystemExit('Activa ADMIN_VERIFICACION_PRUEBAS=true en backend/.env y confirma el entorno local.')
    print('Cuenta administrativa de PRUEBAS. No valida identidades reales.')
    if input('Escribe CONFIRMO para continuar: ').strip() != 'CONFIRMO':
        raise SystemExit('Operación cancelada.')
    nombre = input('Nombre del administrador de pruebas: ').strip()
    email = input('Correo del administrador de pruebas: ').strip().lower()
    if not (2 <= len(nombre) <= 150 and len(email) <= 255 and re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email)):
        raise SystemExit('Nombre o correo inválido.')
    clave = getpass('Contraseña nueva (mínimo 12 caracteres): ')
    confirmar = getpass('Repite la contraseña: ')
    if len(clave) < 12 or len(clave) > 128 or clave != confirmar:
        raise SystemExit('Las contraseñas no coinciden o no cumplen el largo requerido.')

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_rol FROM dbo.Roles WHERE nombre = 'ADMIN'")
        fila = cursor.fetchone()
        if not fila:
            raise SystemExit('Falta ejecutar database/07_verificacion_admin_demo.sql en SSMS.')
        rol = fila[0]
        cursor.execute('SELECT 1 FROM dbo.Usuarios WHERE email = ?', (email,))
        if cursor.fetchone():
            raise SystemExit('Ya existe una cuenta con ese correo. No se modificó.')
        identificador = 'ADM' + secrets.token_hex(5).upper()[:9]  # reservado, <= 12 caracteres
        cursor.execute('''
            INSERT INTO dbo.Usuarios
              (nombre_completo, rut, email, telefono, fecha_nacimiento, password_hash, id_rol)
            VALUES (?, ?, ?, ?, NULL, ?, ?)
        ''', (nombre, identificador, email, 'NO_APLICA', generate_password_hash(clave), rol))
        conn.commit()
        print('Administrador de pruebas creado. Usa su correo y contraseña para iniciar sesión.')
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
