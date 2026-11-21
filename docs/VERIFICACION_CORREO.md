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
- Los códigos emitidos sin entrega real se invalidan.
- Las habilitaciones administrativas de prueba se mantienen desactivadas.
- Usar únicamente correos de prueba propios con autorización, nunca credenciales de terceros.

## Qué demostrar si no se configura el proveedor

Mostrar el formulario y explicar que el envío externo requiere un remitente validado. No afirmar que el correo se envió si el sistema responde que el envío no está configurado.
