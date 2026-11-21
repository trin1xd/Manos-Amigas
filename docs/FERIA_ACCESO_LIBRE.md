# Acceso libre para visitantes — Feria Manos Amigas

Este es un **prototipo académico, no un servicio disponible para contratar ayuda**.

## Qué cambia
- En el sitio público de la feria aparecen dos accesos: «Probar como adulto mayor» y «Probar como universitario».
- Cada visita crea un usuario ficticio independiente y abre una sesión inmediatamente, sin correo, contraseña, RUT ni aprobación administrativa.
- La cuenta universitaria ficticia queda con estado técnico `VERIFICADO` para que funcione el recorrido de postulaciones, **sin acreditar realmente identidad ni estudios**.
- Quien elige «Crear cuenta» como universitario también puede registrarse sin correo USS y queda habilitado solo mientras la feria esté activa.
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

Las solicitudes son ficticias. No coordinar visitas reales, no ingresar datos personales y no utilizar este prototipo para contratar servicios.

## Al acabar la feria
Poner `FERIA_REGISTRO_LIBRE=false` en el backend y deshabilitar `VITE_MODO_FERIA` al reconstruir el frontend. Los estudiantes nuevos volverán a quedar pendientes de verificación. Las cuentas ficticias creadas previamente deben considerarse datos de prueba y no usarse como identidades verificadas.
