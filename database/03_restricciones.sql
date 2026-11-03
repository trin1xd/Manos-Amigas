USE ManosAmigas;
GO

/*
  Restricciones UNIQUE, FOREIGN KEY y CHECK.
  Cada una se crea solo si no existe (el script se puede re-ejecutar).
*/

-- ---------- UNIQUE ----------
IF OBJECT_ID(N'dbo.UQ_Roles_nombre') IS NULL
    ALTER TABLE dbo.Roles ADD CONSTRAINT UQ_Roles_nombre UNIQUE (nombre);
GO
IF OBJECT_ID(N'dbo.UQ_Usuarios_rut') IS NULL
    ALTER TABLE dbo.Usuarios ADD CONSTRAINT UQ_Usuarios_rut UNIQUE (rut);
GO
IF OBJECT_ID(N'dbo.UQ_Usuarios_email') IS NULL
    ALTER TABLE dbo.Usuarios ADD CONSTRAINT UQ_Usuarios_email UNIQUE (email);
GO
IF OBJECT_ID(N'dbo.UQ_PerfilUniversitario_correo_institucional') IS NULL
    ALTER TABLE dbo.PerfilUniversitario
        ADD CONSTRAINT UQ_PerfilUniversitario_correo_institucional UNIQUE (correo_institucional);
GO
IF OBJECT_ID(N'dbo.UQ_FamiliarAdultoMayor_par') IS NULL
    ALTER TABLE dbo.FamiliarAdultoMayor
        ADD CONSTRAINT UQ_FamiliarAdultoMayor_par UNIQUE (id_familiar, id_adulto_mayor);
GO
IF OBJECT_ID(N'dbo.UQ_Servicios_nombre') IS NULL
    ALTER TABLE dbo.Servicios ADD CONSTRAINT UQ_Servicios_nombre UNIQUE (nombre);
GO

-- ---------- FOREIGN KEY ----------
IF OBJECT_ID(N'dbo.FK_Usuarios_Roles') IS NULL
    ALTER TABLE dbo.Usuarios ADD CONSTRAINT FK_Usuarios_Roles
        FOREIGN KEY (id_rol) REFERENCES dbo.Roles(id_rol);
GO
IF OBJECT_ID(N'dbo.FK_PerfilAdultoMayor_Usuarios') IS NULL
    ALTER TABLE dbo.PerfilAdultoMayor ADD CONSTRAINT FK_PerfilAdultoMayor_Usuarios
        FOREIGN KEY (id_usuario) REFERENCES dbo.Usuarios(id_usuario);
GO
IF OBJECT_ID(N'dbo.FK_PerfilUniversitario_Usuarios') IS NULL
    ALTER TABLE dbo.PerfilUniversitario ADD CONSTRAINT FK_PerfilUniversitario_Usuarios
        FOREIGN KEY (id_usuario) REFERENCES dbo.Usuarios(id_usuario);
GO
IF OBJECT_ID(N'dbo.FK_PerfilFamiliar_Usuarios') IS NULL
    ALTER TABLE dbo.PerfilFamiliar ADD CONSTRAINT FK_PerfilFamiliar_Usuarios
        FOREIGN KEY (id_usuario) REFERENCES dbo.Usuarios(id_usuario);
GO
IF OBJECT_ID(N'dbo.FK_FamiliarAdultoMayor_Familiar') IS NULL
    ALTER TABLE dbo.FamiliarAdultoMayor ADD CONSTRAINT FK_FamiliarAdultoMayor_Familiar
        FOREIGN KEY (id_familiar) REFERENCES dbo.PerfilFamiliar(id_usuario);
GO
IF OBJECT_ID(N'dbo.FK_FamiliarAdultoMayor_AdultoMayor') IS NULL
    ALTER TABLE dbo.FamiliarAdultoMayor ADD CONSTRAINT FK_FamiliarAdultoMayor_AdultoMayor
        FOREIGN KEY (id_adulto_mayor) REFERENCES dbo.PerfilAdultoMayor(id_usuario);
GO
IF OBJECT_ID(N'dbo.FK_DocumentosVerificacion_Universitario') IS NULL
    ALTER TABLE dbo.DocumentosVerificacion ADD CONSTRAINT FK_DocumentosVerificacion_Universitario
        FOREIGN KEY (id_usuario) REFERENCES dbo.PerfilUniversitario(id_usuario);
GO
IF OBJECT_ID(N'dbo.FK_Solicitudes_Usuarios') IS NULL
    ALTER TABLE dbo.Solicitudes ADD CONSTRAINT FK_Solicitudes_Usuarios
        FOREIGN KEY (id_solicitante) REFERENCES dbo.Usuarios(id_usuario);
GO
IF OBJECT_ID(N'dbo.FK_Solicitudes_Servicios') IS NULL
    ALTER TABLE dbo.Solicitudes ADD CONSTRAINT FK_Solicitudes_Servicios
        FOREIGN KEY (id_servicio) REFERENCES dbo.Servicios(id_servicio);
GO

-- ---------- CHECK (estados y valores permitidos) ----------
IF OBJECT_ID(N'dbo.CK_Usuarios_estado') IS NULL
    ALTER TABLE dbo.Usuarios ADD CONSTRAINT CK_Usuarios_estado
        CHECK (estado IN ('ACTIVO', 'BLOQUEADO', 'DESACTIVADO'));
GO
IF OBJECT_ID(N'dbo.CK_PerfilUniversitario_estado') IS NULL
    ALTER TABLE dbo.PerfilUniversitario ADD CONSTRAINT CK_PerfilUniversitario_estado
        CHECK (estado_verificacion IN ('PENDIENTE_VERIFICACION', 'VERIFICADO', 'RECHAZADO', 'SUSPENDIDO'));
GO
IF OBJECT_ID(N'dbo.CK_PerfilUniversitario_anio') IS NULL
    ALTER TABLE dbo.PerfilUniversitario ADD CONSTRAINT CK_PerfilUniversitario_anio
        CHECK (anio_cursa BETWEEN 1 AND 10);
GO
IF OBJECT_ID(N'dbo.CK_Documentos_tipo') IS NULL
    ALTER TABLE dbo.DocumentosVerificacion ADD CONSTRAINT CK_Documentos_tipo
        CHECK (tipo_documento IN ('SELFIE', 'CEDULA_FRENTE', 'CEDULA_REVERSO', 'ALUMNO_REGULAR', 'ANTECEDENTES'));
GO
IF OBJECT_ID(N'dbo.CK_Documentos_estado') IS NULL
    ALTER TABLE dbo.DocumentosVerificacion ADD CONSTRAINT CK_Documentos_estado
        CHECK (estado_verificacion IN ('PENDIENTE', 'APROBADO', 'RECHAZADO'));
GO
-- Un mismo tipo de documento por universitario (se reemplaza, no se duplica).
IF OBJECT_ID(N'dbo.UQ_Documentos_usuario_tipo') IS NULL
    ALTER TABLE dbo.DocumentosVerificacion ADD CONSTRAINT UQ_Documentos_usuario_tipo
        UNIQUE (id_usuario, tipo_documento);
GO

