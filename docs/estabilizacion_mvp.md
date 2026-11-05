# Manos Amigas — Pulido y estabilización del MVP

## Alcance

Cambios no destructivos: enlace real al registro, accesibilidad «Texto grande» y «Ayuda» en inicio, manejo HTTP `401` por estado, entorno de Flask acotado y documentación actualizada. No cambia el modelo de datos ni los endpoints de solicitudes, postulaciones o familiares.

## Instalación (una rama nueva, sin modificaciones previas)

```powershell
cd C:\Users\pc\Desktop\manos-amigas-nuevo
git status
git switch main
git pull --ff-only origin main
git switch -c feature/pulido-estabilizacion
Expand-Archive -Path "$env:USERPROFILE\Downloads\ManosAmigas_Pulido_Estabilizacion.zip" -DestinationPath . -Force
python .\instalar_pulido_mvp.py
```

Si Git detecta archivos versionados modificados, conserva tu trabajo y no continúes hasta revisarlo. El instalador verifica que la rama es `feature/pulido-estabilizacion` y se detiene si los archivos no coinciden con la versión revisada; crea un respaldo fuera del repositorio.

## Flask local

Por defecto `python app.py` inicia con `FLASK_HOST=127.0.0.1`, `FLASK_PORT=5000` y `FLASK_DEBUG=false`. No hace falta agregar nada a `.env` para el uso normal. No es un servidor de producción.

**Excepción para el panel ADMIN de pruebas:** el endpoint de decisión administrativa existente exige simultáneamente `ADMIN_VERIFICACION_PRUEBAS=true` y Flask en `debug` o `testing`. Si necesitas probar aprobaciones con cuentas ficticias en tu propio equipo, agrega temporalmente en `backend/.env`:

```dotenv
FLASK_HOST=127.0.0.1
FLASK_DEBUG=true
ADMIN_VERIFICACION_PRUEBAS=true
```

Reinicia Flask, realiza la prueba local y luego vuelve a poner `FLASK_DEBUG=false` y `ADMIN_VERIFICACION_PRUEBAS=false`. Nunca habilites debug en un servidor accesible desde otros equipos; el arranque por `python app.py` lo bloquea para un host distinto de localhost.

## Diagnóstico real de base de datos

En SSMS abre y ejecuta `database/utilidades/diagnostico_mvp_solo_lectura.sql` después de confirmar que estás conectado a tu SQL Server de pruebas. Se limita a consultas SELECT, **no borra ni modifica datos**. Las dos primeras comprobaciones de integridad deben devolver cero filas. La consulta de solicitudes sin adulto asociado puede detectar datos anteriores a la migración 06; revisa antes de corregir nada.

Importante: `GET /api/health` solo demuestra que Flask responde. No comprueba SQL Server. Los tests automatizados existentes usan principalmente fakes/mocks; no demuestran por sí solos que la conexión real funcione.

## Comprobación automática

```powershell
cd C:\Users\pc\Desktop\manos-amigas-nuevo\backend
.\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm run build
npm run lint
```

## Comprobación manual (cuentas ficticias)

1. Iniciar sesión y cerrar sesión en cada perfil. Ir desde «Regístrate aquí» a selección de perfil.
2. En inicio pulsar «Texto grande», navegar al registro y comprobar que el texto aumenta; volver al inicio y desactivarlo. Pulsar «Ayuda» y comprobar el panel.
3. Con una cuenta ficticia autenticada, eliminar el token de `localStorage` y refrescar: la app debe volver a inicio de sesión sin mostrar datos. Para probar la gestión centralizada de `401`, usar una sesión con token expirado y hacer una petición de API desde el dashboard.
4. Crear una solicitud como adulto, postular como universitario habilitado y aceptar con adulto o familiar. Refrescar las páginas y verificar persistencia.
5. Confirmar que un familiar NO vinculado no pueda consultar ni modificar solicitudes de otra persona.
6. En SSMS ejecutar el diagnóstico de solo lectura y revisar que no aparezcan anomalías.
7. Si vas a probar ADMIN, habilitar temporalmente ambos flags, trabajar solo con cuentas ficticias y deshabilitarlos al finalizar.

No publicar contraseñas, JWT, RUT reales o archivos `.env` en la evidencia del proyecto.

## Archivos para el commit (NO subir el ZIP ni el instalador)

- `frontend/src/App.jsx`
- `frontend/src/pages/Login/Login.jsx`
- `frontend/src/services/api.js`
- `frontend/src/services/postulacionesService.js`
- `frontend/src/pages/Universitario/TareasDisponibles.jsx`
- `frontend/src/pages/Universitario/MisPostulaciones.jsx`
- `frontend/src/components/home/Hero.jsx`
- `frontend/src/components/home/Hero.module.css`
- `frontend/src/index.css`
- `frontend/src/components/dashboard/DashboardLayout.jsx`
- `backend/app.py`
- `backend/.env.example`
- `backend/tests/test_estabilizacion_api.py`
- `database/utilidades/diagnostico_mvp_solo_lectura.sql`
- `README.md`
- `docs/estabilizacion_mvp.md`

## Funcionalidades todavía pendientes

Recuperación real de contraseña, verificación documental auténtica, seguimiento e historial de servicios, notificaciones, chat, SOS, pagos y calificaciones. «Texto grande» mejora elementos basados en `rem`, pero se necesita una revisión de accesibilidad más amplia para los estilos de tamaño fijo.
