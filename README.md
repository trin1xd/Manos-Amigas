# Manos Amigas

Prototipo de **Manos Amigas**: plataforma que conecta adultos mayores (y sus familiares) con universitarios que ofrecen ayuda cotidiana.

## Tecnologías

- **Frontend:** React + Vite
- **Backend:** Python + Flask (API REST en `/api`)
- **Base de datos:** SQL Server
- **Acceso a SQL Server:** pyodbc
- **Administración de BD:** SQL Server Management Studio 22 (SSMS)

## Estructura

```text
manos-amigas/
├── frontend/                 # Aplicación React
│   └── src/ (components, pages, services, hooks, utils, assets)
├── backend/                  # API Flask
│   ├── app.py
│   ├── config.py
│   ├── database/connection.py        # conexión pyodbc
│   ├── routes/auth_routes.py         # HTTP: request / response
│   ├── services/auth_service.py      # reglas de negocio
│   ├── repositories/user_repository.py  # consultas SQL parametrizadas
│   ├── utils/ (rut.py, validators.py)
│   └── tests/
├── database/                 # Scripts SQL numerados
└── docs/                     # api.md, modelo-base-datos.md, arquitectura.md
```

## 1. Preparar la base de datos

En SSMS 22, conectarse a tu instancia y ejecutar **en este orden** (abrir cada archivo y presionar *Execute*):

1. `database/01_crear_base_datos.sql` — crea la base `ManosAmigas`
2. `database/02_crear_tablas.sql` — tablas
3. `database/03_restricciones.sql` — UNIQUE, FOREIGN KEY, CHECK
4. `database/04_datos_iniciales.sql` — roles (`ADULTO_MAYOR`, `UNIVERSITARIO`, `FAMILIAR`) y datos base
5. `database/05_verificar_instalacion.sql` — comprobación

Los scripts se pueden re-ejecutar sin errores. Si ya habías creado el esquema inicial anterior (con `Usuarios.nombre/apellido`), borra la base primero:

```sql
USE master;
ALTER DATABASE ManosAmigas SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE ManosAmigas;
```

> Requiere además tener instalado el **ODBC Driver 18 for SQL Server** en el equipo donde corre Flask.

## 2. Configurar y levantar el backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Editar `backend/.env` con tus datos (nunca se sube al repositorio):

```env
SECRET_KEY=una-clave-larga-y-aleatoria
DB_SERVER=localhost            # o localhost\SQLEXPRESS
DB_NAME=ManosAmigas
DB_USER=sa
DB_PASSWORD=tu_password
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUSTED_CONNECTION=false    # true = autenticación de Windows (ignora DB_USER/DB_PASSWORD)
DB_TRUST_SERVER_CERTIFICATE=true
CORS_ORIGINS=http://localhost:5173
```

Levantar la API:

```powershell
python app.py
```

Comprobación: `GET http://localhost:5000/api/health`

Pruebas (no necesitan SQL Server, usan una base en memoria):

```powershell
python -m pytest
```

## 3. Levantar el frontend

```bash
cd frontend
npm install
npm run dev
```

Vite usa `http://localhost:5173`.

## Roles y estados

| Rol (`Roles.nombre`) | Perfil |
|---|---|
| `ADULTO_MAYOR` | `PerfilAdultoMayor` |
| `UNIVERSITARIO` | `PerfilUniversitario` |
| `FAMILIAR` | `PerfilFamiliar` |

- Estado de cuenta (`Usuarios.estado`): `ACTIVO`, `BLOQUEADO`, `DESACTIVADO`.
- Estado del universitario (`PerfilUniversitario.estado_verificacion`): `PENDIENTE_VERIFICACION` (al registrarse), `VERIFICADO`, `RECHAZADO`, `SUSPENDIDO`.

El rol es único por cuenta y no se puede cambiar desde la API.

## Estado actual

- Implementado: registro por perfil, login básico, persistencia en SQL Server, rol en la respuesta del login, JWT, GET /auth/me y protección por rol.
- El frontend aún no está conectado a estos endpoints (el diseño visual no se modificó).
- Pendiente a propósito: subida de documentos, verificación de universitarios y de correo institucional, asociación familiar ↔ adulto mayor, servicios, solicitudes, pagos, chat, SOS, notificaciones.

## Documentación

- `docs/api.md` — endpoints, ejemplos, JWT futuro
- `docs/modelo-base-datos.md` — tablas y relaciones
- `docs/arquitectura.md`
- `docs/guia-antigravity.md`
