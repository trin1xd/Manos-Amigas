USE ManosAmigas;
GO
/* MIGRACIÓN 08: Seguimiento e historial de servicios. ADITIVA E IDEMPOTENTE.
   Realizar RESPALDO antes de ejecutar. No eliminar ni recrear tablas anteriores.
   Las fechas del seguimiento se guardan en UTC; las fechas planificadas existentes
   conservan su convención local original.
*/
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.Solicitudes', N'U') IS NULL
    THROW 51008, 'Falta dbo.Solicitudes. Ejecute primero las migraciones anteriores.', 1;
IF OBJECT_ID(N'dbo.Postulaciones', N'U') IS NULL
    THROW 51008, 'Falta dbo.Postulaciones. Ejecute primero migracion 06.', 1;
GO
IF OBJECT_ID(N'dbo.SeguimientoServicios', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.SeguimientoServicios (
        id_solicitud INT NOT NULL CONSTRAINT PK_SeguimientoServicios PRIMARY KEY,
        fecha_llegada_utc DATETIME2(0) NULL,
        fecha_inicio_utc DATETIME2(0) NULL,
        fecha_termino_utc DATETIME2(0) NULL,
        fecha_confirmacion_utc DATETIME2(0) NULL,
        id_confirmador INT NULL,
        CONSTRAINT FK_SeguimientoServicios_Solicitudes
            FOREIGN KEY (id_solicitud) REFERENCES dbo.Solicitudes(id_solicitud),
        CONSTRAINT FK_SeguimientoServicios_Confirmador
            FOREIGN KEY (id_confirmador) REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT CK_SeguimientoServicios_Orden CHECK (
            (fecha_inicio_utc IS NULL OR fecha_llegada_utc IS NOT NULL) AND
            (fecha_termino_utc IS NULL OR fecha_inicio_utc IS NOT NULL) AND
            (fecha_confirmacion_utc IS NULL OR (fecha_termino_utc IS NOT NULL AND id_confirmador IS NOT NULL)) AND
            (id_confirmador IS NULL OR fecha_confirmacion_utc IS NOT NULL)
        )
    );
END;
GO
IF OBJECT_ID(N'dbo.HistorialSeguimiento', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.HistorialSeguimiento (
        id_evento INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_HistorialSeguimiento PRIMARY KEY,
        id_solicitud INT NOT NULL,
        id_actor INT NOT NULL,
        accion NVARCHAR(20) NOT NULL,
        fecha_utc DATETIME2(0) NOT NULL CONSTRAINT DF_HistorialSeguimiento_Fecha DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_HistorialSeguimiento_Solicitudes FOREIGN KEY (id_solicitud)
            REFERENCES dbo.Solicitudes(id_solicitud),
        CONSTRAINT FK_HistorialSeguimiento_Actor FOREIGN KEY (id_actor)
            REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT CK_HistorialSeguimiento_Accion CHECK
            (accion IN (N'LLEGADA', N'INICIO', N'TERMINO', N'CONFIRMAR')),
        CONSTRAINT UQ_HistorialSeguimiento_UnaAccion UNIQUE (id_solicitud, accion)
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes
               WHERE object_id = OBJECT_ID(N'dbo.HistorialSeguimiento')
                 AND name = N'IX_HistorialSeguimiento_Solicitud')
    CREATE INDEX IX_HistorialSeguimiento_Solicitud
        ON dbo.HistorialSeguimiento(id_solicitud, fecha_utc);
GO
SELECT N'Migracion 08 instalada' AS resultado,
       (SELECT COUNT(*) FROM dbo.Solicitudes) AS solicitudes_conservadas,
       (SELECT COUNT(*) FROM dbo.Postulaciones) AS postulaciones_conservadas,
       (SELECT COUNT(*) FROM dbo.SeguimientoServicios) AS seguimientos,
       (SELECT COUNT(*) FROM dbo.HistorialSeguimiento) AS eventos;
GO
