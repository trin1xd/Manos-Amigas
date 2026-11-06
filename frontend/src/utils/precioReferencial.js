// Precio de referencia propuesto en el informe de la Solemne 2 (secciones 4.1 y 6.1).
// Es una propuesta que se está validando con potenciales clientes: el prototipo no cobra dinero.
export const PRECIO_REFERENCIAL_TAREA = 8000;
export const DURACION_MAXIMA_PRECIO_HORAS = 2;

export function formatoPesos(valor) {
  return `$${new Intl.NumberFormat('es-CL').format(valor)}`;
}

// Texto a mostrar según la duración elegida (en horas).
export function precioReferencialPara(duracionHoras) {
  const horas = Number(duracionHoras);
  if (horas >= 1 && horas <= DURACION_MAXIMA_PRECIO_HORAS) {
    return {
      definido: true,
      monto: formatoPesos(PRECIO_REFERENCIAL_TAREA),
      detalle: 'Por tarea de 1 a 2 horas',
    };
  }
  return {
    definido: false,
    monto: 'Por definir',
    detalle: 'Las tareas de más de 2 horas aún no tienen precio',
  };
}
