const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const TOKEN_KEY = 'manos_amigas_token';

export async function apiRequest(path, options = {}) {
  let authHeaders = {};
  try {
    const token = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
    if (token) {
      authHeaders = { Authorization: `Bearer ${token}` };
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
    throw error;
  }

  return data;
}

export { API_URL };
