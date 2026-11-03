# API — Manos Amigas

Base local: `http://localhost:5000/api` · Todas las respuestas son JSON.

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/health` | Verificar que el backend está activo |
| POST | `/auth/register/adulto-mayor` | Registrar adulto mayor |
| POST | `/auth/register/universitario` | Registrar universitario |
| POST | `/auth/register/familiar` | Registrar familiar |
| POST | `/auth/login` | Iniciar sesión |

## Formato de respuestas

Éxito: `{"success": true, "message": "...", "user": {...}}`
Error: `{"success": false, "message": "...", "errors": {"campo": "detalle"}}` (`errors` solo si aplica).

| Código | Cuándo |
|---|---|
| 201 | Registro exitoso |
| 200 | Login exitoso |
| 400 | JSON inválido, campos faltantes o inválidos |
| 401 | Credenciales incorrectas |
| 403 | Cuenta no activa (`BLOQUEADO` / `DESACTIVADO`) |
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
          "estado": "ACTIVO", "estado_verificacion": "PENDIENTE_VERIFICACION"}}
```
- `rol` indica qué dashboard mostrar: `ADULTO_MAYOR`, `UNIVERSITARIO` o `FAMILIAR`.
- `estado` es el estado de la cuenta; `estado_verificacion` solo aparece para universitarios (no se mezclan rol y estado).
- Credenciales incorrectas: `401` con el mismo mensaje para correo inexistente o contraseña errada.

## Probar con PowerShell (RUT de ejemplo válidos)

```powershell
$body = @{
  nombre_completo="Pedro Soto"; rut="12.345.678-5"; telefono="+56955556666"
  email="pedro@example.com"; password="clave-segura-3"; parentesco="Hijo"
} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/auth/register/familiar -ContentType "application/json; charset=utf-8" -Body $body

$login = @{ email="pedro@example.com"; password="clave-segura-3" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/api/auth/login -ContentType "application/json" -Body $login
```

Con `curl`: `curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email\":\"pedro@example.com\",\"password\":\"clave-segura-3\"}"`

RUT válidos de prueba: `12.345.678-5`, `7.654.321-6` (se pueden validar con `utils.rut.is_valid_rut`). Para otros, calcula el DV con `utils.rut.calculate_dv`.

Verificar en SSMS: ejecutar `database/05_verificar_instalacion.sql`.

## Autenticación futura (JWT)

Hoy el login **no emite token**: el frontend recibe `user` y debe tratarlo como no confiable para endpoints protegidos. Para agregar JWT más adelante:

1. Instalar `Flask-JWT-Extended` y agregar `JWT_SECRET_KEY` a `.env`/`config.py`.
2. En `auth_service.login` (o en la ruta) llamar a `create_access_token(identity=str(user["id"]), additional_claims={"rol": user["rol"]})` y devolver `access_token` junto a `user`.
3. Proteger rutas con `@jwt_required()` y restringir por rol leyendo el claim `rol`.
4. En React, guardar el token y enviarlo en `Authorization: Bearer <token>` desde `services/api.js`.

## Pruebas

`backend/tests/test_auth.py` usa una base en memoria y no necesita SQL Server. Una prueba de integración real requiere la base `ManosAmigas` con los 5 scripts ejecutados y un `.env` válido; se hace manualmente con los ejemplos anteriores.
