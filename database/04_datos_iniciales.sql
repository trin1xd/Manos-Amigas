USE ManosAmigas;
GO

INSERT INTO Roles (nombre)
SELECT v.nombre
FROM (VALUES
    ('ADULTO_MAYOR'),
    ('UNIVERSITARIO'),
    ('FAMILIAR')
) v(nombre)
WHERE NOT EXISTS (
    SELECT 1 FROM Roles r WHERE r.nombre = v.nombre
);
GO

INSERT INTO Servicios (nombre, descripcion)
SELECT v.nombre, v.descripcion
FROM (VALUES
    ('Compras', 'Apoyo en supermercado, farmacia y tiendas locales.'),
    ('Trámites', 'Apoyo en gestiones y diligencias cotidianas.'),
    ('Tareas del hogar', 'Apoyo en organización y tareas domésticas cotidianas.'),
    ('Apoyo digital', 'Ayuda con celular, videollamadas y aplicaciones.'),
    ('Acompañamiento', 'Acompañamiento a citas o diligencias.'),
    ('Compañía', 'Visitas, paseos y conversación.')
) v(nombre, descripcion)
WHERE NOT EXISTS (
    SELECT 1 FROM Servicios s WHERE s.nombre = v.nombre
);
GO
