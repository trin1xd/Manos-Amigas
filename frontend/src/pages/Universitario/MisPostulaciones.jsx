import { useCallback, useEffect, useState } from 'react';
import dash from '../../components/dashboard/DashboardLayout.module.css';
import styles from './UniversitarioPaneles.module.css';
import { esErrorDeSesion, getMisPostulaciones } from '../../services/postulacionesService';
import { formatearFechaHora } from './formatoFecha';

// Cada estado lleva símbolo y texto: el color nunca es lo único que lo distingue.
const ESTADO_POSTULACION = {
  PENDIENTE: { texto: '◷ Pendiente de respuesta', clase: '' },
  ACEPTADA: { texto: '✓ Aceptada', clase: dash.estadoOk },
  RECHAZADA: { texto: '✕ Rechazada', clase: dash.estadoAlerta },
};

const ESTADO_SOLICITUD = {
  PENDIENTE: 'Solicitud abierta',
  ASIGNADA: 'Solicitud asignada',
  CANCELADA: 'Solicitud cancelada',
};

export default function MisPostulaciones({ onLogout }) {
  const [postulaciones, setPostulaciones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  // Solo cambia el estado después de recibir la respuesta; el indicador de carga
  // se activa desde el botón "Actualizar" o con el valor inicial.
  const cargar = useCallback(async () => {
    try {
      setPostulaciones(await getMisPostulaciones());
      setError('');
    } catch (err) {
      if (esErrorDeSesion(err)) {
        return; // El evento global ya redirige a iniciar sesión.
      }
      setError(err.message || 'No pudimos cargar tus postulaciones.');
    } finally {
      setCargando(false);
    }
  }, [onLogout]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  function actualizar() {
    setCargando(true);
    cargar();
  }

  return (
    <section className={dash.panel} aria-labelledby="uni-postulaciones" aria-busy={cargando}>
      <div className={styles.encabezado}>
        <h2 id="uni-postulaciones">Mis postulaciones</h2>
        <button type="button" className={styles.botonSecundario} onClick={actualizar} disabled={cargando}>
          {cargando ? 'Actualizando...' : 'Actualizar'}
        </button>
      </div>
      <p className={styles.descripcion}>Aquí ves a qué tareas postulaste y la respuesta que recibiste.</p>

      {error && <p className={styles.mensajeError} role="alert">{error}</p>}

      {cargando && postulaciones.length === 0 && (
        <p className={styles.mensajeInfo} role="status">Cargando tus postulaciones...</p>
      )}

      {!cargando && !error && postulaciones.length === 0 && (
        <p className={styles.mensajeInfo} role="status">Todavía no has postulado a ninguna tarea.</p>
      )}

      {postulaciones.length > 0 && (
        <ul className={styles.lista}>
          {postulaciones.map((postulacion) => {
            const estado = ESTADO_POSTULACION[postulacion.estado] || { texto: postulacion.estado, clase: '' };
            return (
              <li key={postulacion.id} className={styles.item}>
                <h3 className={styles.itemTitulo}>{postulacion.servicio}</h3>
                <dl className={styles.meta}>
                  <div><dt>Fecha de la tarea:</dt><dd>{formatearFechaHora(postulacion.fecha_solicitada)}</dd></div>
                  <div><dt>Postulaste el:</dt><dd>{formatearFechaHora(postulacion.fecha_creacion)}</dd></div>
                </dl>
                <div className={styles.estadosFila}>
                  <span className={`${dash.estado} ${estado.clase}`}>{estado.texto}</span>
                  {ESTADO_SOLICITUD[postulacion.estado_solicitud] && (
                    <span className={dash.estado}>{ESTADO_SOLICITUD[postulacion.estado_solicitud]}</span>
                  )}
                </div>
                {postulacion.estado === 'ACEPTADA' && (
                  <p className={styles.nota}>
                    Tu postulación fue aceptada. La coordinación de contacto se habilitará en una próxima etapa.
                  </p>
                )}
              </li>
            );
          })}
        </ul>
      )}

      <p className={dash.aviso}>Manos Amigas no entrega datos de contacto en esta versión y no realiza pagos desde este panel.</p>
    </section>
  );
}
