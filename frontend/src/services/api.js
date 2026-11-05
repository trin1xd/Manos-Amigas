const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const TOKEN_KEY = 'manos_amigas_token';

export async function apiRequest(path, options = {}) {
  let authHeaders = {};
  let tokenEnviado = null;
  try {
    tokenEnviado = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
    if (tokenEnviado) {
      authHeaders = { Authorization: `Bearer ${tokenEnviado}` };
    }
  } catch {
    // Continuar sin cabecera de autorización si el entorno no permite acceso a localStorage
  }

  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders,
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const error = new Error(data?.message || 'Error al comunicarse con el servidor.');
    error.fields = data?.errors || {};
    error.status = response.status;
    // Solo una respuesta 401 de una sesión enviada invalida el token.
    // Un 401 de credenciales incorrectas en /auth/login NO borra sesiones.
    if (response.status === 401 && path !== '/auth/login') {
      try {
        // No invalidar una nueva sesión por una respuesta tardía de la anterior.
        const tokenVigente = localStorage.getItem(TOKEN_KEY);
        if ((!tokenEnviado && !tokenVigente) || (tokenEnviado && tokenVigente === tokenEnviado)) {
          localStorage.removeItem(TOKEN_KEY);
          window.dispatchEvent(new Event('manos-amigas:sesion-expirada'));
        }
      } catch {
        // El navegador podría bloquear el almacenamiento.
      }
    }
    throw error;
  }

  return data;
}

export { API_URL };
