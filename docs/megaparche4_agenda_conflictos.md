# Megaparche 4: agenda y prevención de doble asignación

## Funciones

- `GET /api/agenda/mia`: muestra hasta 100 servicios asignados, en curso o finalizados de los últimos 90 días; incluye compromisos futuros. No muestra nombres, contactos, direcciones, RUT, coordenadas ni descripciones libres de terceros.
- Universitario: solo servicios con postulación **ACEPTADA** propia. Adulto mayor: solo sus solicitudes. Familiar: solo solicitudes de adultos mayores con vínculo **activo** y cuenta adulta activa.
- Pestaña **Agenda** en los tres dashboards; sección de compromisos vigentes y servicios finalizados recientes.
- Al aceptar una postulación, el backend bloquea la fila del universitario para serializar aceptaciones simultáneas y comprueba si ya tiene una asignación **ASIGNADA** o **EN_CURSO** con horario solapado. En conflicto se devuelve HTTP **409** sin asignar el servicio, sin rechazar otros postulantes y sin avisos de asignación; la transacción se revierte.
- Dos servicios que se tocan justo en el límite de horario, por ejemplo 09:00–10:00 y 10:00–11:00, se permiten (intervalos semiabiertos).
- La disponibilidad semanal del Megaparche 3 continúa siendo **informativa**: la comprobación nueva solo impide solapamientos entre asignaciones ya aceptadas, no obliga a declarar franjas.

## Instalación SQL Server

En SSMS, respaldar `ManosAmigas`. Ejecutar **solo** `database/13_indice_agenda_conflictos.sql`. Es aditivo, idempotente y no cambia datos. Las consultas de agenda y la regla de conflicto funcionarán sin el índice, pero se recomienda aplicarlo antes de las pruebas manuales.

## Verificación

1. En rama `feature/mega-agenda-conflictos`, ejecutar `python instalar_mega4.py`.
2. Ejecutar `backend/.venv/Scripts/python.exe -m pytest -q`, `npm run build`, `npm run lint` y confirmar `GET /api/agenda/mia` sin token devuelve 401 (no 404).
3. Verificar que Juan Pedro y la cuenta adulta/familiar autorizada vean el mismo servicio asignado, sin datos privados adicionales.
4. Preparar **dos solicitudes ficticias** para el mismo estudiante: A lunes 09:00–11:00 y B lunes 10:00–12:00 en una fecha futura. Aceptar A, luego intentar aceptar B. B debe responder 409 y conservarse PENDIENTE.
5. Crear C lunes 11:00–12:00 y asignarlo al mismo estudiante: se permite si ninguna otra asignación lo cruza.
6. Una cuenta familiar sin vínculo activo y otro universitario no pueden ver servicios ajenos en `/api/agenda/mia`.
7. Verificar que se conserva la disponibilidad del Megaparche 3 y que los avisos se generan solo cuando la aceptación tuvo éxito.

**Límites:** el MVP usa la hora local del servidor y no maneja tiempos de viaje ni traslado entre servicios. No se generan recordatorios push, no se reasignan estudiantes automáticamente y no se ejecutan tareas en segundo plano. Los servicios cancelados no aparecen en esta agenda (permanecen en las pantallas previas/avisos).
