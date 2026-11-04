import { apiRequest } from './api';

/**
 * Servicio de tareas disponibles y postulaciones del UNIVERSITARIO.
 * Todas las llamadas pasan por apiRequest, que ya adjunta el token de sesión.
 */

// Tareas abiertas (solo datos públicos: id, servicio, fecha_solicitada, duracion_horas, estado).
export async function getSolicitudesDisponibles() {
  const data = await apiRequest('/solicitudes/disponibles');
  return data?.solicitudes ?? [];
}

// Postula al universitario autenticado a una solicitud.
export async function postular(idSolicitud) {
  const data = await apiRequest(`/solicitudes/${encodeURIComponent(idSolicitud)}/postular`, {
    method: 'POST',
  });
  return data?.postulacion ?? null;
}

// Postulaciones del universitario autenticado, con su estado.
export async function getMisPostulaciones() {
  const data = await apiRequest('/postulaciones/mias');
  return data?.postulaciones ?? [];
}

// apiRequest solo expone el mensaje del error (no el código HTTP). Estos son los
// mensajes del backend para una sesión ausente, inválida, vencida o de un usuario
// que ya no existe (respuestas 401). Sirven para cerrar la sesión local.
const MENSAJES_DE_SESION = [
  'Token de autenticación no proporcionado.',
  'Token de autenticación inválido.',
  'El token de autenticación ha expirado.',
  'Identificador de usuario inválido.',
  'Usuario no encontrado.',
];

export function esErrorDeSesion(error) {
  return MENSAJES_DE_SESION.includes(error?.message);
}
