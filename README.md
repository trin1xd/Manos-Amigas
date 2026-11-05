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
6. `database/06_operacion_solicitudes.sql` — solicitudes, postulaciones y vínculos
7. `database/07_verificacion_admin_demo.sql` — rol ADMIN y auditoría de pruebas

**Importante:** en una base que ya contiene datos, NO borres ni recrees la base. Haz una copia de seguridad antes de cualquier migración. Las migraciones 06 y 07 son aditivas. Para revisar la base actual ejecuta `database/utilidades/diagnostico_mvp_solo_lectura.sql` (solo consultas SELECT).

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
JWT_SECRET_KEY=otra-clave-larga-y-aleatoria
FLASK_HOST=127.0.0.1
FLASK_DEBUG=false
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
| `ADMIN` | Administración local de pruebas; sin registro público |

- Estado de cuenta (`Usuarios.estado`): `ACTIVO`, `BLOQUEADO`, `DESACTIVADO`.
- Estado del universitario (`PerfilUniversitario.estado_verificacion`): `PENDIENTE_VERIFICACION` (al registrarse), `VERIFICADO`, `RECHAZADO`, `SUSPENDIDO`.

El rol es único por cuenta y no se puede cambiar desde la API.

## Estado actual

- **Operativo en el MVP:** registro por perfil, login y JWT, solicitudes del adulto mayor/familiar, postulaciones de universitarios habilitados, aceptación/cancelación y relación familiar autorizada. El frontend React consume la API Flask con datos de SQL Server.
- **ADMIN solo para pruebas:** permite aprobar o rechazar cuentas ficticias y registrar auditoría. NO verifica identidad, documentos, antecedentes ni correo institucional real.
- **Aún pendiente:** llegada/inicio/finalización de servicios, historial, notificaciones, pagos, chat, SOS, calificaciones, recuperación de contraseña y verificación real.
- **Estabilización:** ver `docs/estabilizacion_mvp.md`; revisar SQL sin modificar datos con `database/utilidades/diagnostico_mvp_solo_lectura.sql`.
- **Flask:** `python app.py` escucha solo en localhost y usa debug desactivado por defecto. Para probar el panel ADMIN localmente, activar temporalmente `FLASK_DEBUG=true` y `ADMIN_VERIFICACION_PRUEBAS=true` solo en `.env` privado y reiniciar Flask. Nunca exponer debug a la red.

## Documentación

- `docs/api.md` — endpoints, ejemplos, JWT futuro
- `docs/modelo-base-datos.md` — tablas y relaciones
- `docs/arquitectura.md`
- `docs/guia-antigravity.md`
