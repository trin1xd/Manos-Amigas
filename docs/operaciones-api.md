# Manos Amigas · backend operativo MVP

Esta entrega incorpora API real para **solicitudes, postulaciones y vínculos familiares**, sin cambiar el registro, el login, las credenciales ni la base de datos original. Usa Flask-JWT-Extended + `@require_role`, SQL Server y consultas `pyodbc` parametrizadas.

## Instalación segura

1. Guarda tu trabajo y crea una rama nueva. Asegúrate de que estás sobre un `main` que ya contiene los tres dashboards.
2. Extrae el ZIP en la raíz de `manos-amigas-nuevo` (carpetas `backend`, `database`, `docs` y script `instalar_backend.py`). Comprueba `git status` antes de instalar.
3. Ejecuta `python instalar_backend.py` en la raíz. Modifica **solo** `backend/app.py`, agrega el blueprint `ops_bp` y hace copia de seguridad `backend/app.py.antes_operaciones.bak`.
4. **Haz un respaldo de `ManosAmigas` antes de modificar SQL Server.** Abre en SSMS `database/06_operacion_solicitudes.sql`, verifica la base `ManosAmigas` y ejecútalo. Este script es incremental, idempotente y no elimina tablas ni registros.
5. En `backend` (con tu `.venv` activo) ejecuta `python -m pytest`. Después inicia `python app.py` y comprueba `/api/health`.
6. Ejecuta pruebas de integración manuales con cuentas **ficticias**. No uses datos médicos, direcciones reales ni documentos personales para probar.

**Advertencia:** el script SQL incorpora columnas nuevas a `Solicitudes` y crea `Postulaciones`. No uses scripts `reiniciar_datos_demo.sql` ni borres/recrees `ManosAmigas`. El código consulta las columnas nuevas: **la migración 06 debe estar ejecutada antes de llamar a las nuevas rutas**.

## Endpoints (todos bajo `/api`, todos requieren JWT)

| Método | Ruta | Rol permitido | Resultado |
|---|---|---|---|
| GET | `/catalogo/servicios` | Cualquiera de los tres | `servicios: [{id,nombre,descripcion}]` |
| POST | `/solicitudes` | Adulto mayor, familiar vinculado | `solicitud: {id,estado,id_adulto_mayor}` |
| GET | `/solicitudes/mias` | Adulto mayor, familiar | `solicitudes: []` autorizadas |
| GET | `/solicitudes/disponibles` | Universitario verificado | Tareas abiertas, datos mínimos |
| POST | `/solicitudes/{id}/postular` | Universitario verificado | `postulacion` nueva |
| GET | `/postulaciones/mias` | Universitario | `postulaciones: []` |
| GET | `/solicitudes/{id}/postulaciones` | Adulto propietario o familiar vinculado | Lista de postulantes |
| POST | `/solicitudes/{id}/postulaciones/{postId}/aceptar` | Adulto propietario o familiar vinculado | Solicitud pasa a `ASIGNADA` |
| POST | `/solicitudes/{id}/cancelar` | Adulto propietario o familiar vinculado | Solicitud pasa a `CANCELADA` |
| POST | `/familiares/vincular` | Adulto mayor | Autoriza a familiar existente por email |
| DELETE | `/familiares/{id_familiar}/vinculo` | Adulto mayor | Revoca vínculo |
| GET | `/familiares/adultos` | Familiar | Lista de adultos autorizados |

Los errores siguen el contrato `{ "success": false, "message": "..." }` con 400, 401, 403, 404, 409 o 500.

### Crear una solicitud (adulto mayor)

```json
{
  "id_servicio": 1,
  "fecha": "2026-12-20",
  "hora": "15:30",
  "duracion_horas": 2,
  "descripcion": "Necesito ayuda con compras cotidianas."
}
```

`id_servicio` es el **ID numérico real** obtenido de `GET /api/catalogo/servicios`, no los identificadores temporales del frontend (`aseo`, `lena`, etc.). Fecha y hora deben ser futuras; 1–3 horas; descripción de 10–500 caracteres. El servidor **no acepta precios ni realiza cobros**.

Para que un **familiar** cree una solicitud debe añadir `"id_adulto_mayor": 123` (ID de un adulto al que ya está vinculado mediante autorización del propio adulto). El backend comprueba la relación en SQL Server; no basta con pasar el ID.

### Autorizar a un familiar desde la cuenta del adulto mayor

```json
{
  "email_familiar": "familiar@example.com",
  "parentesco": "Hija"
}
```

La dirección y contactos privados del adulto mayor **no** se entregan al familiar desde estos endpoints. El vínculo habilita solo nombres y seguimiento/gestión de solicitudes. El adulto puede revocar la relación. **MVP:** el alta por correo es una autorización unilateral del adulto; la aceptación de invitaciones por el familiar queda para otra etapa.

### Estudiantes y estados

Un universitario registrado queda en `PENDIENTE_VERIFICACION`; puede iniciar sesión y consultar `/api/postulaciones/mias`, pero las solicitudes disponibles y la creación de postulaciones responden **403** hasta estar `VERIFICADO`. No se implementó todavía un panel administrativo para verificar identidad ni carga real de documentos.

Para una **demostración exclusivamente local con una cuenta ficticia ya comprobada**, puedes establecer el estado de verificación manualmente en SSMS, identificando primero el usuario de prueba y revisando que sea de rol UNIVERSITARIO:

```sql
SELECT u.id_usuario, u.nombre_completo, r.nombre AS rol, p.estado_verificacion
FROM dbo.Usuarios u
JOIN dbo.Roles r ON r.id_rol = u.id_rol
JOIN dbo.PerfilUniversitario p ON p.id_usuario = u.id_usuario
WHERE u.email = 'estudiante-prueba@example.com';
-- SOLO EN BD LOCAL DE PRUEBAS, Y TRAS COMPROBAR EL ID:
-- UPDATE dbo.PerfilUniversitario SET estado_verificacion = 'VERIFICADO'
-- WHERE id_usuario = ID_VERIFICADO_DE_PRUEBA;
```

No hacer esto con cuentas reales; en producción la verificación debe seguir un proceso administrativo autorizado. Cerrar y volver a iniciar sesión o recargar para actualizar el estado del usuario en `/api/auth/me`.

### Flujo de postulación

1. Adulto/familiar crea solicitud (`PENDIENTE`).
2. Universitario verificado ve `GET /api/solicitudes/disponibles` (sin nombre, dirección, teléfono ni descripción privada del adulto).
3. Universitario hace `POST /api/solicitudes/{id}/postular`.
4. Adulto o familiar autorizado revisa `GET /api/solicitudes/{id}/postulaciones`.
5. Adulto/familiar acepta una (`ACEPTADA`), las demás quedan `RECHAZADA`, y la solicitud pasa a `ASIGNADA` en la misma transacción.
6. Propietario o familiar autorizado puede cancelar (`CANCELADA`). No hay pagos ni asignación automática.

## Probar con PowerShell

En la terminal de Windows, con Flask encendido en otra:

```powershell
$base = 'http://127.0.0.1:5000/api'
$credenciales = @{ email = 'adulto-prueba@example.com'; password = 'CONTRASENA_DE_TU_CUENTA_DE_PRUEBA' } | ConvertTo-Json
$login = Invoke-RestMethod -Uri "$base/auth/login" -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($credenciales))
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Uri "$base/catalogo/servicios" -Headers $headers
Invoke-RestMethod -Uri "$base/solicitudes/mias" -Headers $headers
# Elegir un ID real de servicio de la respuesta anterior.
$sol = @{ id_servicio=1; fecha='2026-12-20'; hora='15:30'; duracion_horas=2; descripcion='Necesito ayuda con compras cotidianas.' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$base/solicitudes" -Headers $headers -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($sol))
```

Cambia fecha/hora por una futura y `id_servicio` por una opción activa obtenida en el catálogo. **No pegues en chats contraseñas ni `access_token`.**

## Seguridad y límites del MVP

- Autorización en el servidor: los usuarios no pueden consultar ni manipular solicitudes de terceros sin relación activa. JWT validado antes de cada solicitud, perfil/estado recargados desde SQL Server.
- Postulaciones solo de estudiantes con `estado_verificacion='VERIFICADO'`. Una postulación por estudiante y una aceptada por solicitud mediante restricciones SQL.
- Para aceptación/cancelación se bloquea la fila de solicitud en la transacción para reducir condiciones de carrera.
- El catálogo y las tareas disponibles no contienen datos personales privados. Las descripciones se muestran únicamente a adultos/familiares autorizados.
- **No implementado**: pagos, notificaciones, certificación de documentos, verificación administrativa, invitación/aceptación del familiar, chat, finalización/valoración de tareas, auditoría, políticas de retención, liberación de datos de contacto al estudiante asignado, mapas y protección contra abusos/rate limiting.
- Las fechas se interpretan como hora **local del servidor**; en esta instalación Windows de Chile eso debe corresponder a America/Santiago. Para despliegue remoto habrá que estandarizar fechas con offset/zona horaria.
- Los endpoints anteriores no están todavía conectados a las pestañas visuales de React: es la siguiente tarea. La demo de tareas del adulto mayor sigue usando datos locales hasta integrarla con esta API.

## Verificación técnica

- `python -m pytest` ejecuta las pruebas Flask del repositorio y las nuevas pruebas de contrato y roles. Estas pruebas usan mocks y no requieren SQL Server.
- La persistencia real requiere ejecutar la migración 06 en SSMS y luego probar con cuentas y datos ficticios reales en la instancia local.
