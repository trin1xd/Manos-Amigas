USE ManosAmigas;
GO
/* Migración ADITIVA para la verificación administrativa de pruebas.
   NO elimina usuarios, solicitudes ni datos existentes.
   EJECUTAR CON RESPALDO PREVIO EN UNA BASE LOCAL DE DESARROLLO.
*/
IF NOT EXISTS (SELECT 1 FROM dbo.Roles WHERE nombre = N'ADMIN')
    INSERT INTO dbo.Roles(nombre) VALUES (N'ADMIN');
GO
IF OBJECT_ID(N'dbo.AuditoriaVerificaciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.AuditoriaVerificaciones (
        id_auditoria INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_AuditoriaVerificaciones PRIMARY KEY,
        id_universitario INT NOT NULL,
        id_administrador INT NOT NULL,
        estado_anterior NVARCHAR(30) NOT NULL,
        estado_nuevo NVARCHAR(30) NOT NULL,
        observacion NVARCHAR(500) NOT NULL,
        fecha_revision_utc DATETIME2 NOT NULL CONSTRAINT DF_AuditoriaVerificaciones_Fecha DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_AuditoriaVerificaciones_Universitario FOREIGN KEY (id_universitario)
            REFERENCES dbo.PerfilUniversitario(id_usuario),
        CONSTRAINT FK_AuditoriaVerificaciones_Admin FOREIGN KEY (id_administrador)
            REFERENCES dbo.Usuarios(id_usuario),
        CONSTRAINT CK_AuditoriaVerificaciones_EstadoNuevo CHECK (estado_nuevo IN (N'VERIFICADO', N'RECHAZADO'))
    );
END;
GO
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'dbo.AuditoriaVerificaciones')
      AND name = N'IX_AuditoriaVerificaciones_Universitario'
)
    CREATE INDEX IX_AuditoriaVerificaciones_Universitario
        ON dbo.AuditoriaVerificaciones(id_universitario, fecha_revision_utc DESC);
GO
SELECT N'Migración 07 instalada' AS resultado,
       (SELECT COUNT(*) FROM dbo.Roles WHERE nombre = N'ADMIN') AS rol_admin,
       (SELECT COUNT(*) FROM dbo.AuditoriaVerificaciones) AS decisiones_auditadas;
GO
