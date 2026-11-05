import { useEffect, useState } from 'react';
import { obtenerCalificaciones, calificarServicio } from '../../services/calificacionesService';
import styles from './CalificacionesServicios.module.css';

function Puntuacion({ valor }) {
  return <span aria-label={`${valor} de 5 estrellas`} className={styles.estrellas}>
    {'★'.repeat(valor)}{'☆'.repeat(5 - valor)}
  </span>;
}

export default function CalificacionesServicios({ usuario }) {
  const [servicios, setServicios] = useState([]);
  const [calificaciones, setCalificaciones] = useState({});
  const [comentarios, setComentarios] = useState({});
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(null);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');

  async function actualizar() {
    setCargando(true);
    setError('');
    try {
      setServicios(await obtenerCalificaciones());
    } catch (e) {
      setError(e.message || 'No pudimos consultar las calificaciones.');
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    let activo = true;
    obtenerCalificaciones().then(lista => { if (activo) setServicios(lista); })
      .catch(e => { if (activo) setError(e.message || 'No pudimos consultar las calificaciones.'); })
      .finally(() => { if (activo) setCargando(false); });
    return () => { activo = false; };
  }, []);

  async function guardar(evento, servicio) {
    evento.preventDefault();
    if (guardando !== null) return;
    const nota = Number(calificaciones[servicio.id] || '');
    if (!Number.isInteger(nota) || nota < 1 || nota > 5) {
      setError('Selecciona una calificación de 1 a 5 estrellas.');
      return;
    }
    const comentario = comentarios[servicio.id] || '';
    setGuardando(servicio.id);
    setError('');
    setMensaje('');
    try {
      await calificarServicio(servicio.id, nota, comentario);
      setMensaje(`Calificación del servicio #${servicio.id} guardada.`);
      setServicios(await obtenerCalificaciones());
    } catch (e) {
      setError(e.message || 'No fue posible guardar la calificación.');
    } finally {
      setGuardando(null);
    }
  }

  return <section className={styles.contenedor} aria-labelledby="calif-titulo">
    <div className={styles.encabezado}>
      <div>
        <h2 id="calif-titulo">Calificaciones de servicios</h2>
        <p>Evalúa la experiencia después de que el servicio quede finalizado y confirmado.</p>
      </div>
      <button type="button" onClick={actualizar} disabled={cargando || guardando !== null}>Actualizar</button>
    </div>
    {usuario?.rol === 'FAMILIAR' && <p className={styles.aviso}>La persona adulta mayor y sus familiares autorizados comparten una evaluación por servicio. Solo puedes calificar mientras tu autorización esté vigente.</p>}
    {error && <p className={styles.error} role="alert">{error}</p>}
    {mensaje && <p className={styles.mensaje} role="status">{mensaje}</p>}
    {cargando && <p role="status">Consultando servicios finalizados...</p>}
    {!cargando && !error && servicios.length === 0 && <p className={styles.aviso}>Todavía no hay servicios finalizados para evaluar.</p>}
    <div className={styles.lista}>
      {servicios.map(servicio => <article key={servicio.id} className={styles.tarjeta}>
        <h3>{servicio.servicio} · #{servicio.id}</h3>
        <p><strong>Persona a evaluar:</strong> {servicio.persona_evaluada}</p>
        {servicio.mi_calificacion
          ? <div className={styles.evaluacion}><strong>Tu evaluación</strong>
            <Puntuacion valor={servicio.mi_calificacion.puntaje}/>
            {servicio.mi_calificacion.comentario && <p>{servicio.mi_calificacion.comentario}</p>}
          </div>
          : <form onSubmit={e => guardar(e, servicio)} className={styles.formulario}>
            <label htmlFor={`calif-${servicio.id}`}>Califica de 1 a 5 estrellas</label>
            <select id={`calif-${servicio.id}`} required value={calificaciones[servicio.id] || ''}
              onChange={e => setCalificaciones(actual => ({...actual, [servicio.id]: e.target.value}))}>
              <option value="">Seleccionar puntuación</option>
              {[1,2,3,4,5].map(v => <option key={v} value={v}>{v} {v === 1 ? 'estrella' : 'estrellas'}</option>)}
            </select>
            <label htmlFor={`opinion-${servicio.id}`}>Comentario opcional (máximo 300 caracteres)</label>
            <textarea id={`opinion-${servicio.id}`} rows={3} maxLength={300}
              value={comentarios[servicio.id] || ''}
              onChange={e => setComentarios(actual => ({...actual, [servicio.id]: e.target.value}))}
              placeholder="Cuenta brevemente cómo fue la experiencia, sin datos privados."/>
            <button type="submit" disabled={guardando !== null}>{guardando === servicio.id ? 'Guardando...' : 'Guardar calificación'}</button>
          </form>}
        {servicio.calificacion_recibida && <div className={styles.evaluacion}>
          <strong>Calificación recibida</strong>
          <Puntuacion valor={servicio.calificacion_recibida.puntaje}/>
          {servicio.calificacion_recibida.comentario && <p>{servicio.calificacion_recibida.comentario}</p>}
        </div>}
      </article>)}
    </div>
  </section>;
}
