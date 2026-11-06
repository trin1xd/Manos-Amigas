USE ManosAmigas;
GO
/* Migración 11: chat interno + recuperación de contraseñas.
   ADITIVA. Ejecutar solo tras respaldar ManosAmigas.
   No depende de la migración 09, sí de solicitudes/postulaciones de la 06. */
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.Solicitudes', N'U') IS NULL OR OBJECT_ID(N'dbo.Postulaciones', N'U') IS NULL
    THROW 51011, 'Faltan Solicitudes/Postulaciones. Instale antes la migración de operaciones.', 1;
IF OBJECT_ID(N'dbo.Usuarios', N'U') IS NULL
    THROW 51011, 'Falta dbo.Usuarios.', 1;
GO
IF OBJECT_ID(N'dbo.MensajesServicio', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.MensajesServicio (
        id_mensaje BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_MensajesServicio PRIMARY KEY,
        id_solicitud INT NOT NULL,
        id_remitente INT NOT NULL,
        mensaje NVARCHAR(500) NOT NULL,
        fecha_utc DATETIME2(3) NOT NULL CONSTRAINT DF_MensajesServicio_Fecha DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_MensajesServicio_Solicitud FOREIGN KEY (id_solicitud)
            REFERENCES dbo.Solicitudes(id_solicitud),
        CONSTRAINT FK_MensajesServicio_Remitente FOREIGN KEY (id_remitente)
            REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT CK_MensajesServicio_Texto CHECK (LEN(LTRIM(RTRIM(mensaje))) BETWEEN 1 AND 500)
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID(N'dbo.MensajesServicio') AND name=N'IX_MensajesServicio_Solicitud')
    CREATE INDEX IX_MensajesServicio_Solicitud
        ON dbo.MensajesServicio(id_solicitud, id_mensaje DESC);
GO
/* Versión de contraseña para invalidar JWT previos después de recuperarla. */
IF COL_LENGTH(N'dbo.Usuarios', N'password_version') IS NULL
    ALTER TABLE dbo.Usuarios ADD password_version INT NOT NULL
        CONSTRAINT DF_Usuarios_PasswordVersion DEFAULT (0) WITH VALUES;
GO
IF OBJECT_ID(N'dbo.RecuperacionContrasena', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.RecuperacionContrasena (
        id_recuperacion BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_RecuperacionContrasena PRIMARY KEY,
        id_usuario INT NOT NULL,
        token_hash BINARY(32) NOT NULL,
        creado_utc DATETIME2(0) NOT NULL CONSTRAINT DF_Recuperacion_Creado DEFAULT SYSUTCDATETIME(),
        vence_utc DATETIME2(0) NOT NULL,
        usado_utc DATETIME2(0) NULL,
        CONSTRAINT FK_Recuperacion_Usuario FOREIGN KEY (id_usuario) REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT UQ_Recuperacion_Token UNIQUE (token_hash),
        CONSTRAINT CK_Recuperacion_Vence CHECK (vence_utc > creado_utc)
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID(N'dbo.RecuperacionContrasena') AND name=N'IX_Recuperacion_Usuario')
    CREATE INDEX IX_Recuperacion_Usuario ON dbo.RecuperacionContrasena(id_usuario, creado_utc DESC);
GO
SELECT N'Migración 11 instalada' AS resultado,
    (SELECT COUNT(*) FROM dbo.MensajesServicio) AS mensajes,
    (SELECT COUNT(*) FROM dbo.RecuperacionContrasena) AS recuperaciones;
GO
