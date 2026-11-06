USE ManosAmigas;
GO
/* MIGRACIÓN 09 - Avisos internos. Crear solo si no existe.
   Ejecutar backup previo. No toca mensajes, calificaciones o solicitudes existentes.
   Los avisos solo se generan para acciones NUEVAS después de instalar el código.
*/
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.Usuarios', N'U') IS NULL OR OBJECT_ID(N'dbo.Solicitudes', N'U') IS NULL
    THROW 51009, 'Faltan tablas principales de ManosAmigas.', 1;
GO
IF OBJECT_ID(N'dbo.Notificaciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Notificaciones (
        id_notificacion INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Notificaciones PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_solicitud INT NULL,
        tipo NVARCHAR(32) NOT NULL,
        titulo NVARCHAR(120) NOT NULL,
        detalle NVARCHAR(300) NOT NULL,
        creada_utc DATETIME2(0) NOT NULL CONSTRAINT DF_Notificaciones_Fecha DEFAULT SYSUTCDATETIME(),
        leida_utc DATETIME2(0) NULL,
        CONSTRAINT FK_Notificaciones_Usuario FOREIGN KEY (id_usuario) REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT FK_Notificaciones_Solicitud FOREIGN KEY (id_solicitud) REFERENCES dbo.Solicitudes(id_solicitud),
        CONSTRAINT CK_Notificaciones_Tipo CHECK (tipo IN
          (N'POSTULACION', N'ASIGNACION', N'RECHAZO', N'CANCELACION',
           N'LLEGADA', N'INICIO', N'TERMINO', N'CONFIRMACION'))
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE object_id = OBJECT_ID(N'dbo.Notificaciones')
    AND name = N'IX_Notificaciones_Destinatario')
    CREATE INDEX IX_Notificaciones_Destinatario
        ON dbo.Notificaciones(id_usuario, creada_utc DESC, id_notificacion DESC)
        INCLUDE (leida_utc);
GO
SELECT N'Migración 09 lista' AS resultado,
    (SELECT COUNT(*) FROM dbo.Notificaciones) AS avisos_conservados;
GO
