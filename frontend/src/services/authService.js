import { apiRequest } from './api';

export function login(credentials) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

export function registerAdultoMayor(data) {
  return apiRequest('/auth/register/adulto-mayor', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function registerUniversitario(data) {
  return apiRequest('/auth/register/universitario', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function registerFamiliar(data) {
  return apiRequest('/auth/register/familiar', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
