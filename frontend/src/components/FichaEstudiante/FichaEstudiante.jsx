import styles from './FichaEstudiante.module.css';

// Cada estado lleva símbolo y texto: el color nunca es lo único que lo distingue.
const ESTADO_POSTULACION = {
  PENDIENTE: '◷ Pendiente',
  ACEPTADA: '✓ Aceptada',
  RECHAZADA: '✕ Rechazada',
};

const VERIFICACION = {
  VERIFICADO: { texto: '✓ Cuenta verificada', clase: styles.verificada },
  PENDIENTE_VERIFICACION: { texto: '◷ Verificación pendiente', clase: styles.alerta },
  RECHAZADO: { texto: '✕ Verificación rechazada', clase: styles.alerta },
  SUSPENDIDO: { texto: '✕ Cuenta suspendida', clase: styles.alerta },
};

function textoAnio(anio) {
  const numero = Number(anio);
  return numero > 0 ? `${numero}.º año` : null;
}

/**
 * Ficha mínima del estudiante que postula. Solo muestra lo que entrega el backend para
 * decidir con más confianza: nombre, carrera, universidad, año y estado de verificación.
 * Nunca incluye RUT, correo, teléfono ni dirección.
 */
export default function FichaEstudiante({ postulacion }) {
  const verificacion = VERIFICACION[postulacion.estudiante_verificacion];
  const estudios = [postulacion.estudiante_carrera, postulacion.estudiante_universidad]
    .filter(Boolean)
    .join(' · ');
  const anio = textoAnio(postulacion.estudiante_anio);

  return (
    <div className={styles.ficha}>
      <strong className={styles.nombre}>{postulacion.estudiante_nombre}</strong>
      <p className={styles.estudios}>
        {estudios || 'Sin información de estudios'}
        {anio ? ` · ${anio}` : ''}
      </p>
      <div className={styles.etiquetas}>
        {verificacion && <span className={`${styles.etiqueta} ${verificacion.clase}`}>{verificacion.texto}</span>}
        <span className={styles.etiqueta}>{ESTADO_POSTULACION[postulacion.estado] || postulacion.estado}</span>
      </div>
    </div>
  );
}

export function NotaFichaEstudiante() {
  return (
    <p className={styles.nota}>
      La verificación es una habilitación de prueba: todavía no se validan documentos ni identidades reales.
    </p>
  );
}
