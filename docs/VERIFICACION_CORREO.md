# Envío de correos institucionales — Manos Amigas

El formulario ya crea un código de seis dígitos, almacenado como HMAC, válido 15 minutos y sujeto a límites de frecuencia e intentos. **Sin proveedor de correo no puede enviarlo.**

## Compatibilidad con Render gratuito

Render bloquea SMTP saliente en puertos 25, 465 y 587 para servicios gratuitos. El backend ahora admite **Brevo Transactional Email por HTTPS** usando la API oficial, manteniendo SMTP como alternativa para otros alojamientos.

## Activación (solo un responsable con acceso a Render)

1. Crear cuenta Brevo del proyecto y verificar un remitente que realmente les pertenezca, siguiendo los requisitos de Brevo.
2. Generar una API key para correos transaccionales; nunca pegarla en GitHub ni en un chat.
3. En **Render → manos-amigas-supabase-test → Environment**, configurar:
   - `MAIL_BREVO_API_KEY`: secreto generado por Brevo.
   - `MAIL_FROM`: correo remitente verificado en Brevo.
   - `MAIL_FROM_NAME`: `Manos Amigas` (opcional).
   - `MAIL_FRONTEND_URL`: `https://manos-amigas-feria-2026.onrender.com` (para enlaces de recuperación).
4. Esperar despliegue de Render; iniciar sesión con universitario ficticio cuyo correo **institucional sea auténtico y accesible por su titular**. Abrir **Verificación → Enviar código**, revisar correo y confirmar los seis dígitos.
5. Comprobar que el estado indica `correo_confirmado: true`. **No implica** cuenta administrativamente verificada, matrícula validada ni identidad comprobada.

## Seguridad

- Solo el servidor maneja la API key.
- Los códigos no se muestran en la pantalla ni en los logs del servidor.
- Si el proveedor todavía no está activado, las solicitudes deben fallar de forma segura; no se debe simular que un correo se entregó.
- Los códigos emitidos sin entrega real se invalidan.
- Las habilitaciones administrativas de prueba se mantienen desactivadas.
- Usar únicamente correos de prueba propios con autorización, nunca credenciales de terceros.

## Qué demostrar si no se configura el proveedor

Mostrar el formulario y explicar que el envío externo requiere un remitente validado. No afirmar que el correo se envió si el sistema responde que el envío no está configurado.


## Verificación por código como única aprobación DURANTE LA FERIA

Con `FERIA_REGISTRO_LIBRE=true` y `DB_ENGINE=postgres`:

- Los visitantes que elijan los botones **«Probar»** siguen usando cuentas ficticias y no necesitan correo ni código.
- Los visitantes que prefieran **registrarse como universitarios** pueden ingresar su correo personal (Gmail, Outlook, USS, etc.) y lo confirman en su propio panel **Verificación**.
- El backend genera un número aleatorio de **6 dígitos**, guarda únicamente un HMAC vinculado al usuario y envía el número por Brevo.
- Al recibir el número, el estudiante lo escribe: el servidor compara el HMAC, comprueba vigencia de **15 minutos**, máximo **5 intentos**, máximo **5 códigos/día** y un intervalo de **90 segundos** entre envíos.
- Si coincide, cambia en una sola transacción el correo a confirmado y el estado del estudiante a `VERIFICADO`. Ya puede postular sin pasar por un administrador.
- **Fuera del modo feria**, permanece el correo `@correo.uss.cl` y la revisión administrativa original.
- No equivale a una comprobación real de identidad o matrícula; es un acceso para la feria académica.

**Atención:** mientras no exista un remitente Brevo y una API key configurados en Render, el backend tiene las rutas implementadas pero NO entrega códigos reales. Nunca colocar API keys en el repositorio o enviarlas por chat.
