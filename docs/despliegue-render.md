# Manos Amigas — preparación del backend para Render

Esta preparación no publica el backend ni migra la base de datos. El frontend en Vercel permanece independiente hasta conectar una API funcional.

## Servicio web en Render (después de subir la rama y verificar los cambios)

- Tipo: Web Service, runtime **Docker**.
- Repositorio: `trin1xd/Manos-Amigas`.
- Rama: `feature/despliegue-backend` (para probar sin afectar `main`).
- Root Directory: `backend`.
- Dockerfile Path: `Dockerfile` (dentro del Root Directory).
- Health Check Path: `/api/health`.
- Plan: elige explícitamente **Free** si aparece disponible; verifica límites y cobros antes de continuar.

Variables de entorno en el panel de Render (NO subir un archivo .env):

- `JWT_SECRET_KEY`: valor aleatorio, largo y privado.
- `SECRET_KEY`: otro valor aleatorio, largo y privado.
- `CORS_ORIGINS`: `https://manos-amigas-six.vercel.app` (origen, sin barra final).
- `FLASK_DEBUG`: `false`.
- `ADMIN_VERIFICACION_PRUEBAS`: `false`.
- `DB_SERVER`: nombre público del servidor SQL Azure (a definir).
- `DB_NAME`: nombre real de la base (a definir).
- `DB_USER` y `DB_PASSWORD`: credenciales limitadas para la base remota (a definir).
- `DB_DRIVER`: `ODBC Driver 18 for SQL Server`.
- `DB_TRUSTED_CONNECTION`: `false`.
- `DB_TRUST_SERVER_CERTIFICATE`: `false` para un certificado válido en producción.

El endpoint `/api/health` comprueba que Flask esté levantado, no comprueba conectividad de la base de datos. **No habilitar la API de usuarios para una demostración con datos reales hasta preparar una base SQL remota, aplicar las migraciones necesarias y validar el acceso.**

Después de disponer de backend y base de datos correctos, configurar en Vercel:

- `VITE_API_URL=https://TU-BACKEND.onrender.com/api`

Y volver a desplegar el frontend. No configurar VITE_API_URL con localhost, ni con contraseñas, ni con un servidor sin HTTPS.

## Verificación local antes del commit

```powershell
cd C:\Users\pc\Desktop\manos-amigas-nuevo

git status

git diff --check

git diff -- backend/requirements.txt
```

Si Docker Desktop está instalado, opcionalmente probar:

```powershell
docker build -t manos-amigas-backend -f backend/Dockerfile backend
```

No ejecutar una API administrativa de pruebas en internet. El Dockerfile usa Gunicorn y nunca activa el servidor Flask de desarrollo con debug.

Documentación oficial:
- https://render.com/docs/docker
- https://render.com/docs/free
- https://learn.microsoft.com/en-us/sql/connect/odbc/linux/installing-the-microsoft-odbc-driver-for-sql-server-on-linux
