# Manos Amigas · revisión de universitarios (solo desarrollo local)

Este parche **no verifica identidades reales**. Permite habilitar estudiantes ficticios para probar el flujo de postulaciones. No admite subir cédulas, certificados de antecedentes, selfies ni documentación sensible. No utilizar en producción ni con servicios reales.

## Instalación

1. Crea la rama `feature/verificacion-universitarios` desde `main` actualizado y comprueba `git status`.
2. Extrae el ZIP en la raíz y ejecuta `python instalar_verificacion_admin.py`.
3. Haz respaldo de `ManosAmigas` y ejecuta en **SSMS 22** `database/07_verificacion_admin_demo.sql` usando la BD ManosAmigas. No vuelvas a ejecutar migraciones antiguas.
4. En **`backend/.env`**, agrega `ADMIN_VERIFICACION_PRUEBAS=true` **solo en la computadora local de pruebas**. No lo actives en producción. `.env` no debe subirse a GitHub.
5. Desde `backend`, crea una cuenta administrativa usando **solo una cuenta de prueba**:

   ```powershell
   cd C:\Users\pc\Desktop\manos-amigas-nuevo\backend
   .\.venv\Scripts\python.exe scripts\crear_admin_pruebas.py --confirmo-entorno-local
   ```

   Sigue las indicaciones de la terminal; la contraseña se solicita sin mostrarla. Debe tener al menos 12 caracteres. La cuenta ADMIN no dispone de formulario de registro público. El comando crea un identificador administrativo reservado para cumplir el esquema existente; no es un RUT de persona.
6. Reinicia Flask y Vite. Inicia sesión en `http://localhost:5173` con el correo y clave del administrador. Aparecerá el panel de revisión de estudiantes.
7. Usa un estudiante ficticio en estado `PENDIENTE_VERIFICACION`. Anota una observación de al menos 12 caracteres; para aprobar debes marcar que la habilitación es solo para pruebas. Confirma. Actualiza la lista. Cierra sesión como estudiante y vuelve a entrar para refrescar su estado.

## Rutas nuevas

- `GET /api/admin/universitarios` — solo ADMIN, devuelve la lista de universitarios activos sin RUT ni teléfono.
- `POST /api/admin/universitarios/{id}/decision` — solo ADMIN y solo cuando `ADMIN_VERIFICACION_PRUEBAS=true` **y Flask esté en modo debug/test**. Acepta:

  ```json
  {"accion":"APROBAR", "observacion":"Habilitación ficticia para probar postulaciones", "confirmacion_pruebas":true}
  ```

  O una decisión `RECHAZAR` con observación. Solo puede decidirse desde `PENDIENTE_VERIFICACION`. Una cuenta ya decidida responde 409.

Las decisiones quedan registradas en `dbo.AuditoriaVerificaciones`, con usuario administrador y fecha UTC. El rol ADMIN se consulta en SQL Server en cada petición mediante el decorador existente, no se confía solamente en el JWT.

## Pruebas

```powershell
cd C:\Users\pc\Desktop\manos-amigas-nuevo\backend
.\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm run build
npm run lint
```

Consulta opcional de auditoría en SSMS:

```sql
USE ManosAmigas;
GO
SELECT TOP 15 id_auditoria, id_universitario, id_administrador,
       estado_anterior, estado_nuevo, observacion, fecha_revision_utc
FROM dbo.AuditoriaVerificaciones ORDER BY id_auditoria DESC;
```

## Límites críticos

- Esta aprobación no valida identidad ni documentos. No debe usarse para autorizar servicios reales. Para ello se necesitan flujos de revisión humana con documentación protegida, almacenamiento privado, políticas de retención y auditoría.
- Las contraseñas del administrador nunca se pasan por argumentos de terminal ni se guardan en texto plano, solo su hash.
- Sin MFA, rate limiting y despliegue seguro, el panel NO es apto para producción.
- No pongas contraseñas, tokens ni `.env` en GitHub ni en capturas.
- `AdminVerificaciones.jsx` no modifica dashboards del universitario, familiar o adulto mayor.
- El flag `ADMIN_VERIFICACION_PRUEBAS` debe desactivarse tras las pruebas.
