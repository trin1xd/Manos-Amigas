USE ManosAmigas;
GO

SELECT DB_NAME() AS base_datos_actual;

-- Deben existir las 9 tablas
SELECT name AS tabla FROM sys.tables ORDER BY name;

-- Deben existir exactamente los 3 roles
SELECT * FROM Roles ORDER BY id_rol;

-- Usuarios registrados con su rol (sin mostrar password_hash)
SELECT u.id_usuario, u.nombre_completo, u.rut, u.email, r.nombre AS rol, u.estado
FROM Usuarios u
JOIN Roles r ON r.id_rol = u.id_rol
ORDER BY u.id_usuario;

SELECT * FROM PerfilAdultoMayor;
SELECT * FROM PerfilUniversitario;
SELECT * FROM PerfilFamiliar;
GO
