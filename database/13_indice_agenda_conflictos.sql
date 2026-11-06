USE ManosAmigas;
GO
/* Migración 13: índice aditivo para buscar reservas aceptadas por estudiante.
   No cambia estados, no borra datos ni convierte disponibilidad en asignación.
   Hacer copia de seguridad previamente. */
SET XACT_ABORT ON;
GO
IF OBJECT_ID(N'dbo.Postulaciones', N'U') IS NULL OR OBJECT_ID(N'dbo.Solicitudes', N'U') IS NULL
    THROW 51013, 'Faltan tablas de postulaciones o solicitudes. Ejecuta las migraciones anteriores.', 1;
GO
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'dbo.Postulaciones')
      AND name = N'IX_Postulaciones_UniversitarioEstadoSolicitud'
)
    CREATE INDEX IX_Postulaciones_UniversitarioEstadoSolicitud
      ON dbo.Postulaciones (id_universitario, estado, id_solicitud);
GO
SELECT N'Migración 13 lista (sin alterar servicios)' AS resultado;
GO
