// Precio de referencia propuesto en el informe de la Solemne 2 (secciones 4.1 y 6.1).
// Es una propuesta que se está validando con potenciales clientes: el prototipo no cobra dinero.
export const PRECIO_REFERENCIAL_TAREA = 8000;
export const DURACION_MAXIMA_PRECIO_HORAS = 2;
// Comisión de punto de partida de la sección 6.1 del informe (supuesto aún no validado).
export const COMISION_PLATAFORMA_PORCENTAJE = 20;

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

// Pago estimado para el estudiante: el precio de referencia menos la comisión de la plataforma.
// Es una estimación para la demostración; el prototipo no realiza pagos.
export function pagoEstudianteReferencialPara(duracionHoras) {
  const horas = Number(duracionHoras);
  if (horas >= 1 && horas <= DURACION_MAXIMA_PRECIO_HORAS) {
    const pago = Math.round((PRECIO_REFERENCIAL_TAREA * (100 - COMISION_PLATAFORMA_PORCENTAJE)) / 100);
    return { definido: true, monto: formatoPesos(pago) };
  }
  return { definido: false, monto: 'Por definir' };
}
