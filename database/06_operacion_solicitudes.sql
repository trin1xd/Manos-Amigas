USE ManosAmigas;
GO
/*
  MIGRACION ADITIVA - MVP DE OPERACIONES.
  Ejecutar EN SSMS con copia de seguridad previa; NO elimina ni reinicia datos.
  NO ejecutar scripts de reinicio ni recrear la base.
*/
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.Solicitudes', N'U') IS NULL
    THROW 51000, 'Falta dbo.Solicitudes. Ejecute primero los scripts 01-04.', 1;
IF OBJECT_ID(N'dbo.FamiliarAdultoMayor', N'U') IS NULL
    THROW 51000, 'Falta dbo.FamiliarAdultoMayor.', 1;
GO
-- Identifica al adulto beneficiario incluso cuando la solicitud la crea un familiar.
IF COL_LENGTH('dbo.Solicitudes', 'id_adulto_mayor') IS NULL
    ALTER TABLE dbo.Solicitudes ADD id_adulto_mayor INT NULL;
GO
IF COL_LENGTH('dbo.Solicitudes', 'duracion_horas') IS NULL
    ALTER TABLE dbo.Solicitudes ADD duracion_horas TINYINT NULL;
GO
-- Completar los registros antiguos cuyo solicitante es el mismo adulto mayor.
UPDATE s
SET id_adulto_mayor = s.id_solicitante
FROM dbo.Solicitudes AS s
JOIN dbo.PerfilAdultoMayor AS a ON a.id_usuario = s.id_solicitante
WHERE s.id_adulto_mayor IS NULL;
GO
IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_Solicitudes_AdultoMayor')
    ALTER TABLE dbo.Solicitudes ADD CONSTRAINT FK_Solicitudes_AdultoMayor
        FOREIGN KEY (id_adulto_mayor) REFERENCES dbo.PerfilAdultoMayor(id_usuario);
GO
IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_Solicitudes_Duracion')
    ALTER TABLE dbo.Solicitudes ADD CONSTRAINT CK_Solicitudes_Duracion
        CHECK (duracion_horas BETWEEN 1 AND 3 OR duracion_horas IS NULL);
GO
IF OBJECT_ID(N'dbo.Postulaciones', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Postulaciones (
        id_postulacion INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Postulaciones PRIMARY KEY,
        id_solicitud INT NOT NULL,
        id_universitario INT NOT NULL,
        estado NVARCHAR(20) NOT NULL CONSTRAINT DF_Postulaciones_Estado DEFAULT 'PENDIENTE',
        fecha_creacion DATETIME2 NOT NULL CONSTRAINT DF_Postulaciones_Fecha DEFAULT SYSDATETIME(),
        CONSTRAINT FK_Postulaciones_Solicitudes FOREIGN KEY (id_solicitud)
            REFERENCES dbo.Solicitudes(id_solicitud),
        CONSTRAINT FK_Postulaciones_Universitario FOREIGN KEY (id_universitario)
            REFERENCES dbo.PerfilUniversitario(id_usuario),
        CONSTRAINT UQ_Postulaciones_SolicitudUniversitario UNIQUE (id_solicitud, id_universitario),
        CONSTRAINT CK_Postulaciones_Estado CHECK (estado IN ('PENDIENTE', 'ACEPTADA', 'RECHAZADA'))
    );
END;
GO
-- Protección adicional: una sola postulación ACEPTADA por solicitud.
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UX_Postulaciones_UnaAceptada' AND object_id = OBJECT_ID('dbo.Postulaciones'))
    CREATE UNIQUE INDEX UX_Postulaciones_UnaAceptada ON dbo.Postulaciones(id_solicitud)
        WHERE estado = 'ACEPTADA';
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Solicitudes_AdultoEstado' AND object_id = OBJECT_ID('dbo.Solicitudes'))
    CREATE INDEX IX_Solicitudes_AdultoEstado ON dbo.Solicitudes(id_adulto_mayor, estado, fecha_solicitada);
GO
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Postulaciones_Universitario' AND object_id = OBJECT_ID('dbo.Postulaciones'))
    CREATE INDEX IX_Postulaciones_Universitario ON dbo.Postulaciones(id_universitario, fecha_creacion);
GO
-- Agregar las categorías que aparecen en el prototipo sin eliminar las existentes.
INSERT INTO dbo.Servicios(nombre, descripcion)
SELECT v.nombre, v.descripcion
FROM (VALUES
  (N'Cortar leña', N'Cortar y apilar leña, sin operar maquinaria peligrosa.'),
  (N'Aseo y orden', N'Limpieza y organización cotidiana del hogar.'),
  (N'Cocina y comida', N'Apoyo en preparación de comidas sencillas.'),
  (N'Jardín y huerto', N'Regar y cuidar plantas.'),
  (N'Arreglos menores', N'Ayuda doméstica simple, sin intervenciones eléctricas o de gas.'),
  (N'Mascotas', N'Cuidado cotidiano de mascotas.'),
  (N'Ayuda con tecnología', N'Uso básico de celular, aplicaciones y videollamadas.')
) AS v(nombre, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM dbo.Servicios AS s WHERE s.nombre = v.nombre);
GO
SELECT 'Migración 06 completada' AS resultado,
       (SELECT COUNT(*) FROM dbo.Servicios) AS servicios,
       (SELECT COUNT(*) FROM dbo.Solicitudes) AS solicitudes_existentes,
       (SELECT COUNT(*) FROM dbo.Postulaciones) AS postulaciones;
GO
