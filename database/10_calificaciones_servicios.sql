USE ManosAmigas;
GO
/* MIGRACIÓN 10: calificaciones bidireccionales de servicios finalizados.
   Solo crea objetos que faltan; no reinicia ni elimina información.
   Es independiente de la migración 09 (notificaciones internas).
   Realizar respaldo de ManosAmigas antes de ejecutarla.
*/
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.SeguimientoServicios', N'U') IS NULL
    THROW 51010, 'Falta la migración 08 (seguimiento).', 1;
IF OBJECT_ID(N'dbo.Calificaciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Calificaciones (
        id_calificacion INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Calificaciones PRIMARY KEY,
        id_solicitud INT NOT NULL,
        id_evaluador INT NOT NULL,
        id_evaluado INT NOT NULL,
        tipo NVARCHAR(30) NOT NULL,
        puntaje TINYINT NOT NULL,
        comentario NVARCHAR(300) NULL,
        fecha_utc DATETIME2(0) NOT NULL CONSTRAINT DF_Calificaciones_Fecha DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_Calificaciones_Solicitudes FOREIGN KEY (id_solicitud)
            REFERENCES dbo.Solicitudes(id_solicitud),
        CONSTRAINT FK_Calificaciones_Evaluador FOREIGN KEY (id_evaluador)
            REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT FK_Calificaciones_Evaluado FOREIGN KEY (id_evaluado)
            REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT CK_Calificaciones_Tipo CHECK (tipo IN
            (N'ADULTO_A_UNIVERSITARIO', N'UNIVERSITARIO_A_ADULTO')),
        CONSTRAINT CK_Calificaciones_Puntaje CHECK (puntaje BETWEEN 1 AND 5),
        CONSTRAINT CK_Calificaciones_Diferentes CHECK (id_evaluador <> id_evaluado),
        /* Adulto y familiar autorizado comparten el mismo cupo de evaluación */
        CONSTRAINT UQ_Calificaciones_UnSentido UNIQUE (id_solicitud, tipo)
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes
   WHERE object_id = OBJECT_ID(N'dbo.Calificaciones') AND name = N'IX_Calificaciones_Evaluado')
    CREATE INDEX IX_Calificaciones_Evaluado ON dbo.Calificaciones(id_evaluado, fecha_utc);
GO
SELECT N'Migración 10 instalada' AS resultado,
       (SELECT COUNT(*) FROM dbo.Calificaciones) AS calificaciones_conservadas;
GO
