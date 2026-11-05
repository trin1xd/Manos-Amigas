# Megaparche: calificaciones + accesibilidad (prototipo académico)

## Qué incluye

- Calificación de 1 a 5 estrellas con comentario opcional de hasta 300 caracteres.
- Solo se habilita tras el estado FINALIZADA y confirmación del servicio.
- El universitario evalúa al adulto mayor; el adulto o familiar con autorización vigente evalúan al universitario. Adulto/familiar comparten un único cupo de evaluación por servicio.
- Listado privado de servicios propios finalizados, con evaluación dada y recibida. Sin RUT, correos, teléfonos ni dirección.
- Preferencias persistentes para texto ampliado, contraste y reducción de animaciones en todas las pantallas; control accesible en la esquina inferior izquierda.

## Seguridad y límites

- El backend verifica JWT y rol vigente; también comprueba la pertenencia al servicio y los vínculos activos.
- El servidor deriva la persona evaluada: la interfaz nunca envía su ID.
- Un índice único SQL evita dobles evaluaciones del mismo sentido.
- No se modera automáticamente el lenguaje de los comentarios; usen cuentas ficticias y no incluyan datos privados.
- La interfaz todavía no es una auditoría de accesibilidad WCAG completa ni el alto contraste garantiza compatibilidad con todos los lectores de pantalla. Los ajustes requieren evaluación humana.
- No se incorporan aquí verificación real de documentos, recuperación por correo, chat, SOS ni pagos. Esas partes requieren diseño independiente.

## Instalación

1. Crear rama desde main: `git switch main`, `git pull --ff-only origin main`, `git switch -c feature/mega-calificaciones-accesibilidad`.
2. Extraer ZIP en raíz y ejecutar `python instalar_mega_calificaciones.py`.
3. En SSMS crear respaldo de ManosAmigas. Ejecutar **solo** `database/10_calificaciones_servicios.sql` (requiere migración 08; no requiere 09).
4. Reiniciar Flask y React.
5. Backend: `cd backend` y `.\.venv\Scripts\python.exe -m pytest -q`.
6. Frontend: `cd frontend` y `npm run build`, `npm run lint`.
7. Con cuentas de prueba, finalizar y confirmar un servicio; entrar a Calificaciones de cada rol y evaluarlo. Comprobar que no permita un segundo voto del mismo lado, ni de un familiar revocado.
8. Probar texto grande/contraste y reducción de movimiento en inicio de sesión y dashboards.
9. Revisar `git diff --stat` antes de seleccionar los archivos a subir. No usar `git add .`.

Las notificaciones ya entregadas en otro ZIP pueden quedar pendientes: este megaparché no las activa ni las modifica. El número 10 evita reutilizar la migración 09. 
