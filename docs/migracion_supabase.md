# Migración en desarrollo: SQL Server → Supabase PostgreSQL

Arquitectura objetivo:
- GitHub: código fuente.
- Vercel: frontend React/Vite (sin cambios en esta etapa).
- Render: backend Flask (mantener la versión actual hasta completar pruebas).
- Supabase: PostgreSQL; conexión desde Render por **Session pooler IPv4**.

## Estado comprobado en Supabase
- 20 tablas, 30 claves foráneas, 20 claves primarias, 21 restricciones CHECK y 12 UNIQUE.
- RLS habilitado en las 20 tablas (verificar también las políticas y privilegios).
- Roles (4) y Servicios (13) cargados; datos de usuarios y operaciones aún pendientes.
- Evitar exponer la conexión PostgreSQL al frontend, así como publicar secretos en GitHub.

## Adaptaciones técnicas pendientes
1. Revisar integridad del esquema exportado (columnas, defaults, índices parciales, permisos y triggers).
2. Migrar consultas de backend: placeholders `?` → `%s`; `dbo.Tabla` → `public."Tabla"` (identificadores sensibles a mayúsculas); `TOP` → `LIMIT`; `OUTPUT INSERTED` → `RETURNING`; `SYSDATETIME()`/`SYSUTCDATETIME()` → expresiones PostgreSQL; hints de bloqueo `WITH (UPDLOCK, HOLDLOCK)` → bloqueos transaccionales `FOR UPDATE` cuando corresponda; `bit` → boolean.
3. Adaptar tratamiento de filas y excepciones pyodbc en servicios y repositorios. Probar registro/login, autorizaciones, solicitudes, postulaciones y el resto de endpoints.
4. Migrar datos de prueba a través de un proceso local y seguro, manteniendo IDs y secuencias; no subir RUT, correos, hashes ni credenciales al repositorio.
5. Configurar `DATABASE_URL` en Render como secreto (Session pooler / URI, contraseña URL-encoded cuando corresponda), CORS permitido a la URL exacta de Vercel y HTTPS.
6. Probar primero en un despliegue de prueba; sólo después evaluar integrar a main.

`backend/database/postgres_connection.py` es una utilidad **aislada e inactiva**; no cambiar `database/connection.py` ni el despliegue de Render hasta adaptar las consultas.

Para habilitarla en un entorno de prueba se requerirá la dependencia `psycopg[binary]` en ese entorno. No se configura aún en producción.
