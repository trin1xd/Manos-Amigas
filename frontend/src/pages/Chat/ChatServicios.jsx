import { useCallback, useEffect, useState } from 'react';
import { obtenerConversaciones, obtenerMensajes, enviarMensaje } from '../../services/chatService';
import styles from './ChatServicios.module.css';

const LABELS = { ASIGNADA: 'Asignada', EN_CURSO: 'En curso', FINALIZADA: 'Finalizada' };

function fechaLocal(value) {
  if (!value) return '';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? '' :
    new Intl.DateTimeFormat('es-CL', { dateStyle: 'short', timeStyle: 'short' }).format(d);
}

export default function ChatServicios({ usuario }) {
  const [conversaciones, setConversaciones] = useState([]);
  const [elegida, setElegida] = useState(null);
  const [mensajes, setMensajes] = useState([]);
  const [texto, setTexto] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(true);
  const [enviando, setEnviando] = useState(false);

  const actualizarMensajes = useCallback(async (id) => {
    if (!id) return;
    const nuevos = await obtenerMensajes(id);
    setMensajes(nuevos);
  }, []);

  const actualizarConversaciones = useCallback(async () => {
    const lista = await obtenerConversaciones();
    setConversaciones(lista);
    setElegida(actual => (lista.some(item => item.id === actual) ? actual : (lista[0]?.id ?? null)));
  }, []);

  useEffect(() => {
    let activo = true;
    obtenerConversaciones().then(lista => {
      if (!activo) return;
      setConversaciones(lista);
      setElegida(lista[0]?.id ?? null);
    }).catch(err => { if (activo) setError(err.message); })
      .finally(() => { if (activo) setCargando(false); });
    return () => { activo = false; };
  }, []);

  useEffect(() => {
    if (!elegida) return undefined;
    let activo = true;
    const refrescar = async () => {
      try {
        const datos = await obtenerMensajes(elegida);
        if (activo) { setMensajes(datos); setError(''); }
      } catch (err) {
        if (activo) setError(err.message || 'No fue posible cargar los mensajes.');
      }
    };
    refrescar();
    const interval = window.setInterval(refrescar, 8000);
    return () => { activo = false; window.clearInterval(interval); };
  }, [elegida]);

  const conversacion = conversaciones.find(c => c.id === elegida);
  async function actualizar() {
    try {
      setError('');
      await actualizarConversaciones();
      if (elegida) await actualizarMensajes(elegida);
    } catch (err) { setError(err.message); }
  }

  async function enviar(evento) {
    evento.preventDefault();
    if (!elegida || !texto.trim() || enviando) return;
    setEnviando(true);
    setError('');
    try {
      await enviarMensaje(elegida, texto.trim());
      setTexto('');
      await actualizarMensajes(elegida);
    } catch (err) { setError(err.message || 'No se pudo enviar el mensaje.'); }
    finally { setEnviando(false); }
  }

  return (
    <section className={styles.contenedor} aria-labelledby="chat-titulo">
      <div className={styles.cabecera}>
        <div>
          <h2 id="chat-titulo">Chat de servicios</h2>
          <p>Mensajes entre el estudiante asignado, la persona adulta mayor y sus familiares autorizados.</p>
        </div>
        <button type="button" onClick={actualizar}>Actualizar</button>
      </div>
      <p className={styles.aviso}>Este chat no es un servicio de emergencias. No compartas contraseñas ni datos sensibles.</p>
      {error && <p role="alert" className={styles.error}>{error}</p>}
      {cargando && <p role="status">Cargando conversaciones...</p>}
      {!cargando && conversaciones.length === 0 && <p className={styles.vacio}>El chat aparecerá cuando tengas un servicio asignado.</p>}
      {conversaciones.length > 0 && (
        <div className={styles.panel}>
          <aside className={styles.conversaciones} aria-label="Tus conversaciones">
            {conversaciones.map(c => <button type="button" key={c.id}
              className={`${styles.item} ${elegida === c.id ? styles.activa : ''}`}
              aria-pressed={elegida === c.id}
              onClick={() => { setElegida(c.id); setMensajes([]); setError(''); }}>
              <strong>{c.servicio} · #{c.id}</strong>
              <span>{LABELS[c.estado] || c.estado}</span>
            </button>)}
          </aside>
          <div className={styles.chat}>
            {conversacion && <div className={styles.detalle}>
              <strong>{conversacion.servicio} · #{conversacion.id}</strong>
              <span>{conversacion.adulto} · {conversacion.universitario}</span>
            </div>}
            <div className={styles.mensajes} aria-label="Mensajes del servicio" role="log" aria-live="polite" aria-relevant="additions">
              {mensajes.length === 0 && <p>Sin mensajes por ahora.</p>}
              {mensajes.map(m => <div key={m.id}
                className={`${styles.mensaje} ${m.id_remitente === usuario?.id ? styles.propio : ''}`}>
                <strong>{m.id_remitente === usuario?.id ? 'Tú' : m.remitente}</strong>
                <p>{m.mensaje}</p>
                <time>{fechaLocal(m.fecha_utc)}</time>
              </div>)}
            </div>
            {conversacion?.estado === 'FINALIZADA' ?
              <p className={styles.aviso}>Servicio finalizado. Puedes consultar los mensajes, pero el chat está cerrado.</p> :
              <form className={styles.compositor} onSubmit={enviar}>
                <label htmlFor="chat-mensaje">Escribir mensaje (máximo 500 caracteres)</label>
                <textarea id="chat-mensaje" rows="3" maxLength="500" value={texto}
                  onChange={e => setTexto(e.target.value)} placeholder="Escribe tu mensaje..." />
                <button type="submit" disabled={enviando || !texto.trim()}>
                  {enviando ? 'Enviando...' : 'Enviar mensaje'}
                </button>
              </form>}
          </div>
        </div>
      )}
    </section>
  );
}
