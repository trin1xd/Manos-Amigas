USE ManosAmigas;
GO
/* MIGRACION 14 - confirmacion del control del correo institucional.
   Aditiva e idempotente: NO elimina usuarios, historiales ni datos existentes.
   RESPALDAR ManosAmigas antes de ejecutar.
   Confirmar correo NO significa acreditar identidad ni condición de alumno regular.
*/
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.PerfilUniversitario',N'U') IS NULL OR OBJECT_ID(N'dbo.Usuarios',N'U') IS NULL
    THROW 51014, 'Falta el esquema base de ManosAmigas.', 1;
IF COL_LENGTH('dbo.PerfilUniversitario','correo_institucional_verificado') IS NULL
    THROW 51014, 'Falta la columna correo_institucional_verificado.', 1;
GO
IF OBJECT_ID(N'dbo.CodigosCorreoInstitucional',N'U') IS NULL
BEGIN
    CREATE TABLE dbo.CodigosCorreoInstitucional (
        id_universitario INT NOT NULL PRIMARY KEY,
        codigo_hash VARBINARY(32) NULL,
        vence_utc DATETIME2 NULL,
        intentos TINYINT NOT NULL CONSTRAINT DF_CCI_Intentos DEFAULT 0,
        ultimo_envio_utc DATETIME2 NULL,
        dia_envios_utc DATE NULL,
        envios_dia TINYINT NOT NULL CONSTRAINT DF_CCI_Envios DEFAULT 0,
        fecha_confirmacion_utc DATETIME2 NULL,
        CONSTRAINT FK_CCI_Universitario FOREIGN KEY(id_universitario)
            REFERENCES dbo.PerfilUniversitario(id_usuario),
        CONSTRAINT CK_CCI_Intentos CHECK (intentos BETWEEN 0 AND 5),
        CONSTRAINT CK_CCI_Envios CHECK (envios_dia BETWEEN 0 AND 5)
    );
END;
GO
IF OBJECT_ID(N'dbo.AuditoriaVerificacionInstitucional',N'U') IS NULL
BEGIN
    CREATE TABLE dbo.AuditoriaVerificacionInstitucional (
        id_auditoria BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        id_universitario INT NOT NULL,
        id_actor INT NOT NULL,
        evento VARCHAR(32) NOT NULL,
        fecha_utc DATETIME2 NOT NULL CONSTRAINT DF_AVI_Fecha DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_AVI_Universitario FOREIGN KEY(id_universitario)
            REFERENCES dbo.PerfilUniversitario(id_usuario),
        CONSTRAINT FK_AVI_Actor FOREIGN KEY(id_actor)
            REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT CK_AVI_Evento CHECK(evento IN
            ('CODIGO_SOLICITADO','CORREO_CONFIRMADO','CONSTANCIA_SUBIDA','CONSTANCIA_CONSULTADA'))
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE
    object_id=OBJECT_ID(N'dbo.AuditoriaVerificacionInstitucional') AND name=N'IX_AVI_Universitario')
    CREATE INDEX IX_AVI_Universitario ON dbo.AuditoriaVerificacionInstitucional(id_universitario,fecha_utc DESC);
GO
SELECT N'Migracion 14 - correo institucional lista' AS resultado,
       (SELECT COUNT(*) FROM dbo.CodigosCorreoInstitucional) AS registros_codigos,
       (SELECT COUNT(*) FROM dbo.PerfilUniversitario WHERE correo_institucional_verificado = 1) AS correos_confirmados;
GO
