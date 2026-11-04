import { useEffect, useState } from 'react';
import { decidirVerificacion, obtenerUniversitariosRevision } from '../../services/verificacionAdminService';
import styles from './AdminVerificaciones.module.css';

const ESTADO = {
  PENDIENTE_VERIFICACION: 'Pendiente de revisión',
  VERIFICADO: 'Habilitado para pruebas',
  RECHAZADO: 'Rechazado',
  SUSPENDIDO: 'Suspendido',
};

function Estudiante({ estudiante, onDecision, ocupado }) {
  const [accion, setAccion] = useState('');
  const [observacion, setObservacion] = useState('');
  const [confirmacion, setConfirmacion] = useState(false);
  const [error, setError] = useState('');
  const pendiente = estudiante.estado_verificacion === 'PENDIENTE_VERIFICACION';

  async function enviar(evento) {
    evento.preventDefault();
    if (!accion || observacion.trim().length < 12 || (accion === 'APROBAR' && !confirmacion)) {
      setError('Indica la decisión, escribe al menos 12 caracteres y confirma el alcance de pruebas al aprobar.');
      return;
    }
    const verbo = accion === 'APROBAR' ? 'habilitar para pruebas' : 'rechazar';
    if (!window.confirm(`¿Confirmas ${verbo} la cuenta de ${estudiante.nombre}?`)) return;
    setError('');
    const ok = await onDecision(estudiante.id, accion, observacion.trim(), confirmacion);
    if (ok) {
      setAccion('');
      setObservacion('');
      setConfirmacion(false);
    }
  }

  return (
    <article className={styles.estudiante}>
      <div className={styles.filaTitulo}>
        <div>
          <h3>{estudiante.nombre}</h3>
          <p>{estudiante.universidad} · {estudiante.carrera} · Año {estudiante.anio_cursa}</p>
        </div>
        <span className={styles.estado}>{ESTADO[estudiante.estado_verificacion] || estudiante.estado_verificacion}</span>
      </div>
      <dl className={styles.detalles}>
        <div><dt>Correo de cuenta</dt><dd>{estudiante.email}</dd></div>
        <div><dt>Correo institucional declarado</dt><dd>{estudiante.correo_institucional}</dd></div>
        <div><dt>Correo institucional confirmado</dt><dd>{estudiante.correo_institucional_verificado ? 'Sí' : 'No'}</dd></div>
      </dl>
      {pendiente && (
        <form className={styles.formulario} onSubmit={enviar}>
          <label>
            Decisión administrativa de pruebas
            <select value={accion} onChange={e => { setAccion(e.target.value); setError(''); }} required disabled={ocupado}>
              <option value="">Selecciona una opción</option>
              <option value="APROBAR">Habilitar para pruebas</option>
              <option value="RECHAZAR">Rechazar</option>
            </select>
          </label>
          <label>
            Observación (obligatoria)
            <textarea value={observacion} onChange={e => setObservacion(e.target.value)}
              minLength={12} maxLength={500} rows={3} required disabled={ocupado}
              placeholder="Explica brevemente la decisión sin incluir datos sensibles." />
          </label>
          {accion === 'APROBAR' && (
            <label className={styles.check}>
              <input type="checkbox" checked={confirmacion} disabled={ocupado}
                onChange={e => setConfirmacion(e.target.checked)} />
              <span>Confirmo que habilito esta cuenta únicamente para pruebas locales; no he certificado su identidad ni antecedentes.</span>
            </label>
          )}
          {error && <p className={styles.error} role="alert">{error}</p>}
          <button type="submit" disabled={ocupado || !accion}>{ocupado ? 'Guardando...' : 'Registrar decisión'}</button>
        </form>
      )}
    </article>
  );
}

export default function AdminVerificaciones({ usuario, onLogout }) {
  const [estudiantes, setEstudiantes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [ocupadoId, setOcupadoId] = useState(null);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [filtro, setFiltro] = useState('pendientes');

  async function cargar() {
    setCargando(true);
    setError('');
    try {
      setEstudiantes(await obtenerUniversitariosRevision());
    } catch (err) {
      setError(err.message || 'No se pudo consultar la lista.');
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    let activo = true;
    obtenerUniversitariosRevision().then(datos => {
      if (activo) setEstudiantes(datos);
    }).catch(err => {
      if (activo) setError(err.message || 'No se pudo consultar la lista.');
    }).finally(() => {
      if (activo) setCargando(false);
    });
    return () => { activo = false; };
  }, []);

  async function decidir(id, accion, observacion, confirmacion) {
    setOcupadoId(id);
    setError('');
    setMensaje('');
    try {
      const actualizado = await decidirVerificacion(id, accion, observacion, confirmacion);
      setEstudiantes(previas => previas.map(item =>
        item.id === id ? { ...item, estado_verificacion: actualizado.estado_verificacion } : item
      ));
      setMensaje('Decisión registrada en la base de datos y auditoría.');
      return true;
    } catch (err) {
      setError(err.message || 'No fue posible guardar la decisión.');
      return false;
    } finally {
      setOcupadoId(null);
    }
  }

  const visibles = filtro === 'pendientes'
    ? estudiantes.filter(e => e.estado_verificacion === 'PENDIENTE_VERIFICACION')
    : estudiantes;
  const pendientes = estudiantes.filter(e => e.estado_verificacion === 'PENDIENTE_VERIFICACION').length;

  return (
    <div className={styles.pagina}>
      <header className={styles.barra}>
        <strong>♥ Manos Amigas · Administración de pruebas</strong>
        <button onClick={onLogout} type="button" className={styles.salir}>Cerrar sesión</button>
      </header>
      <main className={styles.contenedor}>
        <p className={styles.eyebrow}>Panel restringido · Rol ADMIN</p>
        <h1>Revisión de universitarios</h1>
        <p className={styles.subtitulo}>Sesión de {usuario?.nombre || 'Administración'} · {pendientes} pendiente(s)</p>
        <aside className={styles.alerta} aria-label="Advertencia de seguridad">
          <strong>Exclusivamente para desarrollo y pruebas.</strong>
          <p>Esta pantalla NO valida cédulas, antecedentes, selfies ni condición de alumno regular. Una aprobación solo habilita un usuario ficticio para comprobar el flujo del sistema. No utilizar con personas ni servicios reales.</p>
        </aside>
        <div className={styles.barraAcciones}>
          <label>Mostrar
            <select value={filtro} onChange={e => setFiltro(e.target.value)}>
              <option value="pendientes">Pendientes</option>
              <option value="todos">Todas las cuentas</option>
            </select>
          </label>
          <button type="button" onClick={cargar} disabled={cargando || ocupadoId !== null}>
            {cargando ? 'Cargando...' : 'Actualizar'}
          </button>
        </div>
        {error && <p className={styles.error} role="alert">{error}</p>}
        {mensaje && <p className={styles.ok} role="status">{mensaje}</p>}
        {cargando && <p role="status">Consultando datos...</p>}
        {!cargando && visibles.length === 0 && <p className={styles.vacio}>No hay universitarios en esta categoría.</p>}
        <div className={styles.lista}>
          {visibles.map(e => <Estudiante key={e.id} estudiante={e} ocupado={ocupadoId !== null} onDecision={decidir} />)}
        </div>
      </main>
    </div>
  );
}
