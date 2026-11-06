import { useEffect, useState } from 'react';
import { obtenerNotificaciones, leerNotificacion, leerTodasNotificaciones } from '../../services/notificacionesService';
import styles from './Notificaciones.module.css';

const FORMAT = new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' });
function fechaLegible(value) {
  if (!value) return '';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? 'Fecha no disponible' : FORMAT.format(d);
}

export default function Notificaciones() {
  const [lista, setLista] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [trabajando, setTrabajando] = useState(false);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');

  async function actualizar() {
    setCargando(true);
    setError('');
    try {
      const data = await obtenerNotificaciones();
      setLista(data.notificaciones || []);
    } catch (e) {
      setError(e.message || 'No fue posible consultar los avisos.');
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    let activo = true;
    obtenerNotificaciones().then(data => {
      if (activo) setLista(data.notificaciones || []);
    }).catch(e => {
      if (activo) setError(e.message || 'No fue posible consultar los avisos.');
    }).finally(() => {
      if (activo) setCargando(false);
    });
    return () => { activo = false; };
  }, []);

  async function marcar(id) {
    if (trabajando) return;
    setTrabajando(true);
    setMensaje('');
    setError('');
    try {
      await leerNotificacion(id);
      await actualizar();
      setMensaje('Aviso marcado como leído.');
    } catch (e) {
      setError(e.message || 'No fue posible marcar el aviso.');
    } finally {
      setTrabajando(false);
    }
  }

  async function marcarTodas() {
    if (trabajando) return;
    setTrabajando(true);
    setMensaje('');
    setError('');
    try {
      await leerTodasNotificaciones();
      await actualizar();
      setMensaje('Avisos marcados como leídos.');
    } catch (e) {
      setError(e.message || 'No fue posible actualizar los avisos.');
    } finally {
      setTrabajando(false);
    }
  }

  const sinLeer = lista.filter(item => !item.leida_utc).length;
  return (
    <section className={styles.contenedor} aria-labelledby="aviso-titulo">
      <div className={styles.encabezado}>
        <div>
          <h2 id="aviso-titulo">🔔 Avisos internos</h2>
          <p>Notificaciones de tus solicitudes y servicios. Se consultan desde SQL Server.</p>
        </div>
        <div className={styles.acciones}>
          <button type="button" onClick={actualizar} disabled={cargando || trabajando}>Actualizar</button>
          <button type="button" onClick={marcarTodas} disabled={cargando || trabajando || sinLeer === 0}>
            Marcar todos como leídos
          </button>
        </div>
      </div>
      <p className={styles.ayuda}>
        {sinLeer} sin leer entre los últimos {lista.length} avisos. No se envían correos ni notificaciones push.
      </p>
      {error && <p role="alert" className={styles.error}>{error}</p>}
      {mensaje && <p role="status" className={styles.exito}>{mensaje}</p>}
      {cargando && <p role="status">Cargando avisos...</p>}
      {!cargando && lista.length === 0 && <p className={styles.vacio}>Todavía no hay avisos. Aparecerán cuando se realicen nuevas acciones.</p>}
      <ul className={styles.lista}>
        {lista.map(item => (
          <li key={item.id} className={`${styles.aviso} ${item.leida_utc ? styles.leido : ''}`}>
            <div className={styles.tituloFila}>
              <h3>{item.titulo}</h3>
              {!item.leida_utc && <span className={styles.etiqueta}>Nuevo</span>}
            </div>
            <p>{item.detalle}</p>
            <small>{fechaLegible(item.creada_utc)}</small>
            {!item.leida_utc && <button type="button" onClick={() => marcar(item.id)} disabled={trabajando || cargando}>
              Marcar como leído
            </button>}
          </li>
        ))}
      </ul>
    </section>
  );
}
