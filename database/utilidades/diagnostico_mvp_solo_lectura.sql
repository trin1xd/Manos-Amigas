/* Manos Amigas | Comprobación SOLO DE LECTURA.
   Ejecutar en SSMS únicamente contra una base ManosAmigas de pruebas.
   No contiene INSERT, UPDATE, DELETE, ALTER ni DROP.
   No verifica datos privados ni sustituye pruebas integrales.
*/
USE ManosAmigas;
GO

SELECT N'Usuarios' AS tabla, COUNT_BIG(*) AS registros FROM dbo.Usuarios
UNION ALL SELECT N'Solicitudes', COUNT_BIG(*) FROM dbo.Solicitudes
UNION ALL SELECT N'Postulaciones', COUNT_BIG(*) FROM dbo.Postulaciones
UNION ALL SELECT N'Vínculos familiares', COUNT_BIG(*) FROM dbo.FamiliarAdultoMayor;
GO

-- Debe devolver cero solicitudes ASIGNADAS sin postulación ACEPTADA.
SELECT s.id_solicitud, s.estado
FROM dbo.Solicitudes AS s
WHERE s.estado = N'ASIGNADA'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Postulaciones AS p
      WHERE p.id_solicitud = s.id_solicitud AND p.estado = N'ACEPTADA'
  );
GO

-- Debe devolver cero filas: más de una aceptación por solicitud.
SELECT p.id_solicitud, COUNT_BIG(*) AS aceptaciones
FROM dbo.Postulaciones AS p
WHERE p.estado = N'ACEPTADA'
GROUP BY p.id_solicitud
HAVING COUNT_BIG(*) > 1;
GO

-- Debe devolver cero filas: solicitudes nuevas sin adulto asociado.
SELECT s.id_solicitud, s.estado
FROM dbo.Solicitudes AS s
WHERE s.id_adulto_mayor IS NULL;
GO

-- Cantidades agrupadas para conocer los estados presentes.
SELECT estado, COUNT_BIG(*) AS total
FROM dbo.Solicitudes
GROUP BY estado
ORDER BY estado;
GO

IF OBJECT_ID(N'dbo.AuditoriaVerificaciones', N'U') IS NOT NULL
    SELECT COUNT_BIG(*) AS revisiones_administrativas
    FROM dbo.AuditoriaVerificaciones;
ELSE
    SELECT N'La migración 07 todavía no está instalada' AS observacion;
GO
