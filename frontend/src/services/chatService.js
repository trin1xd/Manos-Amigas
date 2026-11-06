import { apiRequest } from './api';

export async function obtenerConversaciones() {
  const data = await apiRequest('/chat/conversaciones');
  return data.conversaciones || [];
}

export async function obtenerMensajes(id) {
  const data = await apiRequest(`/chat/solicitudes/${Number(id)}/mensajes`);
  return data.mensajes || [];
}

export async function enviarMensaje(id, mensaje) {
  return apiRequest(`/chat/solicitudes/${Number(id)}/mensajes`, {
    method: 'POST', body: JSON.stringify({ mensaje }),
  });
}
