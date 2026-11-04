# API — Manos Amigas

Base local: `http://localhost:5000/api` · Todas las respuestas son JSON.

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/health` | Verificar que el backend está activo |
| POST | `/auth/register/adulto-mayor` | Registrar adulto mayor |
| POST | `/auth/register/universitario` | Registrar universitario |
| POST | `/auth/register/familiar` | Registrar familiar |
| POST | `/auth/login` | Iniciar sesión (devuelve access_token) |
| GET | `/auth/me` | Obtener datos del usuario autenticado (requiere JWT) |
| GET | `/auth/prueba-universitario` | Demostración de autorización por rol (requiere rol `UNIVERSITARIO`) |

## Cabecera de autenticación

Para acceder a endpoints protegidos, se debe enviar el token de acceso en la cabecera HTTP:

```http
Authorization: Bearer <access_token>
```

## Formato de respuestas

Éxito: `{"success": true, "message": "...", "user": {...}}`
Error: `{"success": false, "message": "...", "errors": {"campo": "detalle"}}` (`errors` solo si aplica).

| Código | Cuándo |
|---|---|
| 201 | Registro exitoso |
| 200 | Login exitoso o consulta autorizada |
| 400 | JSON inválido, campos faltantes o inválidos |
| 401 | Credenciales incorrectas, token ausente, inválido o expirado |
| 403 | Cuenta no activa (`BLOQUEADO` / `DESACTIVADO`) o rol no autorizado |
| 409 | RUT, email o correo institucional ya registrados |
| 500 | Error interno (p. ej. SQL Server inaccesible) |

Nunca se devuelve la contraseña ni `password_hash`.

## Reglas de datos

- **RUT**: se acepta con o sin puntos/guion, se valida el dígito verificador (módulo 11) y se guarda como `12345678-5` (sin puntos, con guion, K mayúscula). Único.
- **Email**: se guarda en minúsculas. Único. El `correo_institucional` del universitario es distinto del personal, también único, y queda con `correo_institucional_verificado = 0` (la verificación por código no está implementada).
- **Contraseña**: mínimo 8 caracteres; se almacena con `werkzeug.security.generate_password_hash`.
- **fecha_nacimiento**: formato `AAAA-MM-DD` (se eligió fecha en vez de edad para no desactualizarla). Obligatoria para adulto mayor y universitario.
- **Teléfono**: 8 a 15 dígitos, admite `+`, espacios y guiones.

## POST `/auth/register/adulto-mayor`

```json
{
  "nombre_completo": "Rosa Muñoz Pérez",
  "rut": "7.654.321-6",
  "fecha_nacimiento": "1950-05-20",
  "telefono": "+56912345678",
  "email": "rosa@example.com",
  "password": "clave-segura-1",
  "direccion": "Av. Siempre Viva 123, Valdivia",
  "contacto_confianza_nombre": "Luis Muñoz",
  "contacto_confianza_telefono": "+56987654321",
  "indicaciones_acceso": "Portón verde, perro pequeño"
}
```
`indicaciones_acceso` es opcional. No existen campos médicos (Manos Amigas no presta servicios de salud).

Respuesta `201`:
```json
{"success": true, "message": "Usuario registrado correctamente",
 "user": {"id": 15, "nombre": "Rosa Muñoz Pérez", "rol": "ADULTO_MAYOR"}}
```

## POST `/auth/register/universitario`

```json
{
  "nombre_completo": "Camila Rojas",
  "rut": "20.123.456-K",
  "fecha_nacimiento": "2002-03-10",
  "telefono": "+56911112222",
  "email": "camila@example.com",
  "password": "clave-segura-2",
  "universidad": "Universidad Austral",
  "carrera": "Enfermería",
  "anio_cursa": 3,
  "correo_institucional": "camila@alumnos.uach.cl",
  "contacto_emergencia_nombre": "Marta Rojas",
  "contacto_emergencia_telefono": "+56933334444"
}
```
> El dígito verificador debe ser correcto; usa RUT válidos al probar (ver `docs`/ejemplos PowerShell abajo).

Respuesta `201`:
```json
{"success": true, "message": "Usuario registrado correctamente",
 "user": {"id": 16, "nombre": "Camila Rojas", "rol": "UNIVERSITARIO",
          "estado_verificacion": "PENDIENTE_VERIFICACION"}}
```
El universitario **no** queda habilitado para prestar servicios hasta estar `VERIFICADO`.

## POST `/auth/register/familiar`

```json
{
  "nombre_completo": "Pedro Soto",
  "rut": "12.345.678-5",
  "telefono": "+56955556666",
  "email": "pedro@example.com",
  "password": "clave-segura-3",
  "parentesco": "Hijo",
  "telefono_alternativo": "+56944445555"
}
```
`telefono_alternativo` es opcional. La asociación con adultos mayores (`FamiliarAdultoMayor`) aún no se gestiona.

Error de validación `400`:
```json
{"success": false, "message": "Hay errores en los datos enviados.",
 "errors": {"rut": "El RUT no es válido.", "universidad": "Campo obligatorio."}}
```
Duplicado `409`:
```json
{"success": false, "message": "Los datos ya están registrados.",
 "errors": {"email": "Ya existe una cuenta con este correo."}}
```

## POST `/auth/login`

```json
{"email": "camila@example.com", "password": "clave-segura-2"}
```
Respuesta `200`:
```json
{"success": true, "message": "Inicio de sesión correcto",
 "user": {"id": 16, "nombre": "Camila Rojas", "rol": "UNIVERSITARIO",
          "estado": "ACTIVO", "estado_verificacion": "PENDIENTE_VERIFICACION"},
 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
```
- `rol` indica qué dashboard mostrar: `ADULTO_MAYOR`, `UNIVERSITARIO` o `FAMILIAR`.
- `estado` es el estado de la cuenta; `estado_verificacion` solo aparece para universitarios (no se mezclan rol y estado).
- `access_token`: token JWT para autenticar las peticiones a endpoints protegidos.
- Credenciales incorrectas: `401` con el mismo mensaje para correo inexistente o contraseña errada.

## GET `/auth/me`

Consulta los datos del usuario autenticado actual. Requiere la cabecera `Authorization: Bearer <access_token>`. Consulta la base de datos en tiempo real mediante el ID del token para comprobar que la cuenta siga activa.

Respuesta `200`:
```json
{
  "success": true,
  "user": {
    "id": 16,
    "nombre": "Camila Rojas",
    "rol": "UNIVERSITARIO",
    "estado": "ACTIVO",
    "estado_verificacion": "PENDIENTE_VERIFICACION"
  }
}
```
*(Para `ADULTO_MAYOR` y `FAMILIAR`, `estado_verificacion` se omite).*

- `401`: Token no proporcionado, token inválido o expirado (`{"success": false, "message": "..."}`).
- `403`: Si la cuenta no está activa (`BLOQUEADO` o `DESACTIVADO`) (`{"success": false, "message": "La cuenta no está activa."}`).

## GET `/auth/prueba-universitario`

Endpoint de demostración protegido con `@require_role("UNIVERSITARIO")`. Requiere la cabecera `Authorization: Bearer <access_token>`. Consulta el rol real en la base de datos.

Respuesta `200` (rol correcto):
```json
{
  "success": true,
  "message": "Acceso permitido a universitario.",
  "user": {
    "id": 16,
    "nombre": "Camila Rojas",
    "rol": "UNIVERSITARIO",
    "estado": "ACTIVO",
    "estado_verificacion": "PENDIENTE_VERIFICACION"
  }
}
```

- `401`: Token ausente o inválido.
- `403`: Si el rol real en BD no es `UNIVERSITARIO` (`{"success": false, "message": "No tiene permisos para acceder a este recurso."}`) o si la cuenta no está activa.

## Autenticación y Sesiones (JWT)

El sistema utiliza **Flask-JWT-Extended** para autenticación persistente y sin estado mediante JWT.

1. **Configuración y Seguridad**:
   - `JWT_SECRET_KEY`: Se lee desde `.env`. Si no está configurada, el backend falla inmediatamente al iniciar para evitar el uso de claves por defecto inseguras (fail-secure).
   - `JWT_ACCESS_TOKEN_EXPIRES_MINUTES`: Configurable en `.env` (60 minutos por defecto).
2. **Generación del token**: Al iniciar sesión con credenciales válidas en `POST /auth/login`, se emite un `access_token` firmado criptográficamente (HMAC-SHA256) con identidad `str(id_usuario)` y claim `rol`.
3. **Control de acceso y revocación inmediata**:
   - Las rutas protegidas validan el token con `@jwt_required()` o `@require_role(*roles)`.
   - Para evitar confiar ciegamente en claims desactualizados, se consulta la base de datos con `find_user_by_id`. Si una cuenta es `BLOQUEADO` o `DESACTIVADO`, o su rol cambia, el acceso se revoca de inmediato (403).
4. **Manejo de errores estándar**: Tokens ausentes, inválidos o expirados responden con HTTP 401 y formato uniforme `{"success": false, "message": "..."}` en español.
5. **Frontend**: El token se almacena en `localStorage` mediante `sessionService.js` y se inyecta de forma transparente en `api.js` en la cabecera `Authorization: Bearer <token>`.

## Pruebas

`backend/tests/test_auth.py` y `backend/tests/test_auth_jwt.py` usan una base en memoria y no necesitan SQL Server. Suman 27 pruebas automáticas:

```powershell
cd backend
python -m pytest
```

Una prueba de integración real requiere la base `ManosAmigas` con los 5 scripts ejecutados y un `.env` válido; se hace manualmente con los ejemplos anteriores.

## Probar con PowerShell (RUT de ejemplo válidos)

```powershell
$body = @{
  nombre_completo="Pedro Soto"; rut="12.345.678-5"; telefono="+56955556666"
  email="pedro@example.com"; password="clave-segura-3"; parentesco="Hijo"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/auth/register/familiar -ContentType "application/json; charset=utf-8" -Body $body

$login = @{ email="pedro@example.com"; password="clave-segura-3" } | ConvertTo-Json
$res = Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/auth/login -ContentType "application/json" -Body $login
$token = $res.access_token

# Consultar /me con el token obtenido
Invoke-RestMethod -Method Get -Uri http://localhost:5000/api/auth/me -Headers @{ Authorization = "Bearer $token" }
```

Con `curl`: `curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"pedro@example.com\",\"password\":\"clave-segura-3\"}"`

RUT válidos de prueba: `12.345.678-5`, `7.654.321-6` (se pueden validar con `utils.rut.is_valid_rut`). Para otros, calcula el DV con `utils.rut.calculate_dv`.

Verificar en SSMS: ejecutar `database/05_verificar_instalacion.sql`.
