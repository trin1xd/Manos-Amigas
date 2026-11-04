/** Solicitudes reales: usa el cliente existente que añade el JWT. */
import { apiRequest } from './api';

export async function obtenerCatalogoServicios() {
  const respuesta = await apiRequest('/catalogo/servicios');
  return respuesta.servicios ?? [];
}

export async function obtenerMisSolicitudes() {
  const respuesta = await apiRequest('/solicitudes/mias');
  return respuesta.solicitudes ?? [];
}

export async function registrarSolicitud(datos) {
  const respuesta = await apiRequest('/solicitudes', {
    method: 'POST',
    body: JSON.stringify(datos),
  });
  return respuesta.solicitud;
}

export async function obtenerPostulantes(idSolicitud) {
  const respuesta = await apiRequest(`/solicitudes/${encodeURIComponent(idSolicitud)}/postulaciones`);
  return respuesta.postulaciones ?? [];
}

export async function aceptarPostulacion(idSolicitud, idPostulacion) {
  const respuesta = await apiRequest(
    `/solicitudes/${encodeURIComponent(idSolicitud)}/postulaciones/${encodeURIComponent(idPostulacion)}/aceptar`,
    { method: 'POST' }
  );
  return respuesta.solicitud;
}

export async function cancelarSolicitud(idSolicitud) {
  const respuesta = await apiRequest(`/solicitudes/${encodeURIComponent(idSolicitud)}/cancelar`, {
    method: 'POST',
  });
  return respuesta.solicitud;
}

export async function autorizarFamiliar(datos) {
  const respuesta = await apiRequest('/familiares/vincular', {
    method: 'POST',
    body: JSON.stringify(datos),
  });
  return respuesta.vinculo;
}
