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

// apiRequest conserva el código HTTP, independiente del texto del mensaje.
export function esErrorDeSesion(error) {
  return error?.status === 401;
}
