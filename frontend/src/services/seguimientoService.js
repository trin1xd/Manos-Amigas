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

export async function obtenerQrLlegada(idSolicitud) {
  const data = await apiRequest(`/seguimiento/solicitudes/${encodeURIComponent(idSolicitud)}/qr-llegada`, {
    method: 'POST',
  });
  return data;
}

export async function confirmarLlegadaPorQr(token) {
  const data = await apiRequest('/seguimiento/llegada/qr', {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
  return data.seguimiento;
}
