USE ManosAmigas;
GO
/* MIGRACIÓN 12 - franjas semanales elegidas por el universitario.
   Día: 0 lunes, ... 6 domingo. Horas locales (sin zona horaria).
   Solo informativo: no asigna tareas, no bloquea postulaciones automáticamente.
*/
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.Usuarios', N'U') IS NULL OR OBJECT_ID(N'dbo.PerfilUniversitario', N'U') IS NULL
    THROW 51012, 'Faltan tablas de usuarios y perfil universitario.', 1;
GO
IF OBJECT_ID(N'dbo.DisponibilidadUniversitario', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.DisponibilidadUniversitario (
        id_disponibilidad INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_DisponibilidadUniversitario PRIMARY KEY,
        id_universitario INT NOT NULL,
        dia_semana TINYINT NOT NULL,
        hora_inicio TIME(0) NOT NULL,
        hora_fin TIME(0) NOT NULL,
        CONSTRAINT FK_DisponibilidadUniversitario_Perfil FOREIGN KEY (id_universitario)
            REFERENCES dbo.PerfilUniversitario(id_usuario),
        CONSTRAINT CK_DisponibilidadUniversitario_Dia CHECK (dia_semana BETWEEN 0 AND 6),
        CONSTRAINT CK_DisponibilidadUniversitario_Hora CHECK (hora_inicio < hora_fin),
        CONSTRAINT UQ_DisponibilidadUniversitario_Franja UNIQUE
            (id_universitario, dia_semana, hora_inicio, hora_fin)
    );
END;
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'dbo.DisponibilidadUniversitario')
      AND name = N'IX_DisponibilidadUniversitario_Usuario')
    CREATE INDEX IX_DisponibilidadUniversitario_Usuario
       ON dbo.DisponibilidadUniversitario(id_universitario, dia_semana, hora_inicio);
GO
SELECT N'Migración 12 lista' AS resultado,
       (SELECT COUNT(*) FROM dbo.DisponibilidadUniversitario) AS franjas_conservadas;
GO
