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


## Envío desde Gmail mediante Google Apps Script (alternativa a Brevo)

No requiere cuenta de Brevo. Solo el Gmail separado que el equipo creó para Manos Amigas.

1. Abre el proyecto en https://script.google.com y sustituye `Código.gs` por el contenido de `integraciones/apps-script/Code.gs`. Guarda los cambios.
2. Ejecuta la función `prepararConexion` exactamente **una vez**. Autoriza el proyecto (propio) y abre su **Registro de ejecución**. Aparecerá `MAIL_APPS_SCRIPT_SECRET=<clave>`. La clave es privada: **no pegar en chats, GitHub ni código frontend**.
3. En Render, en el servicio **backend** `manos-amigas-supabase-test`, sección Environment, crea `MAIL_APPS_SCRIPT_SECRET` con el valor que imprimió Apps Script (solo la parte posterior al signo igual).
4. En Apps Script, selecciona **Implementar > Nueva implementación > Aplicación web**; ejecuta como **Yo** y concede acceso a **Cualquiera** (es el backend Render quien llama por HTTPS, sin sesión de Google). Completa la autorización si se solicita.
5. Copia la URL de aplicación web que termina en `/exec`, y guárdala en la sección Environment del backend como `MAIL_APPS_SCRIPT_URL`. **No** uses el ID del proyecto ni una URL terminada en `/dev`.
6. Render redeplegará su servicio al cambiar estas variables. Desde el sitio público de la feria, crea una cuenta universitaria usando un correo real (Gmail, Outlook o USS), inicia sesión, abre Verificación, envía el código y confírmalo. Tras confirmar no necesita administración.

El botón **Probar como universitario** sigue creando usuarios ficticios sin verificación. No usa Gmail ni consume cuota.

### Seguridad y cuotas
- La aplicación web ejecuta como la cuenta de Manos Amigas, pero requiere una **firma HMAC-SHA256** por petición antes de usar `MailApp.sendEmail`. La clave se guarda en las propiedades del Apps Script y en variables privadas de Render; nunca en el repositorio ni en el navegador.
- La firma incluye la fecha, el destinatario, el asunto y el cuerpo del correo y se acepta solo durante dos minutos. El script bloquea una repetición accidental de la misma firma.
- El backend valida los códigos de seis dígitos (15 min, máximo 5 intentos), no Apps Script. Apps Script solo entrega mensajes.
- La cuota de Gmail personal está limitada por Google y puede ser inferior a la demanda de una feria concurrida; revisar el valor de `MailApp.getRemainingDailyQuota()`.
- Si cambia el código del script ya publicado, crea una **nueva versión** en `Implementar > Administrar implementaciones` (o realiza una implementación nueva y cambia la URL en Render).
- No ejecutar `prepararConexion` otra vez mientras esté funcionando: hacerlo cambia la clave, por lo que habrá que actualizar Render.
- No escribir ni compartir la clave, los códigos OTP o los enlaces de recuperación en capturas públicas.
- El proveedor Gmail tiene prioridad sobre Brevo y SMTP cuando las dos variables `MAIL_APPS_SCRIPT_*` están definidas.


### Correo USS previamente ocupado en una prueba
En el entorno de feria, los nuevos registros universitarios conservan el correo real
en `Usuarios.email`. El campo histórico `PerfilUniversitario.correo_institucional`
recibe una referencia interna única terminada en `@demo.invalid`, por lo que un
correo USS utilizado como institucional en un perfil anterior no bloquea a la
persona que intenta registrar su dirección real.

Las pantallas de verificación, la comprobación de dominio y el envío del código
utilizan **`Usuarios.email` durante la feria**, nunca esa referencia interna.
Fuera de feria se mantiene la validación institucional original. No se modifica
ni borra ningún perfil anterior, y siguen vigentes los controles de duplicidad
de `Usuarios.email` y RUT.
