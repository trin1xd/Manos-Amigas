import { apiRequest } from './api';

export async function obtenerNotificaciones() {
  return apiRequest('/notificaciones/mias');
}
export async function leerNotificacion(id) {
  return apiRequest(`/notificaciones/${id}/leer`, { method: 'POST' });
}
export async function leerTodasNotificaciones() {
  return apiRequest('/notificaciones/leer-todas', { method: 'POST' });
}
