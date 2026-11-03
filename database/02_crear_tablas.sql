USE ManosAmigas;
GO

/*
  Tablas de Manos Amigas.
  - Aqui se definen columnas, PRIMARY KEY, NOT NULL y valores por defecto.
  - UNIQUE, FOREIGN KEY y CHECK se agregan en 03_restricciones.sql.
  - Cada tabla se crea solo si no existe (el script se puede re-ejecutar).

  Si tu base tenia el esquema inicial anterior (Usuarios con nombre/apellido),
  elimina la base y vuelve a ejecutar los scripts desde 01.
*/

-- Roles: ADULTO_MAYOR, UNIVERSITARIO, FAMILIAR
IF OBJECT_ID(N'dbo.Roles', N'U') IS NULL
CREATE TABLE dbo.Roles (
    id_rol INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    nombre NVARCHAR(50) NOT NULL
);
GO

-- Tabla central de cuentas (credenciales + datos generales). Un rol por cuenta.
IF OBJECT_ID(N'dbo.Usuarios', N'U') IS NULL
CREATE TABLE dbo.Usuarios (
    id_usuario INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    nombre_completo NVARCHAR(150) NOT NULL,
    rut NVARCHAR(12) NOT NULL,                 -- formato guardado: 12345678-5
    email NVARCHAR(255) NOT NULL,              -- siempre en minusculas
    telefono NVARCHAR(20) NOT NULL,
    fecha_nacimiento DATE NULL,                -- obligatoria para adulto mayor y universitario (lo valida el backend)
    password_hash NVARCHAR(255) NOT NULL,
    id_rol INT NOT NULL,
    estado NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO',   -- ACTIVO | BLOQUEADO | DESACTIVADO
    fecha_creacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    fecha_actualizacion DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

-- Perfil 1 a 1 con Usuarios: la PK es a la vez FK (id_usuario).
IF OBJECT_ID(N'dbo.PerfilAdultoMayor', N'U') IS NULL
CREATE TABLE dbo.PerfilAdultoMayor (
    id_usuario INT NOT NULL PRIMARY KEY,
    direccion NVARCHAR(255) NOT NULL,                    -- informacion privada
    contacto_confianza_nombre NVARCHAR(150) NOT NULL,
    contacto_confianza_telefono NVARCHAR(20) NOT NULL,
    indicaciones_acceso NVARCHAR(500) NULL               -- mascota, porton, timbre, escalera, etc.
    -- Sin campos medicos: Manos Amigas no presta servicios de salud.
);
GO

IF OBJECT_ID(N'dbo.PerfilUniversitario', N'U') IS NULL
CREATE TABLE dbo.PerfilUniversitario (
    id_usuario INT NOT NULL PRIMARY KEY,
    universidad NVARCHAR(150) NOT NULL,
    carrera NVARCHAR(150) NOT NULL,
    anio_cursa TINYINT NOT NULL,
    correo_institucional NVARCHAR(255) NOT NULL,
    correo_institucional_verificado BIT NOT NULL DEFAULT 0,   -- preparado para verificacion futura
    contacto_emergencia_nombre NVARCHAR(150) NOT NULL,
    contacto_emergencia_telefono NVARCHAR(20) NOT NULL,
    -- PENDIENTE_VERIFICACION | VERIFICADO | RECHAZADO | SUSPENDIDO
    estado_verificacion NVARCHAR(30) NOT NULL DEFAULT 'PENDIENTE_VERIFICACION'
);
GO

IF OBJECT_ID(N'dbo.PerfilFamiliar', N'U') IS NULL
CREATE TABLE dbo.PerfilFamiliar (
    id_usuario INT NOT NULL PRIMARY KEY,
    parentesco NVARCHAR(100) NOT NULL,
    telefono_alternativo NVARCHAR(20) NULL
);
GO

-- Preparada para el futuro: un familiar puede estar asociado a varios adultos mayores.
-- Todavia no se inserta nada en esta tabla.
IF OBJECT_ID(N'dbo.FamiliarAdultoMayor', N'U') IS NULL
CREATE TABLE dbo.FamiliarAdultoMayor (
    id_relacion INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    id_familiar INT NOT NULL,
    id_adulto_mayor INT NOT NULL,
    parentesco NVARCHAR(100) NOT NULL,
    activo BIT NOT NULL DEFAULT 1,
    fecha_creacion DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO

-- Preparada para el futuro: documentos de verificacion del universitario.
-- Todavia no hay subida real de archivos.
IF OBJECT_ID(N'dbo.DocumentosVerificacion', N'U') IS NULL
CREATE TABLE dbo.DocumentosVerificacion (
    id_documento INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo_documento NVARCHAR(30) NOT NULL,        -- SELFIE | CEDULA_FRENTE | CEDULA_REVERSO | ALUMNO_REGULAR | ANTECEDENTES
    referencia_archivo NVARCHAR(500) NULL,       -- ruta o referencia (a definir cuando exista almacenamiento)
    estado_verificacion NVARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',  -- PENDIENTE | APROBADO | RECHAZADO
    fecha_subida DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    fecha_revision DATETIME2 NULL
);
GO

-- Tablas del esquema inicial previo (fuera del alcance de esta etapa; se conservan sin cambios).
IF OBJECT_ID(N'dbo.Servicios', N'U') IS NULL
CREATE TABLE dbo.Servicios (
    id_servicio INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(500) NULL,
    activo BIT NOT NULL DEFAULT 1
);
GO

IF OBJECT_ID(N'dbo.Solicitudes', N'U') IS NULL
CREATE TABLE dbo.Solicitudes (
    id_solicitud INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    id_solicitante INT NOT NULL,
    id_servicio INT NOT NULL,
    fecha_solicitada DATETIME2 NOT NULL,
    descripcion NVARCHAR(1000) NULL,
    estado NVARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    fecha_creacion DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO
