# Guía de trabajo con Antigravity

Abrir como proyecto la carpeta raíz `manos-amigas/` para que el entorno pueda ver frontend, backend, base de datos y documentación al mismo tiempo.

## Contexto técnico que debe mantenerse

- Frontend: React + Vite.
- Backend: Python + Flask.
- Base de datos: SQL Server.
- Acceso a datos: `pyodbc` desde el backend.
- Administración de BD: SSMS 22.

## Reglas para cambios asistidos por IA

- No conectar React directamente a SQL Server.
- No agregar Supabase salvo que se tome explícitamente esa decisión de arquitectura.
- No guardar secretos en Git.
- No modificar scripts SQL ya aplicados sin documentar el cambio; preferir scripts nuevos numerados.
- Mantener componentes reutilizables en `components/` y pantallas completas en `pages/`.
- Mantener acceso HTTP en `frontend/src/services/`.
- Mantener rutas Flask en `backend/routes/` y lógica de negocio en `backend/services/`.
