import { apiRequest } from './api';

export async function obtenerUniversitariosRevision() {
  const resultado = await apiRequest('/admin/universitarios');
  return resultado.universitarios ?? [];
}

export async function decidirVerificacion(id, accion, observacion, confirmacionPruebas) {
  const resultado = await apiRequest(`/admin/universitarios/${encodeURIComponent(id)}/decision`, {
    method: 'POST',
    body: JSON.stringify({
      accion,
      observacion,
      confirmacion_pruebas: confirmacionPruebas,
    }),
  });
  return resultado.universitario;
}
