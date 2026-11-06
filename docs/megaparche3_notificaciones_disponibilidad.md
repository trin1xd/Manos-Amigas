# Megaparche 3: notificaciones internas y disponibilidad semanal

## Alcance

- Bandeja de avisos privada para ADULTO_MAYOR, FAMILIAR y UNIVERSITARIO.
- Postular: se avisa al adulto mayor y familiares vinculados actualmente.
- Aceptar: se avisa al estudiante elegido; los no elegidos reciben aviso de rechazo.
- Cancelar: se avisa a los estudiantes que postularon a la solicitud.
- Llegada, inicio y término: se avisa al adulto mayor y familiares vinculados.
- Confirmación de término: se avisa al estudiante seleccionado.
- Avisos de nuevas acciones, NO retroactivos. Actualización al entrar a la pestaña o pulsar Actualizar; no existe push/SMS/email.
- Los familiares revocados dejan de recibir avisos nuevos; los avisos históricos de su propia cuenta se conservan.
- Disponibilidad del estudiante: franjas semanales recurrentes, días 0-6 (lunes-domingo) y horas HH:MM, máximo 21, mínimo 30 minutos y sin solapamientos.
- La disponibilidad **NO** bloquea automáticamente las postulaciones ni equivale a una reserva confirmada.

## Migraciones (SQL Server Management Studio)

Antes: respaldar la base **ManosAmigas**. Ejecutar los archivos por separado:

1. `database/09_notificaciones_internas.sql`
2. `database/12_disponibilidad_universitarios.sql`

Se utiliza 09 porque estaba reservada para avisos y 12 porque 10=calificaciones y 11=chat/recuperación. Ambas son aditivas e idempotentes. No volver a ejecutar 01–08 ni borrar tablas. La 09 crea `dbo.Notificaciones`; la 12 crea `dbo.DisponibilidadUniversitario`.

## API

Todas las rutas requieren JWT, y comprueban roles reales desde la BD:

- `GET /api/notificaciones/mias` devuelve hasta 100 últimos avisos de la cuenta autenticada y el número no leído **dentro de esos 100**.
- `POST /api/notificaciones/{id}/leer` solo modifica un aviso propio.
- `POST /api/notificaciones/leer-todas` marca los avisos propios no leídos.
- `GET /api/disponibilidad/mia` solo universitario.
- `PUT /api/disponibilidad/mia` solo universitario, JSON `{"franjas":[{"dia_semana":0,"hora_inicio":"09:00","hora_fin":"12:00"}]}`; reemplaza sus propias franjas atómicamente.

Las notificaciones de acciones se insertan en la MISMA transacción de `operations_service` y `seguimiento_service`. En fallo de SQL se revierte la operación y su aviso.

## Prueba manual

1. Ejecutar migraciones y reiniciar Flask con la nueva rama (revisar el puerto de Vite `VITE_API_URL`).
2. Confirmar `curl.exe -i http://localhost:5000/api/notificaciones/mias` devuelve 401 SIN token, y `.../disponibilidad/mia` también.
3. Estudiante verificado de prueba guarda lunes 09:00-12:00 y recarga: la franja permanece. Probar dos franjas solapadas: la API responde 400 y conserva las anteriores.
4. Desde cuentas ficticias: estudiante postula a solicitud nueva → aviso para adulto/familiar vigente; adulto acepta → aviso estudiante. Registrar llegada/inicio/término y confirmar → avisos correspondientes.
5. Revocar un familiar y generar un evento nuevo: ese familiar no debe recibir un nuevo aviso.
6. Marcar avisos como leídos; al recargar deben seguir leídos.
7. Verificar datos: `SELECT TOP (20) * FROM dbo.Notificaciones ORDER BY id_notificacion DESC;` y `SELECT * FROM dbo.DisponibilidadUniversitario;` (solo en entorno de prueba).

## Seguridad y límites

No se exponen direcciones, teléfonos, RUT, correo institucional ni coordenadas en avisos. No envíes contraseñas ni datos médicos por chat. Este módulo no reemplaza una respuesta de emergencia ni brinda atención en tiempo real. Las verificaciones de roles y propiedad se hacen en Flask/SQL, no solo en React. 
