/** API del perfil familiar. Todas las rutas requieren JWT y validación de rol en Flask. */
import { apiRequest } from './api';

export async function obtenerAdultosVinculados() {
  const res = await apiRequest('/familiares/adultos');
  return res.adultos ?? [];
}

export async function obtenerSolicitudesFamiliares() {
  const res = await apiRequest('/solicitudes/mias');
  return res.solicitudes ?? [];
}

export async function obtenerServiciosFamiliares() {
  const res = await apiRequest('/catalogo/servicios');
  return res.servicios ?? [];
}

export async function crearSolicitudFamiliar(datos) {
  const res = await apiRequest('/solicitudes', {
    method: 'POST',
    body: JSON.stringify(datos),
  });
  return res.solicitud;
}

export async function obtenerPostulantesFamiliares(idSolicitud) {
  const res = await apiRequest(`/solicitudes/${encodeURIComponent(idSolicitud)}/postulaciones`);
  return res.postulaciones ?? [];
}

export async function aceptarPostulanteFamiliar(idSolicitud, idPostulacion) {
  const res = await apiRequest(`/solicitudes/${encodeURIComponent(idSolicitud)}/postulaciones/${encodeURIComponent(idPostulacion)}/aceptar`, {
    method: 'POST',
  });
  return res.solicitud;
}

export async function cancelarSolicitudFamiliar(idSolicitud) {
  const res = await apiRequest(`/solicitudes/${encodeURIComponent(idSolicitud)}/cancelar`, {
    method: 'POST',
  });
  return res.solicitud;
}
