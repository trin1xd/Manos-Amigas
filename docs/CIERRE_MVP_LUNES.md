# Manos Amigas — cierre del MVP para el lunes 23-11-2026

## Arquitectura y despliegue
- Frontend: React + Vite en Vercel, rama Preview `migracion-supabase`.
- Backend de pruebas: Flask en Render, servicio `manos-amigas-supabase-test`, rama `migracion-supabase`.
- Base de datos del piloto: PostgreSQL en Supabase.
- El frontend debe tener `VITE_API_URL=https://manos-amigas-supabase-test.onrender.com/api` en Preview.
- Render debe autorizar en `CORS_ORIGINS` los orígenes de los Previews usados (sin barra final).
- La rama `main` no se debe considerar migrada ni publicar cambios sin revisión.

## Flujo funcional comprobado manualmente con cuentas ficticias
1. Registro e inicio de sesión de adulto mayor, familiar y universitario.
2. Creación y consulta de solicitud de ayuda desde la cuenta de adulto mayor.
3. Habilitación administrativa **de prueba** de un universitario ficticio.
4. Visualización de solicitudes y postulación del universitario.
5. Aceptación de postulación y cambio a estado ASIGNADA.
6. Chat entre adulto mayor y universitario asignado.
7. Visualización del servicio en el panel de seguimiento.

## Funcionalidades que requieren validación adicional
- Recorrido completo: LLEGADA, INICIO, TERMINO, CONFIRMAR.
- Notificaciones y agenda ante transiciones del servicio.
- Calificaciones después de un servicio finalizado.
- Autorización y revocación de familiares.
- Recuperación de contraseña mediante correo.
- Controles de seguridad, accesibilidad y experiencia en móviles.

## Verificación y seguridad
- La habilitación de estudiantes ficticios NO valida cédula, matrícula, selfie ni antecedentes.
- El piloto usa las variables `ADMIN_VERIFICACION_PRUEBAS`, `ADMIN_ENTORNO_PRUEBAS` y temporalmente `VERIFICACION_CORREO_OBLIGATORIA=false`.
- Antes de usar la aplicación con personas reales: desactivar ambos interruptores administrativos y exigir de nuevo la confirmación institucional, revisar la seguridad integral y configurar el envío SMTP.
- La verificación por correo está codificada pero no funciona sin credenciales válidas y privadas para un proveedor SMTP. Nunca poner contraseñas personales ni secretos en GitHub.
- No compartir contraseñas de usuarios reales o administrador en documentos, chats o capturas.

## Sugerencias docentes y alcance realista
- **QR de llegada**: implementado en rama de cierre, pero **falta validación funcional de extremo a extremo**. El adulto/familiar genera un QR temporal (10 minutos) y el estudiante asignado abre el enlace, inicia sesión y confirma. El backend valida firma, rol, asignación y estado; el mismo servicio no permite duplicar la llegada. La llegada manual sigue disponible como respaldo. No equivale a identidad ni presencia física verificada.
- **Chatbot vía WhatsApp**: pendiente; un enlace a WhatsApp con mensaje predefinido no equivale a un chatbot. Automatizar mensajes requiere un número/servicio oficial, permisos y configuración de proveedor.
- **Pagos**: solo precios referenciales; no existe cobro ni transferencia de dinero en esta versión.

## Guion breve para la demostración
Entrar como adulto mayor → seleccionar categoría y tarea → mostrar una solicitud ya creada → entrar como universitario ficticio verificado para pruebas → mostrar postulación → volver al adulto mayor y mostrar asignación → abrir chat → enseñar el seguimiento pendiente. Evitar registrar eventos de llegada antes del día del servicio. Enfatizar que se usan datos ficticios.

## Colaboración
- Los cambios UX de `ux/pedir-ayuda-dos-pasos` ya se probaron parcialmente en Preview.
- Este cierre está preparado en rama independiente para revisión antes de integrarlo a `migracion-supabase`.
- Evitar merges directos a `main` y mantener las variables de entorno privadas.

## Prueba de QR (solo cuentas ficticias)
1. Iniciar sesión como adulto mayor con solicitud ASIGNADA y sin llegada registrada; ir a Seguimiento y pulsar «Mostrar QR de llegada».
2. Escanear el código con otro teléfono. Si solicita login, entrar como el universitario asignado.
3. Pulsar «Confirmar mi llegada». Verificar que cambie el seguimiento a «Iniciar servicio».
4. Continuar con INICIO, TERMINO y CONFIRMAR desde el perfil autorizado, y luego evaluar en Calificaciones.
5. Un código vencido debe indicar que se renueve. Una llegada ya confirmada no puede repetirse.

**Limitaciones del piloto:** el QR no verifica GPS ni identidad real. La implementación requiere revisión del deploy, pruebas automatizadas y ensayo manual antes de afirmarla como plenamente funcional.

**Propuestas para versiones futuras:** activar SMTP con una cuenta de proyecto, automatización de chatbot WhatsApp Business e integración de pagos reales. No anunciar estas funcionalidades como implementadas.
