import { useEffect, useState } from 'react';
import { guardarDisponibilidad, obtenerDisponibilidad } from '../../services/disponibilidadService';
import styles from './DisponibilidadUniversitario.module.css';

const DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
const VACIO = { dia_semana: 0, hora_inicio: '09:00', hora_fin: '12:00' };

export default function DisponibilidadUniversitario() {
  const [franjas, setFranjas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    let activo = true;
    obtenerDisponibilidad().then(data => {
      if (activo) setFranjas(data);
    }).catch(e => {
      if (activo) setError(e.message || 'No se pudo cargar la disponibilidad.');
    }).finally(() => { if (activo) setCargando(false); });
    return () => { activo = false; };
  }, []);

  function cambiar(i, campo, value) {
    setFranjas(antes => antes.map((f, j) => j === i
      ? { ...f, [campo]: campo === 'dia_semana' ? Number(value) : value } : f));
    setMensaje('');
  }
  function agregar() {
    if (franjas.length >= 21) return;
    setFranjas(antes => [...antes, { ...VACIO }]);
    setMensaje('');
  }
  function quitar(i) {
    setFranjas(antes => antes.filter((_, j) => i !== j));
    setMensaje('');
  }
  async function guardar(e) {
    e.preventDefault();
    if (guardando) return;
    setGuardando(true);
    setMensaje('');
    setError('');
    try {
      const guardadas = await guardarDisponibilidad(franjas);
      setFranjas(guardadas);
      setMensaje('Disponibilidad semanal guardada en SQL Server.');
    } catch (err) {
      setError(err.message || 'No fue posible guardar la disponibilidad.');
    } finally { setGuardando(false); }
  }
  return (
    <section className={styles.contenedor} aria-labelledby="disp-titulo">
      <h2 id="disp-titulo">📅 Mi disponibilidad semanal</h2>
      <p>Indica los días y las horas en que habitualmente puedes ayudar. Se utiliza horario local de Chile.</p>
      <p className={styles.advertencia}>Esta agenda es informativa: no confirma ni asigna tareas automáticamente. Los compromisos se coordinan mediante las solicitudes aceptadas.</p>
      {error && <p role="alert" className={styles.error}>{error}</p>}
      {mensaje && <p role="status" className={styles.exito}>{mensaje}</p>}
      {cargando ? <p role="status">Cargando disponibilidad...</p> : (
        <form onSubmit={guardar} className={styles.formulario}>
          {franjas.length === 0 && <p className={styles.vacio}>No tienes horarios registrados. Agrega una franja para comenzar.</p>}
          {franjas.map((franja, i) => (
            <fieldset className={styles.franja} key={i}>
              <legend>Franja {i + 1}</legend>
              <label>Día
                <select value={franja.dia_semana} onChange={e => cambiar(i, 'dia_semana', e.target.value)} disabled={guardando}>
                  {DIAS.map((nombre, dia) => <option key={dia} value={dia}>{nombre}</option>)}
                </select>
              </label>
              <label>Desde
                <input type="time" value={franja.hora_inicio} onChange={e => cambiar(i, 'hora_inicio', e.target.value)} disabled={guardando} required />
              </label>
              <label>Hasta
                <input type="time" value={franja.hora_fin} onChange={e => cambiar(i, 'hora_fin', e.target.value)} disabled={guardando} required />
              </label>
              <button className={styles.quitar} type="button" onClick={() => quitar(i)} disabled={guardando} aria-label={`Quitar franja ${i + 1}`}>Quitar</button>
            </fieldset>
          ))}
          <div className={styles.botones}>
            <button type="button" onClick={agregar} disabled={guardando || franjas.length >= 21}>+ Añadir horario</button>
            <button className={styles.guardar} type="submit" disabled={guardando}>{guardando ? 'Guardando...' : 'Guardar disponibilidad'}</button>
          </div>
          <small>Máximo 21 franjas semanales, de al menos 30 minutos y sin superposiciones. Guardar sin franjas significa que no tienes disponibilidad registrada.</small>
        </form>
      )}
    </section>
  );
}
