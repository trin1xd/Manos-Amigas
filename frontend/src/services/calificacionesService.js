import { apiRequest } from './api';

export async function obtenerCalificaciones() {
  const res = await apiRequest('/calificaciones/mias');
  return res.servicios ?? [];
}

export async function calificarServicio(idSolicitud, puntaje, comentario) {
  const res = await apiRequest(`/calificaciones/solicitudes/${encodeURIComponent(idSolicitud)}`, {
    method: 'POST',
    body: JSON.stringify({ puntaje, comentario }),
  });
  return res.calificacion;
}
