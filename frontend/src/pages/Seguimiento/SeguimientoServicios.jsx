import { useEffect, useState } from 'react';
import { obtenerSeguimiento, registrarAccionSeguimiento, obtenerQrLlegada } from '../../services/seguimientoService';
import styles from './SeguimientoServicios.module.css';

const ETIQUETAS = {
  PENDIENTE: 'Pendiente de asignación',
  ASIGNADA: 'Asignada',
  EN_CURSO: 'En curso',
  FINALIZADA: 'Finalizada',
  CANCELADA: 'Cancelada',
};
const ACCIONES = {
  LLEGADA: 'Registrar llegada',
  INICIO: 'Iniciar servicio',
  TERMINO: 'Informar término del trabajo',
  CONFIRMAR: 'Confirmar finalización',
};

function fechaLocal(value) {
  if (!value) return 'Pendiente';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value :
    new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
}

function siguienteAccion(servicio, rol) {
  const s = servicio;
  if (rol === 'UNIVERSITARIO') {
    if (s.estado === 'ASIGNADA' && !s.fecha_llegada_utc) return 'LLEGADA';
    if (s.estado === 'ASIGNADA' && s.fecha_llegada_utc && !s.fecha_inicio_utc) return 'INICIO';
    if (s.estado === 'EN_CURSO' && s.fecha_inicio_utc && !s.fecha_termino_utc) return 'TERMINO';
  } else if (['ADULTO_MAYOR', 'FAMILIAR'].includes(rol)) {
    if (s.estado === 'EN_CURSO' && s.fecha_termino_utc && !s.fecha_confirmacion_utc) return 'CONFIRMAR';
  }
  return null;
}

export default function SeguimientoServicios({ usuario }) {
  const [servicios, setServicios] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [accionando, setAccionando] = useState(null);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [qr, setQr] = useState(null);
  const [cargandoQr, setCargandoQr] = useState(null);
  const rol = usuario?.rol;

  async function cargar() {
    setCargando(true);
    setError('');
    try {
      setServicios(await obtenerSeguimiento());
    } catch (err) {
      setError(err.message || 'No pudimos obtener el seguimiento.');
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    let activo = true;
    obtenerSeguimiento().then(lista => {
      if (activo) setServicios(lista);
    }).catch(err => {
      if (activo) setError(err.message || 'No pudimos consultar los servicios.');
    }).finally(() => {
      if (activo) setCargando(false);
    });
    return () => { activo = false; };
  }, []);

  async function mostrarQr(servicio) {
    setCargandoQr(servicio.id);
    setError('');
    try {
      const resultado = await obtenerQrLlegada(servicio.id);
      setQr({ id: servicio.id, imagen: resultado.qr_svg });
    } catch (err) {
      setError(err.message || 'No fue posible generar el QR.');
    } finally {
      setCargandoQr(null);
    }
  }

  async function ejecutar(servicio, accion) {
    if (!window.confirm(`¿Confirmas "${ACCIONES[accion]}" para el servicio #${servicio.id}?`)) return;
    setAccionando(servicio.id);
    setError('');
    setMensaje('');
    try {
      await registrarAccionSeguimiento(servicio.id, accion);
      setQr(null);
      setMensaje('Acción de seguimiento guardada correctamente.');
      await cargar();
    } catch (err) {
      setError(err.message || 'No fue posible guardar el cambio.');
    } finally {
      setAccionando(null);
    }
  }

  return (
    <section className={styles.contenedor} aria-labelledby="seguimiento-titulo">
      <div className={styles.encabezado}>
        <div>
          <h2 id="seguimiento-titulo">Seguimiento e historial</h2>
          <p>Consulta el estado de tus servicios y registra cada etapa.</p>
        </div>
        <button type="button" onClick={cargar} disabled={cargando || accionando !== null}>
          {cargando ? 'Cargando...' : 'Actualizar'}
        </button>
      </div>
      {rol === 'UNIVERSITARIO' && <p className={styles.aviso}>Las horas de llegada e inicio son declaraciones del estudiante, no una validación por GPS.</p>}
      {error && <p className={styles.error} role="alert">{error}</p>}
      {mensaje && <p className={styles.exito} role="status">{mensaje}</p>}
      {cargando && <p role="status">Consultando información...</p>}
      {!cargando && servicios.length === 0 && (
        <div className={styles.vacio}>Todavía no hay servicios para mostrar. Cuando se acepte una postulación, aparecerá aquí.</div>
      )}
      <div className={styles.lista}>
        {servicios.map(servicio => {
          const accion = siguienteAccion(servicio, rol);
          return (
            <article className={styles.tarjeta} key={servicio.id}>
              <div className={styles.tituloFila}>
                <h3>{servicio.servicio} · #{servicio.id}</h3>
                <span className={styles.estado}>{ETIQUETAS[servicio.estado] || servicio.estado}</span>
              </div>
              {servicio.adulto_nombre && <p><strong>Adulto mayor:</strong> {servicio.adulto_nombre}</p>}
              {servicio.estudiante_nombre && <p><strong>Universitario:</strong> {servicio.estudiante_nombre}</p>}
              <p><strong>Programado:</strong> {fechaLocal(servicio.fecha_solicitada)}</p>
              <dl className={styles.fechas}>
                <div><dt>Llegada</dt><dd>{fechaLocal(servicio.fecha_llegada_utc)}</dd></div>
                <div><dt>Inicio</dt><dd>{fechaLocal(servicio.fecha_inicio_utc)}</dd></div>
                <div><dt>Término informado</dt><dd>{fechaLocal(servicio.fecha_termino_utc)}</dd></div>
                <div><dt>Confirmación</dt><dd>{fechaLocal(servicio.fecha_confirmacion_utc)}</dd></div>
              </dl>
              {['ADULTO_MAYOR', 'FAMILIAR'].includes(rol) && servicio.estado === 'ASIGNADA'
                && !servicio.fecha_llegada_utc && (
                <div className={styles.bloqueQr}>
                  <p><strong>Confirmar llegada con QR</strong></p>
                  <p>Muestra este código al estudiante cuando llegue. Deberá abrirlo desde su teléfono e iniciar sesión.</p>
                  <button type="button" className={styles.botonQr} onClick={() => mostrarQr(servicio)}
                    disabled={cargandoQr !== null}>
                    {cargandoQr === servicio.id ? 'Generando...' : qr?.id === servicio.id ? 'Renovar QR' : 'Mostrar QR de llegada'}
                  </button>
                  {qr?.id === servicio.id && (
                    <div className={styles.imagenQr}>
                      <img src={qr.imagen} alt={`QR temporal para confirmar la llegada al servicio #${servicio.id}`} width="240" height="240" />
                      <small>Caduca en 10 minutos. Solo sirve para este servicio y una llegada; si vence, pulsa «Renovar QR».</small>
                    </div>
                  )}
                </div>
              )}
              {accion && <button type="button" className={styles.accion} disabled={accionando !== null || cargando}
                onClick={() => ejecutar(servicio, accion)}>
                {accionando === servicio.id ? 'Guardando...' : accion === 'LLEGADA' ? 'Registrar llegada manualmente' : ACCIONES[accion]}
              </button>}
              {servicio.estado === 'FINALIZADA' && (
                <p className={styles.exito}>Servicio finalizado y confirmado. Puedes ir a Calificaciones para evaluar la experiencia.</p>
              )}
              {servicio.estado === 'EN_CURSO' && servicio.fecha_termino_utc && rol === 'UNIVERSITARIO' && (
                <p className={styles.aviso}>Esperando confirmación del adulto mayor o familiar autorizado.</p>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
