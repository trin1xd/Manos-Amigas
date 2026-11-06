# Panel del universitario: tareas y postulaciones

Conecta las pestañas **Tareas** y **Mis postulaciones** de `UniversitarioDashboard.jsx` con la API operativa descrita en `docs/operaciones-api.md`.

## Qué hace
- **Tareas**: lista las solicitudes abiertas de adultos mayores y permite postular, con una confirmación en dos pasos.
- **Mis postulaciones**: muestra a qué tareas postuló el universitario y el estado de cada una.
- Si el perfil **no está `VERIFICADO`**, la pestaña Tareas muestra un aviso y **no llama a la API** (el backend respondería 403).
- Las tareas muestran solo `servicio`, `fecha_solicitada` y `duracion_horas`. No se muestran nombre, dirección, teléfono ni descripción privada del adulto mayor.

## Endpoints que usa
| Método | Ruta | Para qué |
|---|---|---|
| GET | `/solicitudes/disponibles` | Listar tareas abiertas |
| POST | `/solicitudes/{id}/postular` | Postular a una tarea |
| GET | `/postulaciones/mias` | Listar mis postulaciones |

Todas pasan por `apiRequest` (`services/api.js`), que adjunta el token de sesión.

## Estados
- Postulación: `PENDIENTE`, `ACEPTADA`, `RECHAZADA`. Cada una lleva símbolo y texto, no solo color.
- Solicitud: `PENDIENTE` (abierta), `ASIGNADA`, `CANCELADA`.
- Cuando una postulación es `ACEPTADA` se muestra un aviso de que la coordinación de contacto se habilitará en una próxima etapa.

## Errores y sesión
- Los mensajes de error del servidor (por ejemplo 409 "Ya postulaste" o "ya no admite postulaciones") se muestran en el panel.
- Si el servidor responde que la sesión está ausente, inválida o vencida (401), se llama a `onLogout`. `apiRequest` solo entrega el mensaje del error, por lo que la detección compara esos mensajes (ver `esErrorDeSesion` en `services/postulacionesService.js`).

## Fechas
El backend entrega `AAAA-MM-DDTHH:MM` en hora local del servidor, sin zona horaria. El navegador lo interpreta como hora local, y la hora mostrada coincide con la guardada.

## Archivos
- `frontend/src/services/postulacionesService.js`
- `frontend/src/pages/Universitario/TareasDisponibles.jsx`
- `frontend/src/pages/Universitario/MisPostulaciones.jsx`
- `frontend/src/pages/Universitario/UniversitarioPaneles.module.css`
- `frontend/src/pages/Universitario/formatoFecha.js`
- `frontend/src/utils/precioReferencial.js` (precio de referencia y pago estimado al estudiante)
- `frontend/src/pages/Universitario/UniversitarioDashboard.jsx` (solo usa los dos componentes y actualiza textos)

## Pago estimado para el estudiante
Cada tarea de 1 a 2 horas muestra «Pago estimado para ti: $3.200 a $6.400»: el rango de referencia de $4.000 a $8.000 menos 20% de comisión (sección 6.1 del informe). Las tareas de más de 2 horas muestran «Por definir». Es una propuesta en validación y no representa un pago real.

## Lo que NO hace todavía
Verificación administrativa de universitarios, subida de documentos, datos de contacto, pagos, chat, SOS, notificaciones, finalizar o valorar tareas.

## Cómo probarlo
1. Ejecutar `database/06_operacion_solicitudes.sql` (con respaldo previo) y arrancar el backend.
2. Como adulto mayor de prueba (por API), crear una solicitud con fecha futura. Ver `docs/operaciones-api.md`.
3. Con el universitario de prueba en `PENDIENTE_VERIFICACION`: la pestaña Tareas debe mostrar el aviso y no hacer llamadas.
4. En una base local de pruebas, marcarlo `VERIFICADO` (SELECT y UPDATE de `docs/operaciones-api.md`), cerrar sesión y volver a entrar.
5. Postular desde Tareas; repetir debe mostrar el mensaje del servidor. Revisar el estado en Mis postulaciones.
6. Como adulto mayor, aceptar la postulación por API y actualizar Mis postulaciones: debe aparecer `ACEPTADA`.
