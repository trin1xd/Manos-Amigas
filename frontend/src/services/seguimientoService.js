import { apiRequest } from './api';

export async function obtenerSeguimiento() {
  const data = await apiRequest('/seguimiento/mios');
  return data.servicios ?? [];
}

export async function registrarAccionSeguimiento(idSolicitud, accion) {
  const data = await apiRequest(`/seguimiento/solicitudes/${encodeURIComponent(idSolicitud)}/accion`, {
    method: 'POST',
    body: JSON.stringify({ accion }),
  });
  return data.seguimiento;
}
