import { useEffect, useState } from 'react';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import SeguimientoServicios from '../Seguimiento/SeguimientoServicios';
import CalificacionesServicios from '../Calificaciones/CalificacionesServicios';
import ChatServicios from '../Chat/ChatServicios';
import Notificaciones from '../Notificaciones/Notificaciones';
import AgendaServicios from '../Agenda/AgendaServicios';
import { precioReferencialPara } from '../../utils/precioReferencial';
import FichaEstudiante, { NotaFichaEstudiante } from '../../components/FichaEstudiante/FichaEstudiante';
import dash from '../../components/dashboard/DashboardLayout.module.css';
import styles from './FamiliarDashboardOperativo.module.css';
import {
  obtenerAdultosVinculados,
  obtenerSolicitudesFamiliares,
  obtenerServiciosFamiliares,
  crearSolicitudFamiliar,
  obtenerPostulantesFamiliares,
  aceptarPostulanteFamiliar,
  cancelarSolicitudFamiliar,
} from '../../services/familiarService';

const NAVEGACION = [
  { id: 'inicio', nombre: 'Inicio', icono: '🏠' },
  { id: 'adultos', nombre: 'Personas a cargo', icono: '💛' },
  { id: 'solicitudes', nombre: 'Solicitudes', icono: '📋' },
  { id: 'nueva', nombre: 'Pedir ayuda', icono: '🤝' },
  { id: 'seguimiento', nombre: 'Seguimiento', icono: '🕒' },
  { id: 'calificaciones', nombre: 'Calificaciones', icono: '⭐' },
  { id: 'chat', nombre: 'Chat', icono: '💬' },
  { id: 'avisos', nombre: 'Avisos', icono: '🔔' },
  { id: 'agenda', nombre: 'Agenda', icono: '📆' },
  { id: 'perfil', nombre: 'Mi perfil', icono: '👤' },
];

function fechaLegible(value) {
  if (!value) return 'Sin fecha';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium', timeStyle: 'short' }).format(date);
}

function fechaHoy() {
  const d = new Date();
  return [d.getFullYear(), String(d.getMonth() + 1).padStart(2, '0'), String(d.getDate()).padStart(2, '0')].join('-');
}

const FORM_INICIAL = {
  id_adulto_mayor: '', id_servicio: '', fecha: '', hora: '', duracion_horas: '2', descripcion: '',
};

export default function FamiliarDashboardOperativo({ usuario, onLogout }) {
  const [vista, setVista] = useState('inicio');
  const [adultos, setAdultos] = useState([]);
  const [servicios, setServicios] = useState([]);
  const [solicitudes, setSolicitudes] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [version, setVersion] = useState(0);
  const [form, setForm] = useState(FORM_INICIAL);
  const precio = precioReferencialPara(form.duracion_horas);
  const [enviando, setEnviando] = useState(false);
  const [idConPostulantes, setIdConPostulantes] = useState(null);
  const [postulantes, setPostulantes] = useState([]);
  const [cargandoPostulantes, setCargandoPostulantes] = useState(false);
  const [errorPostulantes, setErrorPostulantes] = useState('');
  const [accionEnCurso, setAccionEnCurso] = useState(false);

  // Al entrar en la pestaña correspondiente, sincronizar con SQL Server a través de Flask.
  useEffect(() => {
    if (!['inicio', 'adultos', 'solicitudes', 'nueva'].includes(vista)) return;
    let activo = true;
    setCargando(true);
    setError('');

    async function cargar() {
      try {
        if (vista === 'inicio' || vista === 'adultos' || vista === 'nueva') {
          const lista = await obtenerAdultosVinculados();
          if (activo) setAdultos(lista);
        }
        if (vista === 'solicitudes') {
          const lista = await obtenerSolicitudesFamiliares();
          if (activo) setSolicitudes(lista);
        }
        if (vista === 'nueva') {
          const lista = await obtenerServiciosFamiliares();
          if (activo) setServicios(lista);
        }
      } catch (err) {
        if (activo) setError(err.message || 'No pudimos cargar los datos.');
      } finally {
        if (activo) setCargando(false);
      }
    }
    cargar();
    return () => { activo = false; };
  }, [vista, version]);

  function cambiarVista(nueva) {
    setVista(nueva);
    setError('');
    setMensaje('');
    setIdConPostulantes(null);
    setPostulantes([]);
    setErrorPostulantes('');
  }

  function actualizar() { setVersion(n => n + 1); }

  function editarFormulario(evento) {
    const { name, value } = evento.target;
    setForm(actual => ({ ...actual, [name]: value }));
    setError('');
  }

  async function enviarSolicitud(e) {
    e.preventDefault();
    if (enviando) return;
    const inicio = new Date(`${form.fecha}T${form.hora}:00`);
    if (Number.isNaN(inicio.getTime()) || inicio.getTime() <= Date.now()) {
      setError('Debes elegir una fecha y hora futuras.');
      return;
    }
    if (inicio.getTime() > Date.now() + 366 * 86400000) {
      setError('La fecha debe estar dentro de los próximos 366 días.');
      return;
    }
    if (form.descripcion.trim().length < 10 || form.descripcion.trim().length > 500) {
      setError('La descripción debe contener entre 10 y 500 caracteres.');
      return;
    }
    if (!window.confirm('¿Confirmas que quieres guardar esta solicitud para el adulto mayor seleccionado?')) return;
    setEnviando(true);
    setError('');
    try {
      const nueva = await crearSolicitudFamiliar({
        id_adulto_mayor: Number(form.id_adulto_mayor),
        id_servicio: Number(form.id_servicio),
        fecha: form.fecha,
        hora: form.hora,
        duracion_horas: Number(form.duracion_horas),
        descripcion: form.descripcion.trim(),
      });
      setForm(FORM_INICIAL);
      cambiarVista('solicitudes');
      setMensaje(`Solicitud #${nueva.id} guardada en SQL Server. Estado: ${nueva.estado}.`);
    } catch (err) {
      setError(err.message || 'No se pudo guardar la solicitud.');
    } finally {
      setEnviando(false);
    }
  }

  async function alternarPostulantes(idSolicitud) {
    if (idConPostulantes === idSolicitud) {
      setIdConPostulantes(null);
      setPostulantes([]);
      return;
    }
    setIdConPostulantes(idSolicitud);
    setCargandoPostulantes(true);
    setErrorPostulantes('');
    setPostulantes([]);
    try {
      setPostulantes(await obtenerPostulantesFamiliares(idSolicitud));
    } catch (err) {
      setErrorPostulantes(err.message || 'No fue posible ver los postulantes.');
    } finally {
      setCargandoPostulantes(false);
    }
  }

  async function aceptar(idSolicitud, idPostulacion) {
    if (!window.confirm('¿Aceptar a este estudiante y asignar la tarea?')) return;
    setAccionEnCurso(true);
    setErrorPostulantes('');
    try {
      await aceptarPostulanteFamiliar(idSolicitud, idPostulacion);
      setIdConPostulantes(null);
      setPostulantes([]);
      setMensaje('Postulación aceptada. La solicitud ahora está asignada.');
      actualizar();
    } catch (err) {
      setErrorPostulantes(err.message || 'No fue posible aceptar la postulación.');
    } finally {
      setAccionEnCurso(false);
    }
  }

  async function cancelar(idSolicitud) {
    if (!window.confirm('¿Cancelar esta solicitud? Esto cambiará su estado para las personas involucradas.')) return;
    setAccionEnCurso(true);
    setError('');
    try {
      await cancelarSolicitudFamiliar(idSolicitud);
      setIdConPostulantes(null);
      setMensaje(`Solicitud #${idSolicitud} cancelada.`);
      actualizar();
    } catch (err) {
      setError(err.message || 'No fue posible cancelar la solicitud.');
    } finally {
      setAccionEnCurso(false);
    }
  }

  return (
    <DashboardLayout
      usuario={usuario}
      onLogout={onLogout}
      tituloRol="Familiar / acompañante"
      subtitulo="Organiza el apoyo para tus seres queridos con su autorización."
      navegacion={NAVEGACION}
      vista={vista}
      onCambiarVista={cambiarVista}
    >
      {vista === 'inicio' && (
        <>
          <section className={dash.hero} aria-labelledby="fam-titulo-inicio">
            <div>
              <p className={dash.heroEyebrow}>Cuidar también es acompañar</p>
              <h2 id="fam-titulo-inicio">Más tranquilidad para tu familia</h2>
              <p>Coordina tareas del día a día para un adulto mayor que te haya autorizado.</p>
            </div>
            <span className={dash.heroIcono} aria-hidden="true">💛</span>
          </section>
          <section className={dash.panel} aria-labelledby="fam-vinculos-resumen">
            <div className={styles.encabezado}>
              <h2 id="fam-vinculos-resumen">Personas vinculadas a tu cuenta</h2>
              <button type="button" className={styles.botonSecundario} onClick={actualizar} disabled={cargando}>Actualizar</button>
            </div>
            {cargando && <p role="status">Consultando tus vínculos...</p>}
            {error && <p role="alert" className={styles.error}>{error}</p>}
            {!cargando && !error && (
              <p>{adultos.length === 0
                ? 'Todavía no tienes adultos mayores vinculados. La autorización debe realizarla el adulto mayor desde su perfil.'
                : `Tienes ${adultos.length} persona(s) vinculada(s) y puedes consultar sus solicitudes.`}</p>
            )}
          </section>
          <section className={dash.separacion}>
            <h2 className={dash.tituloSeccion}>¿Qué quieres hacer?</h2>
            <div className={dash.rejilla}>
              <article className={dash.tarjeta}>
                <span className={dash.tarjetaIcono} aria-hidden="true">💛</span>
                <h3>Personas a cargo</h3>
                <p>Consulta quién te autorizó a gestionar solicitudes.</p>
                <button type="button" className={dash.tarjetaBoton} onClick={() => cambiarVista('adultos')}>Ver personas a cargo →</button>
              </article>
              <article className={dash.tarjeta}>
                <span className={dash.tarjetaIcono} aria-hidden="true">📋</span>
                <h3>Seguimiento</h3>
                <p>Consulta las solicitudes de tus familiares vinculados.</p>
                <button type="button" className={dash.tarjetaBoton} onClick={() => cambiarVista('solicitudes')}>Ver solicitudes →</button>
              </article>
            </div>
          </section>
        </>
      )}

      {vista === 'adultos' && (
        <section className={dash.panel} aria-labelledby="fam-adultos">
          <div className={styles.encabezado}>
            <h2 id="fam-adultos">Personas a cargo</h2>
            <button type="button" className={styles.botonSecundario} onClick={actualizar} disabled={cargando}>Actualizar</button>
          </div>
          <p>Solo aparecen adultos mayores que te han autorizado desde su cuenta.</p>
          {cargando && <p role="status">Cargando personas...</p>}
          {error && <p className={styles.error} role="alert">{error}</p>}
          {!cargando && !error && adultos.length === 0 && <p className={styles.aviso}>Aún no tienes vínculos. Pide al adulto mayor que te autorice en «Mi perfil», usando tu correo de cuenta familiar.</p>}
          {!cargando && !error && adultos.length > 0 && (
            <ul className={styles.lista}>
              {adultos.map(adulto => (
                <li key={adulto.id} className={styles.item}>
                  <strong>{adulto.nombre}</strong>
                  <p>Parentesco registrado: {adulto.parentesco || 'Sin información'}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {vista === 'solicitudes' && (
        <section className={dash.panel} aria-labelledby="fam-solicitudes">
          <div className={styles.encabezado}>
            <h2 id="fam-solicitudes">Solicitudes de tus familiares</h2>
            <button type="button" className={styles.botonSecundario} onClick={actualizar} disabled={cargando || accionEnCurso}>Actualizar</button>
          </div>
          {mensaje && <p className={styles.exito} role="status">{mensaje}</p>}
          {error && <p className={styles.error} role="alert">{error}</p>}
          {cargando && <p role="status">Cargando solicitudes...</p>}
          {!cargando && !error && solicitudes.length === 0 && (
            <p>Aún no hay solicitudes en las cuentas vinculadas. Puedes crear una desde «Pedir ayuda» cuando exista una autorización.</p>
          )}
          {!cargando && !error && solicitudes.length > 0 && (
            <ul className={styles.lista}>
              {solicitudes.map(sol => (
                <li key={sol.id} className={styles.item}>
                  <div className={styles.encabezado}>
                    <h3>{sol.servicio} · #{sol.id}</h3>
                    <span className={styles.estado}>{sol.estado}</span>
                  </div>
                  <p><strong>Para:</strong> {sol.adulto_nombre || 'Adulto mayor autorizado'}</p>
                  <p><strong>Fecha:</strong> {fechaLegible(sol.fecha_solicitada)}</p>
                  <p><strong>Duración:</strong> {sol.duracion_horas ?? 'No indicada'} hora(s)</p>
                  <p><strong>Descripción:</strong> {sol.descripcion || 'Sin descripción'}</p>
                  <div className={styles.acciones}>
                    {sol.estado === 'PENDIENTE' && (
                      <button type="button" className={styles.botonSecundario} onClick={() => alternarPostulantes(sol.id)} disabled={accionEnCurso}>
                        {idConPostulantes === sol.id ? 'Ocultar postulantes' : 'Ver postulantes'}
                      </button>
                    )}
                    {['PENDIENTE', 'ASIGNADA'].includes(sol.estado) && (
                      <button type="button" className={styles.botonPeligro} onClick={() => cancelar(sol.id)} disabled={accionEnCurso}>
                        Cancelar solicitud
                      </button>
                    )}
                  </div>
                  {idConPostulantes === sol.id && (
                    <div className={styles.subpanel}>
                      <h4>Estudiantes postulados</h4>
                      {cargandoPostulantes && <p>Cargando postulantes...</p>}
                      {errorPostulantes && <p role="alert" className={styles.error}>{errorPostulantes}</p>}
                      {!cargandoPostulantes && !errorPostulantes && postulantes.length === 0 && <p>Aún no hay postulantes.</p>}
                      {!cargandoPostulantes && !errorPostulantes && postulantes.map(post => (
                        <div key={post.id} className={styles.filaPostulante}>
                          <FichaEstudiante postulacion={post} />
                          {post.estado === 'PENDIENTE' && (
                            <button type="button" className={styles.botonPrincipal} onClick={() => aceptar(sol.id, post.id)} disabled={accionEnCurso}>Aceptar</button>
                          )}
                        </div>
                      ))}
                      {!cargandoPostulantes && !errorPostulantes && postulantes.length > 0 && <NotaFichaEstudiante />}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {vista === 'nueva' && (
        <section className={dash.panel} aria-labelledby="fam-nueva">
          <h2 id="fam-nueva">Pedir ayuda para un adulto mayor</h2>
          <p>Solo puedes crear solicitudes para personas que te autorizaron desde su propia cuenta.</p>
          {cargando && <p role="status">Consultando los datos...</p>}
          {error && <p role="alert" className={styles.error}>{error}</p>}
          {!cargando && !error && adultos.length === 0 && <p className={styles.aviso}>Aún no puedes solicitar tareas: primero necesitas que el adulto mayor te autorice desde «Mi perfil».</p>}
          {!cargando && !error && adultos.length > 0 && servicios.length === 0 && <p>No hay servicios activos para solicitar.</p>}
          {!cargando && !error && adultos.length > 0 && servicios.length > 0 && (
            <form className={styles.formulario} onSubmit={enviarSolicitud}>
              <label htmlFor="f-adulto">Adulto mayor
                <select id="f-adulto" name="id_adulto_mayor" value={form.id_adulto_mayor} onChange={editarFormulario} required>
                  <option value="">Selecciona una persona</option>
                  {adultos.map(adulto => <option key={adulto.id} value={adulto.id}>{adulto.nombre}</option>)}
                </select>
              </label>
              <label htmlFor="f-servicio">Tipo de tarea
                <select id="f-servicio" name="id_servicio" value={form.id_servicio} onChange={editarFormulario} required>
                  <option value="">Selecciona un servicio</option>
                  {servicios.map(servicio => <option key={servicio.id} value={servicio.id}>{servicio.nombre}</option>)}
                </select>
              </label>
              <div className={styles.dosColumnas}>
                <label htmlFor="f-fecha">Fecha
                  <input id="f-fecha" type="date" name="fecha" min={fechaHoy()} value={form.fecha} onChange={editarFormulario} required />
                </label>
                <label htmlFor="f-hora">Hora
                  <input id="f-hora" type="time" name="hora" value={form.hora} onChange={editarFormulario} required />
                </label>
              </div>
              <label htmlFor="f-duracion">Duración
                <select id="f-duracion" name="duracion_horas" value={form.duracion_horas} onChange={editarFormulario} required>
                  <option value="1">1 hora</option>
                  <option value="2">2 horas</option>
                  <option value="3">3 horas</option>
                </select>
              </label>
              <label htmlFor="f-descripcion">Descripción de la tarea
                <textarea id="f-descripcion" name="descripcion" minLength={10} maxLength={500} rows={4} value={form.descripcion} onChange={editarFormulario} placeholder="Describe la ayuda que necesita el adulto mayor" required />
              </label>
              <small>No escribas teléfonos, direcciones ni antecedentes médicos en la descripción.</small>
              <div className={styles.precioReferencial}>
                <div>
                  <strong>Precio de referencia</strong>
                  <span>{precio.detalle}</span>
                </div>
                <strong className={styles.montoPrecio}>{precio.monto}</strong>
              </div>
              <p className={styles.aviso}>Este precio es una propuesta que se está validando. Esta versión no cobra dinero ni asigna estudiantes automáticamente.</p>
              <button type="submit" className={styles.botonPrincipal} disabled={enviando}>{enviando ? 'Guardando...' : 'Guardar solicitud'}</button>
            </form>
          )}
        </section>
      )}

      {vista === 'seguimiento' && (
        <SeguimientoServicios usuario={usuario} />
      )}
      {vista === 'calificaciones' && (
        <CalificacionesServicios usuario={usuario} />
      )}
      {vista === 'chat' && (
        <ChatServicios usuario={usuario} />
      )}
      {vista === 'avisos' && (
        <Notificaciones />
      )}
      {vista === 'agenda' && (
        <AgendaServicios />
      )}
      {vista === 'perfil' && (
        <section className={dash.panel} aria-labelledby="fam-perfil">
          <h2 id="fam-perfil">Mi perfil familiar</h2>
          <p>Datos básicos de tu cuenta autenticada.</p>
          <dl className={dash.datos}>
            <div><dt>Nombre</dt><dd>{usuario?.nombre || 'No disponible'}</dd></div>
            <div><dt>Tipo de cuenta</dt><dd>Familiar</dd></div>
            <div><dt>Estado</dt><dd>{usuario?.estado || 'No disponible'}</dd></div>
          </dl>
          <p className={styles.aviso}>Las direcciones, teléfonos y contactos privados no se muestran en este panel.</p>
        </section>
      )}
    </DashboardLayout>
  );
}
