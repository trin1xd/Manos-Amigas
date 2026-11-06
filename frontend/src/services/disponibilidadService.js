import { apiRequest } from './api';

export async function obtenerDisponibilidad() {
  const data = await apiRequest('/disponibilidad/mia');
  return data.franjas || [];
}
export async function guardarDisponibilidad(franjas) {
  const data = await apiRequest('/disponibilidad/mia', {
    method: 'PUT',
    body: JSON.stringify({ franjas }),
  });
  return data.franjas || [];
}
