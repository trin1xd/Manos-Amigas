# Megaparche 5 (alcance reducido) — SOLO correo institucional

## Objetivo

Permitir que un UNIVERSITARIO con estado PENDIENTE_VERIFICACION confirme que controla el correo institucional que declaró en el registro, sin adjuntar documentos ni certificar identidad.

- Código de 6 dígitos enviado mediante SMTP TLS/SSL, no visible en API ni logs.
- Validez de 15 minutos; 5 intentos por código, 5 envíos por día y 90 segundos entre envíos; HMAC SHA-256 usando JWT_SECRET_KEY; hash en SQL Server.
- Solo se permite el dominio exacto `@correo.uss.cl` para estudiantes universitarios, tanto al registrarse como al solicitar un código. No se aceptan subdominios ni otros dominios. La restricción se aplica en el backend, no solo en el formulario.
- Registro SQL: `dbo.CodigosCorreoInstitucional`, `dbo.AuditoriaVerificacionInstitucional` y campo existente `PerfilUniversitario.correo_institucional_verificado`.
- API protegida con JWT/rol: GET `/api/verificacion-institucional/mia`, POST `/api/verificacion-institucional/enviar-codigo`, POST `/api/verificacion-institucional/confirmar-codigo` JSON `{ "codigo": "012345" }`.
- Panel de universitario: nueva pestaña Verificación. El panel ADMIN existente muestra si el correo está confirmado. No hay carga ni descarga de documentos.
- Por defecto `VERIFICACION_CORREO_OBLIGATORIA=true`: el ADMIN de pruebas NO podrá aprobar una cuenta nueva sin correo confirmado; no afecta cuentas ya aprobadas. Poner a `false` únicamente si se necesita el comportamiento legado con datos ficticios, no para presentación de control real.
- Confirmar correo NO es verificar identidad, matrícula ni antecedentes, ni habilita postulaciones automáticamente. Las aprobaciones del panel ADMIN continúan siendo únicamente para pruebas locales.
- Usuarios previamente registrados con otro dominio no se modifican ni eliminan; no podrán solicitar código hasta que un procedimiento seguro actualice su correo o registren una cuenta de prueba válida. No edites emails directamente en SQL Server sin control de duplicados y auditoría.

## Antes de instalar

1. En PowerShell, desde la raíz, ejecutar `git status`; conservar o confirmar cambios previos. No usar `git add .`.
2. `git switch main`; `git pull --ff-only origin main`; verificar SHA `9a1ae8c` o posterior que contenga PR #19 y #20.
3. `git switch -c feature/mega-verificacion-correo` (si ya existe, `git switch feature/mega-verificacion-correo`, actualizar manualmente desde main si corresponde).
4. Extraer ZIP completo en raíz del repositorio. Ejecutar `python instalar_mega5_correo.py`.
5. Respaldar SQL Server y ejecutar `database/14_confirmacion_correo_institucional.sql` en SSMS, contra `ManosAmigas`. No volver a ejecutar 01–13. Migración aditiva; evita borrar datos.

## backend/.env (privado, NO publicar)

```
VERIFICACION_CORREO_OBLIGATORIA=true
MAIL_SMTP_HOST=smtp.proveedor.cl
MAIL_SMTP_PORT=465
MAIL_SMTP_MODE=SSL
MAIL_SMTP_USER=cuenta-smtp
MAIL_SMTP_PASSWORD=secreto-privado
MAIL_FROM=verificacion@tu-proveedor.cl
```

El dominio permitido para estudiantes es fijo: `@correo.uss.cl` (no requiere una variable de entorno). Los parámetros SMTP son ejemplos y requieren credenciales reales y privadas. Para STARTTLS usar puerto apropiado, normalmente 587. No enviar códigos de verificación a correos personales o inventados. Si SMTP no está listo, el endpoint responde 503 sin generar un código de prueba expuesto.

## Ejecutar y verificar

- Backend: `cd backend`; `./.venv/Scripts/python.exe -m pytest -q` en PowerShell.
- Frontend: `cd frontend`; `npm run build`; `npm run lint`.
- Reiniciar Flask (puerto 5001 si se utiliza) y Vite (VITE_API_URL apuntando al mismo puerto).
- Sin token: `/api/verificacion-institucional/mia` responde 401. Con un estudiante pendiente y correo `@correo.uss.cl`: consultar estado, recibir código por correo, probar código incorrecto, confirmar código correcto, recargar y ver `correo_confirmado: true`.
- Comprobar que una segunda confirmación no reutiliza el código; en ADMIN (solo pruebas locales) debe verse Correo institucional confirmado: Sí; no aprobar cuentas sin correo confirmado cuando flag true.
- SQL lectura: `SELECT TOP(20) id_universitario, fecha_confirmacion_utc FROM dbo.CodigosCorreoInstitucional ORDER BY id_universitario DESC;` No compartir correos/códigos/secretos.
- El panel ADMIN sigue protegido y solo permite decisiones de prueba con `ADMIN_VERIFICACION_PRUEBAS=true` y Flask debug/testing en localhost. No activar debug en redes públicas ni usar identidad de personas reales en una demo.

## Limitaciones y seguridad

La verificación del correo no reemplaza la verificación de identidad. No se recopilan cédulas, PDFs ni selfies. No tiene pagos reales, SOS ni aprobación institucional automática. Las cuentas existentes aprobadas antes de activar la regla no cambian de estado retroactivamente. La recuperación de contraseña que ya existe puede usar las mismas credenciales SMTP tras configurarla por separado.

## Alcance del commit

Solo 14 rutas: cinco archivos modificados y nueve nuevos (ver ARCHIVOS_GIT_MEGA5_CORREO.txt). No subir instalador, payload duplicado, `backend/.env` ni respaldos.
