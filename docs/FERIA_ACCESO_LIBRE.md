# Acceso libre para visitantes — Feria Manos Amigas

Este es un **prototipo académico, no un servicio disponible para contratar ayuda**.

## Qué cambia
- En el sitio público de la feria aparecen dos accesos: «Probar como adulto mayor» y «Probar como universitario».
- Cada visita crea un usuario ficticio independiente y abre una sesión inmediatamente, sin correo, contraseña, RUT ni aprobación administrativa.
- La cuenta universitaria ficticia queda con estado técnico `VERIFICADO` para que funcione el recorrido de postulaciones, **sin acreditar realmente identidad ni estudios**.
- Quien elige «Crear cuenta» como universitario registra su correo real (Gmail, Outlook, USS u otro): entra en «Verificación», solicita y confirma el código de seis dígitos y queda habilitado sin administrador.
- El código solo se puede utilizar en su cuenta, vence a los 15 minutos y tiene un máximo de cinco intentos; no se muestra al visitante en pantalla.
- **Importante:** los botones «Probar» no requieren código ni envían correos, porque crean cuentas ficticias independientes.
- La aplicación permite seguir probando solicitudes, postulación, asignación, chat y seguimiento con datos de ejemplo.

## Configuración de la feria
Backend Render `manos-amigas-supabase-test`:
`FERIA_REGISTRO_LIBRE=true`
Solo se aplica con `DB_ENGINE=postgres`. Las verificaciones del administrador siguen desactivadas.

Frontend sitio estático Render `manos-amigas-feria-2026`:
`VITE_MODO_FERIA=true` (variable de compilación).

En otro entorno, ambas variables quedan desactivadas por defecto.

## Para explicar en la feria
Indicar a cada visitante que ingrese a la portada pública y toque «Probar como adulto mayor» o «Probar como universitario». No es necesario rellenar formularios ni pedir autorizaciones al equipo.

Las solicitudes son ficticias. No coordinar visitas reales, no ingresar domicilios verdaderos y no utilizar este prototipo para contratar servicios.

## Requisito para enviar el código por correo
Configurar en Render backend `MAIL_BREVO_API_KEY` y `MAIL_FROM` con un remitente validado por Brevo. Sin esto, «Enviar código» responderá que el correo no está configurado. El equipo puede seguir usando los dos botones de prueba de un clic aunque Brevo no esté activo.

## Al acabar la feria
Poner `FERIA_REGISTRO_LIBRE=false` en el backend y deshabilitar `VITE_MODO_FERIA` al reconstruir el frontend. Los estudiantes nuevos volverán a quedar pendientes de verificación. Las cuentas ficticias creadas previamente deben considerarse datos de prueba y no usarse como identidades verificadas.
