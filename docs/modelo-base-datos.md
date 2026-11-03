# Modelo de base de datos

SQL Server, base `ManosAmigas`. Scripts en `database/` (ejecutar en orden numérico).

```text
Roles 1───N Usuarios 1───0..1 PerfilAdultoMayor ──┐
                     1───0..1 PerfilUniversitario ──── 1───N DocumentosVerificacion
                     1───0..1 PerfilFamiliar ──┐   │
                                               └─ N───N ─ (FamiliarAdultoMayor) ─ PerfilAdultoMayor
```

## Decisiones

- **Una cuenta, un rol**: `Usuarios.id_rol` apunta a `Roles`. No hay endpoint para cambiarlo; un cambio futuro requerirá proceso administrativo.
- **Perfil 1 a 1**: en cada tabla de perfil la PK `id_usuario` es también FK a `Usuarios`; así es imposible tener dos perfiles del mismo tipo para un usuario.
- Los datos generales (nombre, RUT, email, teléfono, fecha de nacimiento) viven solo en `Usuarios`.
- Rol y estado son conceptos separados: `Usuarios.estado` (cuenta) y `PerfilUniversitario.estado_verificacion` (verificación).
- Sin datos médicos de ningún tipo.

## Tablas

**Roles** — `id_rol` PK, `nombre` UNIQUE. Valores: `ADULTO_MAYOR`, `UNIVERSITARIO`, `FAMILIAR`.

**Usuarios** — `id_usuario` PK, `nombre_completo`, `rut` UNIQUE (`12345678-5`), `email` UNIQUE, `telefono`, `fecha_nacimiento` (NULL; obligatoria para adulto mayor y universitario), `password_hash`, `id_rol` FK, `estado` (`ACTIVO`/`BLOQUEADO`/`DESACTIVADO`), `fecha_creacion`, `fecha_actualizacion`.

**PerfilAdultoMayor** — `id_usuario` PK/FK, `direccion` (privada), `contacto_confianza_nombre`, `contacto_confianza_telefono`, `indicaciones_acceso` (NULL).

**PerfilUniversitario** — `id_usuario` PK/FK, `universidad`, `carrera`, `anio_cursa` (1–10), `correo_institucional` UNIQUE, `correo_institucional_verificado` (0 por defecto), `contacto_emergencia_nombre`, `contacto_emergencia_telefono`, `estado_verificacion` (`PENDIENTE_VERIFICACION` por defecto; `VERIFICADO`, `RECHAZADO`, `SUSPENDIDO`).

**PerfilFamiliar** — `id_usuario` PK/FK, `parentesco`, `telefono_alternativo` (NULL).

**FamiliarAdultoMayor** *(preparada, sin uso aún)* — `id_relacion` PK, `id_familiar` FK → `PerfilFamiliar`, `id_adulto_mayor` FK → `PerfilAdultoMayor`, `parentesco`, `activo`, `fecha_creacion`; UNIQUE (`id_familiar`, `id_adulto_mayor`). Permite que un familiar se asocie a varios adultos mayores.

**DocumentosVerificacion** *(preparada, sin subida real aún)* — `id_documento` PK, `id_usuario` FK → `PerfilUniversitario`, `tipo_documento` (`SELFIE`, `CEDULA_FRENTE`, `CEDULA_REVERSO`, `ALUMNO_REGULAR`, `ANTECEDENTES`), `referencia_archivo` (NULL), `estado_verificacion` (`PENDIENTE`/`APROBADO`/`RECHAZADO`), `fecha_subida`, `fecha_revision`; UNIQUE (`id_usuario`, `tipo_documento`).

**Servicios**, **Solicitudes** — del esquema inicial previo; se conservan sin cambios y fuera del alcance de esta etapa.

## Pendiente

Triggers/lógica para actualizar `fecha_actualizacion`, flujo de verificación, asociación familiar ↔ adulto mayor, administración y cambio de rol.
