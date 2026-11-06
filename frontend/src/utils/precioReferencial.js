// Rango de precio de referencia propuesto en el informe de la Solemne 2 (secciones 4.1, 6.1 y 8.4).
// Es una propuesta que se está validando con potenciales clientes: el prototipo no cobra dinero.
// El valor final dependerá del esfuerzo de la tarea (las consultas pidieron diferenciar por esfuerzo).
export const PRECIO_REFERENCIAL_MINIMO = 4000;
export const PRECIO_REFERENCIAL_MAXIMO = 8000;
export const DURACION_MAXIMA_PRECIO_HORAS = 2;
// Comisión de punto de partida de la sección 6.1 del informe (supuesto aún no validado).
export const COMISION_PLATAFORMA_PORCENTAJE = 20;

export function formatoPesos(valor) {
  return `$${new Intl.NumberFormat('es-CL').format(valor)}`;
}

function formatoRango(minimo, maximo) {
  return `${formatoPesos(minimo)} a ${formatoPesos(maximo)}`;
}

function descontarComision(valor) {
  return Math.round((valor * (100 - COMISION_PLATAFORMA_PORCENTAJE)) / 100);
}

// Rango de referencia como texto, para avisos generales.
export const RANGO_PRECIO_TEXTO = formatoRango(PRECIO_REFERENCIAL_MINIMO, PRECIO_REFERENCIAL_MAXIMO);

// Texto a mostrar según la duración elegida (en horas).
export function precioReferencialPara(duracionHoras) {
  const horas = Number(duracionHoras);
  if (horas >= 1 && horas <= DURACION_MAXIMA_PRECIO_HORAS) {
    return {
      definido: true,
      monto: RANGO_PRECIO_TEXTO,
      detalle: 'Por tarea de 1 a 2 horas',
    };
  }
  return {
    definido: false,
    monto: 'Por definir',
    detalle: 'Las tareas de más de 2 horas aún no tienen precio',
  };
}

// Pago estimado para el estudiante: el rango de referencia menos la comisión de la plataforma.
// Es una estimación para la demostración; el prototipo no realiza pagos.
export function pagoEstudianteReferencialPara(duracionHoras) {
  const horas = Number(duracionHoras);
  if (horas >= 1 && horas <= DURACION_MAXIMA_PRECIO_HORAS) {
    return {
      definido: true,
      monto: formatoRango(descontarComision(PRECIO_REFERENCIAL_MINIMO), descontarComision(PRECIO_REFERENCIAL_MAXIMO)),
    };
  }
  return { definido: false, monto: 'Por definir' };
}
