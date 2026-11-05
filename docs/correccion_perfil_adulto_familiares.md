# Corrección del perfil adulto mayor: móvil y familiares vinculados

## Qué cambió
- En pantallas de hasta 550 px, las cuatro pestañas del adulto mayor se presentan en dos filas (2 x 2). **Mi perfil** queda visible sin desplazarse horizontalmente.
- **Mi perfil → Autorizar a un familiar** incluye la lista de familiares autorizados, con nombre, parentesco y correo.
- El adulto puede **revocar acceso** luego de confirmar. Usa el endpoint DELETE que ya existía.
- Nueva ruta `GET /api/familiares/mios` restringida al rol `ADULTO_MAYOR`. Filtra por usuario autenticado y vínculos activos.
- No se modifica SQL Server ni se agregan tablas; reutiliza `dbo.FamiliarAdultoMayor`.

## Importante: crear cuenta familiar no significa vincularla
El familiar debe registrarse primero como `FAMILIAR`. El adulto debe ingresar luego su correo y parentesco en **Autorizar a un familiar**. Solo los vínculos activos aparecen en **Familiares autorizados**.

## Pruebas en Windows PowerShell
Desde la raíz del repositorio:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm run build
npm run lint
```

En la página: iniciar sesión como adulto, reducir el navegador a ancho de celular, comprobar que `Mi perfil` está visible. Abrirlo, autorizar a un familiar de prueba que ya tenga cuenta, comprobar la aparición en la lista. Recargar la página y verificar que sigue. Revocar el acceso y comprobar que desaparece. Entrar como familiar y verificar que el adulto deja de estar visible.

## Consulta opcional en SSMS (solo lectura)
Reemplaza `correo@ejemplo.cl` por el email **del adulto** cuya cuenta se prueba:

```sql
USE ManosAmigas;
GO
DECLARE @correo_adulto NVARCHAR(255) = N'correo@ejemplo.cl';
SELECT a.nombre_completo AS adulto, f.nombre_completo AS familiar,
       f.email AS email_familiar, v.parentesco, v.activo
FROM dbo.FamiliarAdultoMayor AS v
JOIN dbo.Usuarios AS a ON a.id_usuario = v.id_adulto_mayor
JOIN dbo.Usuarios AS f ON f.id_usuario = v.id_familiar
WHERE a.email = @correo_adulto;
```

Las filas con `activo = 1` deben aparecer en el panel, siempre que el familiar también tenga cuenta activa y rol `FAMILIAR`.

No ejecutes scripts de reinicio ni borres cuentas o vínculos existentes.
