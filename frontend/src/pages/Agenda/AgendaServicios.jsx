import { useEffect, useState } from 'react';
import { obtenerMiAgenda } from '../../services/agendaService';
import styles from './AgendaServicios.module.css';

function fechaLocal(value) {
  if (!value) return 'Fecha no disponible';
  const fecha = new Date(value);
  if (Number.isNaN(fecha.getTime())) return 'Fecha no disponible';
  return new Intl.DateTimeFormat('es-CL', {
    dateStyle: 'full', timeStyle: 'short',
  }).format(fecha);
}

function ListaServicios({ titulo, elementos }) {
  return (
    <section className={styles.grupo} aria-label={titulo}>
      <h3>{titulo} ({elementos.length})</h3>
      {elementos.length === 0 ? (
        <p className={styles.suave}>No tienes servicios en esta categoría.</p>
      ) : (
        <ul className={styles.lista}>
          {elementos.map((item) => (
            <li key={item.id} className={styles.servicio}>
              <div className={styles.cabecera}>
                <strong>{item.servicio} <span className={styles.suave}>#{item.id}</span></strong>
                <span className={styles.estado}>{item.estado.replaceAll('_', ' ')}</span>
              </div>
              <p>📅 {fechaLocal(item.fecha_solicitada)}</p>
              <p>⏱️ {item.duracion_horas ? `${item.duracion_horas} hora(s)` : 'Duración sin especificar'}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function AgendaServicios() {
  const [items, setItems] = useState([]);
  const [actualizar, setActualizar] = useState(0);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let activo = true;
    obtenerMiAgenda()
      .then((res) => { if (activo) { setItems(res); setError(''); } })
      .catch((err) => { if (activo) setError(err.message || 'No se pudo consultar la agenda.'); })
      .finally(() => { if (activo) setCargando(false); });
    return () => { activo = false; };
  }, [actualizar]);

  const vigentes = items.filter((item) => item.estado === 'ASIGNADA' || item.estado === 'EN_CURSO');
  const finalizados = items.filter((item) => item.estado === 'FINALIZADA');

  return (
    <section className={styles.panel} aria-labelledby="titulo-agenda">
      <div className={styles.titulo}>
        <div>
          <h2 id="titulo-agenda">Mi agenda de servicios</h2>
          <p>Compromisos aceptados y servicios finalizados recientemente.</p>
        </div>
        <button type="button" className={styles.boton} onClick={() => { setCargando(true); setActualizar((v) => v + 1); }} disabled={cargando}>
          {cargando ? 'Cargando…' : 'Actualizar'}
        </button>
      </div>
      {cargando && <p role="status">Consultando tu agenda…</p>}
      {error && <p className={styles.error} role="alert">{error}</p>}
      {!cargando && !error && (
        <>
          <ListaServicios titulo="Compromisos vigentes" elementos={vigentes} />
          <ListaServicios titulo="Finalizados recientes" elementos={finalizados} />
        </>
      )}
      <p className={styles.nota}>
        Solo se muestran servicios asignados a tu cuenta, o a adultos mayores a quienes actualmente representas.
        La agenda no es un recordatorio automático ni comparte ubicaciones privadas. Las cancelaciones se consultan en Avisos.
      </p>
    </section>
  );
}
