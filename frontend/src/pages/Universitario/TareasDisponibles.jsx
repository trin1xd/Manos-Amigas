import { useCallback, useEffect, useState } from 'react';
import dash from '../../components/dashboard/DashboardLayout.module.css';
import styles from './UniversitarioPaneles.module.css';
import {
  esErrorDeSesion,
  getMisPostulaciones,
  getSolicitudesDisponibles,
  postular,
} from '../../services/postulacionesService';
import { formatearDuracion, formatearFechaHora } from './formatoFecha';
import { COMISION_PLATAFORMA_PORCENTAJE, RANGO_PRECIO_TEXTO, pagoEstudianteReferencialPara } from '../../utils/precioReferencial';

const ETIQUETAS_VERIFICACION = {
  PENDIENTE_VERIFICACION: 'Pendiente de verificación',
  RECHAZADO: 'Verificación rechazada',
  SUSPENDIDO: 'Verificación suspendida',
};

export default function TareasDisponibles({ usuario, onLogout }) {
  const verificado = usuario?.estado_verificacion === 'VERIFICADO';

  const [tareas, setTareas] = useState([]);
  const [postuladas, setPostuladas] = useState(() => new Set());
  const [cargando, setCargando] = useState(verificado);
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [confirmandoId, setConfirmandoId] = useState(null);
  const [enviandoId, setEnviandoId] = useState(null);

  // Solo cambia el estado después de recibir la respuesta; el indicador de carga
  // se activa desde el botón "Actualizar" o con el valor inicial.
  const cargar = useCallback(async () => {
    try {
      const [lista, mias] = await Promise.all([
        getSolicitudesDisponibles(),
        getMisPostulaciones(),
      ]);
      setTareas(lista);
      setPostuladas(new Set(mias.map((p) => p.id_solicitud)));
      setError('');
    } catch (err) {
      if (esErrorDeSesion(err)) {
        return; // El evento global ya redirige a iniciar sesión.
      }
      setError(err.message || 'No pudimos cargar las tareas.');
    } finally {
      setCargando(false);
    }
  }, [onLogout]);

  useEffect(() => {
    // Sin perfil verificado el backend respondería 403: no se llama a la API.
    if (verificado) cargar();
  }, [verificado, cargar]);

  async function confirmarPostulacion(idSolicitud) {
    setEnviandoId(idSolicitud);
    setError('');
    setAviso('');
    try {
      await postular(idSolicitud);
      setPostuladas((previas) => new Set(previas).add(idSolicitud));
      setAviso('Tu postulación fue enviada. Puedes seguirla en "Mis postulaciones".');
    } catch (err) {
      if (esErrorDeSesion(err)) {
        return; // El evento global ya redirige a iniciar sesión.
      }
      setError(err.message || 'No pudimos enviar tu postulación.');
    } finally {
      setConfirmandoId(null);
      setEnviandoId(null);
    }
    // Refresca la lista y las postulaciones, tanto si salió bien como si no (por ejemplo 409).
    await cargar();
  }

  function actualizar() {
    setCargando(true);
    cargar();
  }

  if (!verificado) {
    const etiqueta = ETIQUETAS_VERIFICACION[usuario?.estado_verificacion] || 'Verificación sin información';
    return (
      <section className={`${dash.panel} ${dash.vacio}`} aria-labelledby="uni-oportunidades">
        <span className={dash.vacioIcono} aria-hidden="true">🧹</span>
        <h2 id="uni-oportunidades">Tareas disponibles</h2>
        <p>Primero necesitas un perfil verificado para ver las tareas y postular.</p>
        <span className={`${dash.estado} ${dash.estadoAlerta}`}>● {etiqueta}</span>
        <p className={dash.aviso}>No se muestran tareas ni datos personales de adultos mayores mientras tu perfil no esté verificado.</p>
      </section>
    );
  }

  return (
    <section className={dash.panel} aria-labelledby="uni-oportunidades" aria-busy={cargando}>
      <div className={styles.encabezado}>
        <h2 id="uni-oportunidades">Tareas disponibles</h2>
        <button type="button" className={styles.botonSecundario} onClick={actualizar} disabled={cargando}>
          {cargando ? 'Actualizando...' : 'Actualizar'}
        </button>
      </div>
      <p className={styles.descripcion}>
        Solicitudes abiertas de adultos mayores. Por privacidad solo ves el tipo de tarea, la fecha y la duración.
      </p>

      {error && <p className={styles.mensajeError} role="alert">{error}</p>}
      {aviso && <p className={styles.mensajeOk} role="status" aria-live="polite">{aviso}</p>}

      {cargando && tareas.length === 0 && (
        <p className={styles.mensajeInfo} role="status">Cargando tareas...</p>
      )}

      {!cargando && !error && tareas.length === 0 && (
        <p className={styles.mensajeInfo} role="status">No hay tareas disponibles por ahora.</p>
      )}

      {tareas.length > 0 && (
        <ul className={styles.lista}>
          {tareas.map((tarea) => {
            const yaPostulo = postuladas.has(tarea.id);
            const confirmando = confirmandoId === tarea.id;
            const enviando = enviandoId === tarea.id;
            return (
              <li key={tarea.id} className={styles.item}>
                <h3 className={styles.itemTitulo}>{tarea.servicio}</h3>
                <dl className={styles.meta}>
                  <div><dt>Fecha:</dt><dd>{formatearFechaHora(tarea.fecha_solicitada)}</dd></div>
                  <div><dt>Duración:</dt><dd>{formatearDuracion(tarea.duracion_horas)}</dd></div>
                  <div><dt>Pago estimado para ti:</dt><dd>{pagoEstudianteReferencialPara(tarea.duracion_horas).monto}</dd></div>
                </dl>
                <div className={styles.acciones}>
                  {yaPostulo && (
                    <span className={`${dash.estado} ${dash.estadoOk}`}>✓ Postulaste a esta tarea</span>
                  )}
                  {!yaPostulo && !confirmando && (
                    <button
                      type="button"
                      className={styles.botonPrincipal}
                      onClick={() => { setConfirmandoId(tarea.id); setAviso(''); setError(''); }}
                      disabled={enviandoId !== null}
                    >
                      Postular
                    </button>
                  )}
                  {!yaPostulo && confirmando && (
                    <div className={styles.confirmacion} role="group" aria-label={`Confirmar postulación a ${tarea.servicio}`}>
                      <p>¿Confirmas que quieres postular a esta tarea?</p>
                      <div className={styles.acciones}>
                        <button
                          type="button"
                          className={styles.botonPrincipal}
                          onClick={() => confirmarPostulacion(tarea.id)}
                          disabled={enviando}
                        >
                          {enviando ? 'Enviando...' : 'Sí, postular'}
                        </button>
                        <button
                          type="button"
                          className={styles.botonSecundario}
                          onClick={() => setConfirmandoId(null)}
                          disabled={enviando}
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <p className={styles.notaPago}>
        El pago estimado es una propuesta que se está validando: el precio de referencia de {RANGO_PRECIO_TEXTO} por tarea de 1 a 2 horas (según el esfuerzo), menos {COMISION_PLATAFORMA_PORCENTAJE}% de comisión de la plataforma.
      </p>
      <p className={dash.aviso}>Manos Amigas no presta servicios médicos ni realiza pagos desde este panel. Postular no asegura la tarea: la persona que la pidió decide.</p>
    </section>
  );
}
