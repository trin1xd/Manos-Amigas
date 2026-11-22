# Acceso libre para visitantes — Feria Manos Amigas

Este es un **prototipo académico**, no una plataforma de contratación real.

## Demostración de feria
- «Probar como adulto mayor» y «Probar como universitario» generan sesiones ficticias sin formulario.
- La gente que prefiera crear una cuenta universitaria también puede iniciar sesión y **usar tareas, postulación, asignación y seguimiento sin correo de confirmación ni intervención administrativa**.
- Durante la feria, el estado real de las cuentas nuevas queda como `PENDIENTE_VERIFICACION`. El acceso temporal **NO las marca como verificadas**; solo los perfiles universitarios activos, pendientes o ya verificados, pueden realizar acciones de la demo. Las cuentas rechazadas/suspendidas siguen sin acceso.
- La opción «Verificación» no aparece en el panel universitario. No hay botón para enviar códigos.
- La API de envío y confirmación de códigos devuelve `410` («Función pausada») en feria, incluso para llamadas directas.
- El código de verificación con Apps Script, SMTP, validación de dominios, cuotas y aprobaciones **se conserva íntegramente** para retomarlo en una versión futura.
- En el sitio no se confirma correo, identidad ni matrícula. No usar datos sensibles reales ni coordinar visitas, pagos o servicios reales.

## Activación
La desactivación temporal usa el modo de demostración existente; **no requiere nueva variable**:
- Backend Render `manos-amigas-supabase-test`: `FERIA_REGISTRO_LIBRE=true` y `DB_ENGINE=postgres`.
- Frontend estático Render `manos-amigas-feria-2026`: `VITE_MODO_FERIA=true`, reconstruir frontend después de los cambios.
- Cuando el backend no está en feria, sigue exigiendo verificación institucional y vuelve a habilitar sus rutas de código.
- Cuando el frontend no está en feria, conserva la sección de verificación.

## Después de la feria
Desactivar ambas opciones: `FERIA_REGISTRO_LIBRE=false` en backend y `VITE_MODO_FERIA=false` en frontend, luego reconstruir el sitio estático. Las cuentas pendientes no se convierten en verificadas de forma persistente.
