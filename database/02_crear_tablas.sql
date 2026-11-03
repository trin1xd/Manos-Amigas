USE ManosAmigas;
GO

/*
  Esquema inicial del proyecto.
  Ajustar campos y relaciones cuando el modelo de negocio quede cerrado.
*/

CREATE TABLE Roles (
    id_rol INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(50) NOT NULL UNIQUE
);
GO

CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    id_rol INT NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    apellido NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    telefono NVARCHAR(30) NULL,
    activo BIT NOT NULL DEFAULT 1,
    fecha_creacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Usuarios_Roles FOREIGN KEY (id_rol) REFERENCES Roles(id_rol)
);
GO

CREATE TABLE Servicios (
    id_servicio INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL UNIQUE,
    descripcion NVARCHAR(500) NULL,
    activo BIT NOT NULL DEFAULT 1
);
GO

CREATE TABLE Solicitudes (
    id_solicitud INT IDENTITY(1,1) PRIMARY KEY,
    id_solicitante INT NOT NULL,
    id_servicio INT NOT NULL,
    fecha_solicitada DATETIME2 NOT NULL,
    descripcion NVARCHAR(1000) NULL,
    estado NVARCHAR(30) NOT NULL DEFAULT 'PENDIENTE',
    fecha_creacion DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT FK_Solicitudes_Usuarios FOREIGN KEY (id_solicitante) REFERENCES Usuarios(id_usuario),
    CONSTRAINT FK_Solicitudes_Servicios FOREIGN KEY (id_servicio) REFERENCES Servicios(id_servicio)
);
GO
