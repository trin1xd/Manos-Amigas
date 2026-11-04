// El backend entrega las fechas como "AAAA-MM-DDTHH:MM" en hora local del servidor
// (sin zona horaria). El navegador interpreta ese formato como hora local, por lo que
// la hora mostrada coincide con la hora guardada en la solicitud.

const FORMATO_DIA = new Intl.DateTimeFormat('es-CL', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
});

const FORMATO_HORA = new Intl.DateTimeFormat('es-CL', {
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});

export function formatearFechaHora(valor) {
  if (!valor) return 'Fecha no disponible';
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return 'Fecha no disponible';
  return `${FORMATO_DIA.format(fecha)}, ${FORMATO_HORA.format(fecha)} h`;
}

export function formatearDuracion(horas) {
  const numero = Number(horas);
  if (!numero) return 'Duración no indicada';
  return `${numero} ${numero === 1 ? 'hora' : 'horas'}`;
}
