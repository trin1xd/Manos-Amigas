import { apiRequest } from './api';

export async function consultarVerificacion() {
  const res = await apiRequest('/verificacion-institucional/mia');
  return res.data;
}

export async function solicitarCodigoInstitucional() {
  return apiRequest('/verificacion-institucional/enviar-codigo', { method: 'POST' });
}

export async function confirmarCodigoInstitucional(codigo) {
  return apiRequest('/verificacion-institucional/confirmar-codigo', {
    method: 'POST',
    body: JSON.stringify({ codigo }),
  });
}
