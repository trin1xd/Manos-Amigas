import { apiRequest } from './api';

export async function obtenerMiAgenda() {
  const resultado = await apiRequest('/agenda/mia');
  return resultado.servicios ?? [];
}
