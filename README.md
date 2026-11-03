# Manos Amigas

Repositorio reorganizado del prototipo **Manos Amigas**.

La estructura sigue una separación clara entre interfaz, API, base de datos y documentación para que el proyecto sea fácil de entender, probar y mantener.

## Tecnologías

- **Frontend:** React + Vite
- **Backend:** Python + Flask
- **Base de datos:** SQL Server
- **Acceso a SQL Server:** pyodbc
- **Administración de BD:** SQL Server Management Studio 22
- **Entorno de desarrollo:** puede abrirse la raíz completa en Antigravity

## Estructura

```text
manos-amigas/
├── frontend/               # Aplicación React
│   └── src/
│       ├── components/     # Componentes reutilizables y secciones
│       ├── pages/          # Pantallas completas
│       ├── services/       # Comunicación con la API
│       ├── hooks/
│       ├── utils/
│       └── assets/
├── backend/                # API Flask
│   ├── routes/
│   ├── services/
│   ├── database/
│   └── tests/
├── database/               # Scripts SQL numerados
│   └── utilidades/
├── docs/                   # Arquitectura y documentación técnica
└── README.md
```

## 1. Preparar la base de datos

Abrir SSMS 22 y ejecutar, en este orden:

1. `database/01_crear_base_datos.sql`
2. `database/02_crear_tablas.sql`
3. `database/03_datos_iniciales.sql`
4. `database/04_verificar_instalacion.sql`

El esquema incluido es una **base inicial** y debe ampliarse cuando se definan las reglas completas del proyecto.

## 2. Levantar el backend

```bash
cd backend
python -m venv .venv
```

Activar el entorno virtual e instalar dependencias:

```bash
pip install -r requirements.txt
```

Copiar `.env.example` como `.env` y completar las credenciales locales de SQL Server.

Luego:

```bash
python app.py
```

Comprobación:

```text
GET http://localhost:5000/api/health
```

## 3. Levantar el frontend

```bash
cd frontend
npm install
npm run dev
```

Por defecto Vite utilizará `http://localhost:5173`.

## Estado actual

- Se conserva el prototipo visual existente.
- `Login` y `Registro` están separados como páginas.
- Supabase fue retirado de la arquitectura base.
- La API Flask está preparada para crecer por módulos.
- La autenticación real todavía está marcada como pendiente.
- SQL Server incluye un esquema mínimo inicial, no un modelo definitivo.

## Convenciones

Consultar:

- `docs/arquitectura.md`
- `docs/api.md`
- `docs/modelo-base-datos.md`
- `docs/guia-antigravity.md`
