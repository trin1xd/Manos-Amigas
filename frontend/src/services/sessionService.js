/**
 * Servicio de gestión de sesión y persistencia de JWT para Manos Amigas.
 */
import { apiRequest } from './api';

const TOKEN_KEY = 'manos_amigas_token';

/**
 * Obtiene el access_token almacenado en localStorage.
 * @returns {string|null}
 */
export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

/**
 * Guarda el access_token en localStorage.
 * @param {string} token
 */
export function setToken(token) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    }
  } catch (error) {
    console.error('Error al guardar el token de sesión:', error);
  }
}

/**
 * Elimina el token de sesión activo.
 */
export function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch (error) {
    console.error('Error al remover el token de sesión:', error);
  }
}

/**
 * Indica si existe un token en almacenamiento.
 * @returns {boolean}
 */
export function hasToken() {
  return Boolean(getToken());
}

/**
 * Inicia sesión contra el backend, guarda el access_token si es exitoso
 * y devuelve los datos recibidos (user, access_token).
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{success: boolean, message: string, user: object, access_token: string}>}
 */
export async function loginUser(email, password) {
  const data = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  if (data?.access_token) {
    setToken(data.access_token);
  }

  return data;
}

/**
 * Consulta los datos del usuario autenticado actual desde el backend.
 * Requiere que exista un token válido.
 * @returns {Promise<{success: boolean, user: object}>}
 */
export async function getMe() {
  return apiRequest('/auth/me');
}

/**
 * Cierra la sesión local del usuario.
 */
export function logout() {
  clearToken();
}

