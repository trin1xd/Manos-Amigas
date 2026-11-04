# Integración operativa del dashboard familiar — Manos Amigas

## Alcance

El parche añade un dashboard familiar independiente. No reemplaza el dashboard visual anterior. `instalar_familiar_api.py` modifica únicamente dos referencias en `frontend/src/App.jsx`.

La API ya existe en el backend (no es necesaria otra migración SQL):

- GET `/api/familiares/adultos`: lista vinculaciones activas de la cuenta familiar.
- GET `/api/solicitudes/mias`: solicitudes de adultos vinculados.
- GET `/api/catalogo/servicios`: categorías reales.
- POST `/api/solicitudes`: solicita ayuda para un adulto vinculado. Payload: `id_adulto_mayor`, `id_servicio`, `fecha`, `hora`, `duracion_horas`, `descripcion`.
- GET `/api/solicitudes/{id}/postulaciones`: postulantes autorizados.
- POST `/api/solicitudes/{id}/postulaciones/{id_post}/aceptar`: asigna un postulante.
- POST `/api/solicitudes/{id}/cancelar`: cancela solicitud.

El backend verifica JWT, el rol `FAMILIAR` y la vinculación real de cada adulto; elegir otro ID no concede acceso.

## Prueba manual segura

1. Crea rama desde `main` al día y extrae ZIP en la raíz del proyecto.
2. Ejecuta `python instalar_familiar_api.py` (crea backup fuera del repositorio).
3. Ejecuta `cd frontend; npm run build; npm run lint` y verifica que no haya errores.
4. Arranca Flask en `backend` y Vite en `frontend` en terminales distintas.
5. Inicia sesión como un adulto mayor de pruebas. En **Mi perfil** autoriza el correo de una cuenta con rol FAMILIAR.
6. Inicia sesión como ese familiar. En **Personas a cargo** debe aparecer el adulto vinculado. Comprueba que un familiar sin autorización no lo ve.
7. En **Pedir ayuda**, crea una solicitud con fecha futura y descripción ficticia. Comprueba en **Solicitudes** que persiste al recargar la página.
8. Con estudiante VERIFICADO de pruebas, postula. Regresa al familiar, pulsa **Ver postulantes** y **Aceptar**. Comprueba que el estudiante ve su postulación aceptada.
9. Prueba cancelar otra solicitud pendiente y comprueba que los estados cambian para ambos perfiles.
10. Repite tests del backend `cd backend; .\.venv\Scripts\python.exe -m pytest -q`.

**Nunca uses datos personales reales ni actives estudiantes reales manualmente desde SQL.** Verificaciones manuales con SQL solo pueden hacerse en una base local de pruebas y con cuentas inventadas.

## Límites del MVP

- No implementa aceptación de invitaciones por parte del familiar, mensajes ni notificaciones automáticas.
- No revela teléfonos ni direcciones del adulto; el backend sigue controlando los recursos.
- No realiza pagos, verificaciones documentales ni cierre de servicios.
- Si vence el JWT, la llamada puede mostrar error; se debe iniciar sesión de nuevo. Manejo global de 401 queda como una mejora posterior.
- Si hay cambios simultáneos en `App.jsx`, el instalador detiene su ejecución sin sobreescribirlos.
