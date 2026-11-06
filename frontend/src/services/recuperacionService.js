import { apiRequest } from './api';

export function solicitarRecuperacion(email) {
  return apiRequest('/auth/recuperacion/solicitar', {
    method: 'POST', body: JSON.stringify({ email }),
  });
}

export function confirmarRecuperacion(token, password) {
  return apiRequest('/auth/recuperacion/confirmar', {
    method: 'POST', body: JSON.stringify({ token, password }),
  });
}
