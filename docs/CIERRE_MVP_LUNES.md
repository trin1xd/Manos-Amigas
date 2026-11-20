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
- **QR de llegada**: pendiente. Debe implementarse como comprobante temporal de un solo uso, asociado al servicio asignado y validado en backend. No demuestra por sí mismo presencia física ni identidad.
- **Chatbot vía WhatsApp**: pendiente; un enlace a WhatsApp con mensaje predefinido no equivale a un chatbot. Automatizar mensajes requiere un número/servicio oficial, permisos y configuración de proveedor.
- **Pagos**: solo precios referenciales; no existe cobro ni transferencia de dinero en esta versión.

## Guion breve para la demostración
Entrar como adulto mayor → seleccionar categoría y tarea → mostrar una solicitud ya creada → entrar como universitario ficticio verificado para pruebas → mostrar postulación → volver al adulto mayor y mostrar asignación → abrir chat → enseñar el seguimiento pendiente. Evitar registrar eventos de llegada antes del día del servicio. Enfatizar que se usan datos ficticios.

## Colaboración
- Los cambios UX de `ux/pedir-ayuda-dos-pasos` ya se probaron parcialmente en Preview.
- Este cierre está preparado en rama independiente para revisión antes de integrarlo a `migracion-supabase`.
- Evitar merges directos a `main` y mantener las variables de entorno privadas.
