# Manos Amigas — Megaparche 2: Chat por servicio + recuperación de contraseña

Base: `main` con PR #15 fusionado. Nueva rama `feature/mega-chat-recuperacion`.

## Instalación

1. **Respaldar** SQL Server (`ManosAmigas`) y conservar respaldo de Git. No borrar datos.
2. Crear rama desde main actualizado y ejecutar `python instalar_mega_chat_recuperacion.py`.
3. En SSMS ejecutar `database/11_chat_recuperacion.sql` tras respaldo **antes de reiniciar Flask** (añade `Usuarios.password_version`). **No** requiere migración 09.
4. Reiniciar un único servidor Flask (evitar instancias antiguas en el puerto 5000). Probar:
   - `GET /api/chat/conversaciones` sin token -> 401.
   - `POST /api/auth/recuperacion/solicitar` con un JSON válido -> 200 genérico, sin revelar si la cuenta existe.
5. Ejecutar `backend/.venv/Scripts/python.exe -m pytest -q` y `npm run build` / `npm run lint` dentro de frontend.

## Chat

- `GET /api/chat/conversaciones`: servicios asignados, en curso o finalizados, solo para participantes autenticados.
- `GET /api/chat/solicitudes/<id>/mensajes`: últimos 80 mensajes en orden cronológico.
- `POST /api/chat/solicitudes/<id>/mensajes` con `{ "mensaje": "..." }`.
- Solo estudiante aceptado, adulto titular o familiar con vínculo **actualmente vigente**. No hay chat con estudiantes desconocidos.
- Escritura limitada a `ASIGNADA` / `EN_CURSO`, máx. 500 caracteres, anti-ráfagas de 3 segundos por remitente y solicitud.
- Servicios finalizados mantienen el historial de lectura pero no admiten mensajes nuevos.
- El frontend actualiza mensajes cada 8 segundos mientras la pestaña permanece abierta; no hay WebSockets, push, imágenes ni adjuntos.
- No compartir datos sensibles. **No es un canal de emergencia.** El administrador debe definir retención de mensajes, reportes de abuso y moderación antes de un despliegue público.

## Recuperación de contraseña por correo

Configurar las siguientes variables **solo en `backend/.env`**, que nunca debe subirse a GitHub:

```dotenv
MAIL_SMTP_HOST=smtp.ejemplo.com
MAIL_SMTP_PORT=465
MAIL_SMTP_MODE=SSL
MAIL_SMTP_USER=cuenta@ejemplo.com
MAIL_SMTP_PASSWORD=CLAVE_DE_APLICACION_DEL_PROVEEDOR
MAIL_FROM=cuenta@ejemplo.com
MAIL_FRONTEND_URL=http://localhost:5173
```

Para servidores puerto 587 usar `MAIL_SMTP_MODE=STARTTLS` y puerto `587`. En despliegue real `MAIL_FRONTEND_URL` debe ser HTTPS. Configura únicamente tu proveedor autorizado; nunca incluyas claves reales en capturas o commits.

- `POST /api/auth/recuperacion/solicitar`: cuerpo `{ "email": "..." }`. Respuesta genérica para evitar enumeración de cuentas.
- `POST /api/auth/recuperacion/confirmar`: cuerpo `{ "token": "...", "password": "..." }`.
- Token aleatorio de 256 bits, solo hash SHA-256 en SQL Server, 20 minutos de vigencia, un solo uso y límite de un envío por cuenta cada 5 minutos. La migración crea `password_version` para invalidar los JWT previos al cambio.
- Si SMTP no está configurado, no se envían correos y **no** se exponen tokens de prueba: la recuperación no está operativa hasta configurarlo.
- Verificar la recepción del correo con cuenta ficticia, la expiración, un intento doble y el ingreso con la nueva contraseña.

### Límites importantes de seguridad antes de producción

- Al recuperar contraseña aumenta `Usuarios.password_version`; los JWT emitidos antes del cambio quedan rechazados por las rutas autenticadas. Volver a iniciar sesión tras la recuperación. Antes de producción conviene añadir revocación explícita de otras causas (robo de dispositivo, cierre de todas las sesiones).
- Se necesita protección anti-abuso por IP en el proxy/API, auditoría de envíos, políticas de privacidad, borrado/retención y TLS de toda la aplicación.
- No utilizar SMTP de prueba ni el enlace HTTP de localhost en producción.

## Subir a Git

Subir solo archivos funcionales dentro de `backend/`, `database/`, `frontend/`, `docs/`.
**Nunca** subir `instalar_mega_chat_recuperacion.py`, `mega2/`, `RESPALDO_MEGA2_CHAT_RECUPERACION/`, archivos `.env` ni otros instaladores anteriores.
