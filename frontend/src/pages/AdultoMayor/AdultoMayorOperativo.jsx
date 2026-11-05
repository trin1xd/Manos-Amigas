import { useEffect, useState } from 'react';
import styles from './AdultoMayorDashboard.module.css';
import ui from './AdultoMayorOperativo.module.css';
import SeguimientoServicios from '../Seguimiento/SeguimientoServicios';
import CalificacionesServicios from '../Calificaciones/CalificacionesServicios';
import {
  obtenerCatalogoServicios,
  obtenerMisSolicitudes,
  registrarSolicitud,
  obtenerPostulantes,
  aceptarPostulacion,
  cancelarSolicitud,
  autorizarFamiliar,
  obtenerFamiliaresAutorizados,
  revocarAutorizacionFamiliar,
} from '../../services/solicitudesService';

const SECCIONES = [
  { clave: 'inicio', etiqueta: 'Inicio' },
  { clave: 'catalogo', etiqueta: 'Pedir ayuda' },
  { clave: 'solicitudes', etiqueta: 'Mis solicitudes' },
  { clave: 'seguimiento', etiqueta: 'Seguimiento' },
  { clave: 'calificaciones', etiqueta: 'Calificaciones' },
  { clave: 'perfil', etiqueta: 'Mi perfil' },
];

const ICONOS = {
  'cortar leña': '🪵',
  'aseo y orden': '🧹',
  'tareas del hogar': '🧹',
  'cocina y comida': '🥣',
  'trámites': '📄',
  'compras': '🛍️',
  'jardín y huerto': '🌿',
  'arreglos menores': '🛠️',
  'compañía': '💛',
  'acompañamiento': '💛',
  'mascotas': '🐾',
  'ayuda con tecnología': '📱',
  'apoyo digital': '📱',
};

function iconoServicio(nombre) {
  return ICONOS[nombre?.toLocaleLowerCase('es-CL')] || '🤝';
}

function fechaBonita(fechaISO) {
  if (!fechaISO || typeof fechaISO !== 'string') return 'Sin fecha';
  const fecha = new Date(fechaISO);
  if (Number.isNaN(fecha.getTime())) return fechaISO;
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'long', timeStyle: 'short' }).format(fecha);
}

function fechaInputLocal() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function FormularioSolicitud({ servicio, onVolver, onCreada }) {
  const [campos, setCampos] = useState({ fecha: '', hora: '', duracion_horas: '2', descripcion: '' });
  const [revisando, setRevisando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState('');
  const [creada, setCreada] = useState(null);

  function actualizar(evento) {
    const { name, value } = evento.target;
    setCampos(prev => ({ ...prev, [name]: value }));
    setError('');
  }

  function revisar(e) {
    e.preventDefault();
    const fecha = new Date(`${campos.fecha}T${campos.hora}:00`);
    if (Number.isNaN(fecha.getTime()) || fecha.getTime() <= Date.now()) {
      setError('Selecciona una fecha y hora posteriores al momento actual.');
      return;
    }
    if (fecha.getTime() > Date.now() + 366 * 86400000) {
      setError('La fecha debe estar dentro de los próximos 366 días.');
      return;
    }
    if (campos.descripcion.trim().length < 10 || campos.descripcion.trim().length > 500) {
      setError('La descripción debe tener entre 10 y 500 caracteres.');
      return;
    }
    setError('');
    setRevisando(true);
  }

  async function confirmar() {
    if (enviando) return;
    setError('');
    setEnviando(true);
    try {
      const nueva = await registrarSolicitud({
        id_servicio: Number(servicio.id),
        fecha: campos.fecha,
        hora: campos.hora,
        duracion_horas: Number(campos.duracion_horas),
        descripcion: campos.descripcion.trim(),
      });
      setCreada(nueva);
    } catch (err) {
      setError(err.message || 'No fue posible guardar la solicitud.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section className={styles.panelSolicitud} aria-labelledby="titulo-solicitud">
      {!creada && (
        <button type="button" className={styles.volver} onClick={onVolver} disabled={enviando}>
          ← Volver a las tareas
        </button>
      )}
      {creada ? (
        <div className={styles.confirmacion} role="status">
          <span className={styles.confirmacionIcono} aria-hidden="true">✓</span>
          <h2 id="titulo-solicitud">Solicitud guardada en SQL Server</h2>
          <p>¡Listo! Se registró la solicitud <strong>#{creada.id}</strong> con estado <strong>{creada.estado}</strong>.</p>
          <p className={styles.nota}>Ahora los universitarios verificados podrán encontrarla si la fecha sigue vigente. No se ha realizado ningún pago.</p>
          <button type="button" className={styles.botonPrimario} onClick={onCreada}>Ver mis solicitudes</button>
        </div>
      ) : (
        <>
          <p className={styles.sobretitulo}>Solicitud real</p>
          <h2 className={styles.tituloSeccion} id="titulo-solicitud">{revisando ? 'Revisar solicitud' : 'Solicitar una tarea'}</h2>
          <div className={styles.tareaElegida}>
            <span className={styles.servicioIcono} aria-hidden="true">{iconoServicio(servicio.nombre)}</span>
            <div><strong>{servicio.nombre}</strong><p>{servicio.descripcion}</p></div>
          </div>
          {!revisando ? (
            <form className={styles.formularioSolicitud} onSubmit={revisar}>
              <div className={styles.filaCampos}>
                <label className={styles.campo} htmlFor="real-fecha">
                  <span>Fecha de la tarea</span>
                  <input id="real-fecha" name="fecha" type="date" required min={fechaInputLocal()}
                    value={campos.fecha} onChange={actualizar} />
                </label>
                <label className={styles.campo} htmlFor="real-hora">
                  <span>Hora de inicio</span>
                  <input id="real-hora" name="hora" type="time" required
                    value={campos.hora} onChange={actualizar} />
                </label>
              </div>
              <label className={styles.campo} htmlFor="real-duracion">
                <span>Duración estimada</span>
                <select id="real-duracion" name="duracion_horas" value={campos.duracion_horas} onChange={actualizar}>
                  <option value="1">1 hora</option>
                  <option value="2">2 horas</option>
                  <option value="3">3 horas</option>
                </select>
              </label>
              <label className={styles.campo} htmlFor="real-descripcion">
                <span>Describe qué necesitas</span>
                <textarea id="real-descripcion" name="descripcion" value={campos.descripcion}
                  onChange={actualizar} minLength={10} maxLength={500} rows={4}
                  placeholder="Necesito ayuda para ordenar la cocina y guardar las compras." required />
                <small>De 10 a 500 caracteres. No incluyas datos médicos ni información privada.</small>
              </label>
              {error && <p className={styles.errorSolicitud} role="alert">{error}</p>}
              <p className={ui.aviso}>Por ahora no hay una tarifa oficial ni un sistema de pagos. La solicitud no cobra dinero.</p>
              <div className={styles.accionesFormulario}>
                <button type="button" className={styles.botonNeutro} onClick={onVolver}>Cancelar</button>
                <button type="submit" className={styles.botonNaranja}>Revisar datos</button>
              </div>
            </form>
          ) : (
            <div className={styles.revision}>
              <dl className={styles.resumenDatos}>
                <div><dt>Tarea</dt><dd>{servicio.nombre}</dd></div>
                <div><dt>Fecha</dt><dd>{campos.fecha}</dd></div>
                <div><dt>Hora</dt><dd>{campos.hora}</dd></div>
                <div><dt>Duración</dt><dd>{campos.duracion_horas} hora(s)</dd></div>
                <div><dt>Descripción</dt><dd>{campos.descripcion.trim()}</dd></div>
              </dl>
              {error && <p className={styles.errorSolicitud} role="alert">{error}</p>}
              <p className={ui.aviso}>Al confirmar se guardará una solicitud real en SQL Server. No se realizará un pago.</p>
              <div className={styles.accionesFormulario}>
                <button type="button" className={styles.botonNeutro} onClick={() => setRevisando(false)} disabled={enviando}>Editar datos</button>
                <button type="button" className={styles.botonNaranja} onClick={confirmar} disabled={enviando}>
                  {enviando ? 'Guardando...' : 'Confirmar y guardar solicitud'}
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}

function VincularFamiliar() {
  const [email, setEmail] = useState('');
  const [parentesco, setParentesco] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const [familiares, setFamiliares] = useState([]);
  const [cargandoFamiliares, setCargandoFamiliares] = useState(true);
  const [errorFamiliares, setErrorFamiliares] = useState('');
  const [revisionFamiliares, setRevisionFamiliares] = useState(0);
  const [revocandoId, setRevocandoId] = useState(null);

  useEffect(() => {
    let activo = true;
    setCargandoFamiliares(true);
    setErrorFamiliares('');
    obtenerFamiliaresAutorizados()
      .then(lista => { if (activo) setFamiliares(lista); })
      .catch(err => { if (activo) setErrorFamiliares(err.message || 'No se pudieron cargar los familiares.'); })
      .finally(() => { if (activo) setCargandoFamiliares(false); });
    return () => { activo = false; };
  }, [revisionFamiliares]);

  async function enviar(e) {
    e.preventDefault();
    if (enviando) return;
    setEnviando(true);
    setMensaje('');
    setError('');
    try {
      await autorizarFamiliar({ email_familiar: email.trim(), parentesco: parentesco.trim() });
      setMensaje('Familiar autorizado correctamente. Ya puede ver tus solicitudes desde su perfil.');
      setEmail('');
      setParentesco('');
      setRevisionFamiliares(n => n + 1);
    } catch (err) {
      setError(err.message || 'No fue posible autorizar al familiar.');
    } finally {
      setEnviando(false);
    }
  }

  async function revocar(id, nombre) {
    if (revocandoId !== null || enviando) return;
    if (!window.confirm(`¿Revocar el acceso de ${nombre} a tus solicitudes?`)) return;
    setRevocandoId(id);
    setError('');
    setMensaje('');
    try {
      await revocarAutorizacionFamiliar(id);
      setMensaje(`Acceso de ${nombre} revocado correctamente.`);
      setRevisionFamiliares(n => n + 1);
    } catch (err) {
      setError(err.message || 'No fue posible revocar el acceso.');
    } finally {
      setRevocandoId(null);
    }
  }

  return (
    <section className={`${styles.panelPerfil} ${ui.bloqueVincular}`} aria-labelledby="titulo-vincular">
      <h2 id="titulo-vincular">Autorizar a un familiar</h2>
      <p className={styles.textoAyuda}>Debe tener una cuenta con rol Familiar. Solo autorizarás a esa cuenta a gestionar tus solicitudes; no se compartirán direcciones ni teléfonos.</p>
      <form className={styles.formularioSolicitud} onSubmit={enviar}>
        <label className={styles.campo} htmlFor="email-familiar">Correo electrónico del familiar
          <input type="email" id="email-familiar" required value={email} onChange={e => setEmail(e.target.value)} />
        </label>
        <label className={styles.campo} htmlFor="parentesco">Parentesco
          <input type="text" id="parentesco" minLength={2} maxLength={100} required value={parentesco} onChange={e => setParentesco(e.target.value)} placeholder="Hija, hijo, nieta..." />
        </label>
        {mensaje && <p className={ui.ok} role="status">{mensaje}</p>}
        {error && <p className={styles.errorSolicitud} role="alert">{error}</p>}
        <button className={styles.botonPrimario} type="submit" disabled={enviando || revocandoId !== null}>{enviando ? 'Autorizando...' : 'Autorizar familiar'}</button>
      </form>

      <div className={ui.encabezadoFamiliares}>
        <h3>Familiares autorizados ({familiares.length})</h3>
        <button className={ui.botonActualizar} type="button" onClick={() => setRevisionFamiliares(n => n + 1)} disabled={cargandoFamiliares || revocandoId !== null}>Actualizar lista</button>
      </div>
      {cargandoFamiliares && <p role="status">Consultando familiares autorizados...</p>}
      {errorFamiliares && <p className={ui.errorVinculos} role="alert">{errorFamiliares}</p>}
      {!cargandoFamiliares && !errorFamiliares && familiares.length === 0 && (
        <p className={styles.nota}>Todavía no tienes familiares autorizados. Registrar una cuenta Familiar no la vincula automáticamente: debes autorizarla usando su correo aquí.</p>
      )}
      {!cargandoFamiliares && familiares.length > 0 && (
        <ul className={ui.listaFamiliares}>
          {familiares.map(familiar => (
            <li key={familiar.id} className={ui.familiarFila}>
              <div className={ui.familiarInfo}>
                <strong>{familiar.nombre}</strong>
                <p>{familiar.parentesco} · {familiar.email}</p>
              </div>
              <button className={ui.botonRevocar} type="button" onClick={() => revocar(familiar.id, familiar.nombre)} disabled={revocandoId !== null || enviando}>
                {revocandoId === familiar.id ? 'Revocando...' : 'Revocar acceso'}
              </button>
            </li>
          ))}
        </ul>
      )}
      <p className={styles.nota}>La autorización entra en vigor al guardarse. La aceptación explícita del familiar se evaluará en una etapa futura.</p>
    </section>
  );
}

export default function AdultoMayorOperativo({ usuario, onLogout }) {
  const [vista, setVista] = useState('inicio');
  const [servicios, setServicios] = useState([]);
  const [solicitudes, setSolicitudes] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [errorCarga, setErrorCarga] = useState('');
  const [revision, setRevision] = useState(0);
  const [idPostulantes, setIdPostulantes] = useState(null);
  const [postulaciones, setPostulaciones] = useState([]);
  const [cargandoPostulantes, setCargandoPostulantes] = useState(false);
  const [errorPostulantes, setErrorPostulantes] = useState('');
  const [accionEnCurso, setAccionEnCurso] = useState(false);

  useEffect(() => {
    if (vista !== 'catalogo' && vista !== 'solicitudes') return;
    let activo = true;
    setCargando(true);
    setErrorCarga('');
    const trabajo = vista === 'catalogo' ? obtenerCatalogoServicios() : obtenerMisSolicitudes();
    trabajo
      .then(resultados => {
        if (!activo) return;
        if (vista === 'catalogo') setServicios(resultados);
        if (vista === 'solicitudes') setSolicitudes(resultados);
      })
      .catch(err => { if (activo) setErrorCarga(err.message || 'No se pudieron cargar los datos.'); })
      .finally(() => { if (activo) setCargando(false); });
    return () => { activo = false; };
  }, [vista, revision]);

  function navegar(destino) {
    setVista(destino);
    setSeleccionado(null);
    setIdPostulantes(null);
    setPostulaciones([]);
    setErrorPostulantes('');
  }

  function refrescar() { setRevision(n => n + 1); }

  async function cargarPostulantes(id) {
    if (idPostulantes === id) {
      setIdPostulantes(null);
      return;
    }
    setIdPostulantes(id);
    setCargandoPostulantes(true);
    setErrorPostulantes('');
    setPostulaciones([]);
    try {
      const lista = await obtenerPostulantes(id);
      setPostulaciones(lista);
    } catch (err) {
      setErrorPostulantes(err.message || 'No fue posible consultar postulantes.');
    } finally {
      setCargandoPostulantes(false);
    }
  }

  async function aceptar(idSolicitud, idPostulacion) {
    if (!window.confirm('¿Aceptar esta postulación y asignar la tarea?')) return;
    setAccionEnCurso(true);
    setErrorPostulantes('');
    try {
      await aceptarPostulacion(idSolicitud, idPostulacion);
      setIdPostulantes(null);
      setPostulaciones([]);
      refrescar();
    } catch (err) {
      setErrorPostulantes(err.message || 'No fue posible aceptar la postulación.');
    } finally {
      setAccionEnCurso(false);
    }
  }

  async function cancelar(idSolicitud) {
    if (!window.confirm('¿Seguro que deseas cancelar esta solicitud?')) return;
    setAccionEnCurso(true);
    setErrorCarga('');
    try {
      await cancelarSolicitud(idSolicitud);
      setIdPostulantes(null);
      refrescar();
    } catch (err) {
      setErrorCarga(err.message || 'No fue posible cancelar la solicitud.');
    } finally {
      setAccionEnCurso(false);
    }
  }

  const nombre = usuario?.nombre?.trim().split(/\s+/)[0] || 'Bienvenido/a';

  return (
    <div className={styles.pagina}>
      <header className={styles.cabecera}>
        <div className={styles.cabeceraInterior}>
          <div className={styles.marca}><span className={styles.marcaIcono} aria-hidden="true">♥</span><span>Manos Amigas</span></div>
          <button type="button" className={styles.cerrarSesion} onClick={onLogout}>Cerrar sesión</button>
        </div>
      </header>
      <div className={styles.contenedor}>
        <div className={styles.presentacion}>
          <p className={styles.sobretitulo}>Espacio de adulto mayor</p>
          <h1>Hola, {nombre} <span aria-hidden="true">👋</span></h1>
          <p>¿En qué podemos ayudarte hoy?</p>
        </div>
        <nav className={styles.navegacion} aria-label="Secciones del panel de adulto mayor">
          {SECCIONES.map(item => (
            <button key={item.clave} type="button" onClick={() => navegar(item.clave)}
              className={`${styles.pestana} ${vista === item.clave || (vista === 'nueva' && item.clave === 'catalogo') ? styles.pestanaActiva : ''}`}
              aria-current={vista === item.clave ? 'page' : undefined}>
              {item.etiqueta}
            </button>
          ))}
        </nav>
        <main id="contenido-dashboard" className={styles.contenido}>
          {vista === 'inicio' && (
            <>
              <section className={styles.tarjetaDestacada} aria-labelledby="titulo-ayuda">
                <div>
                  <p className={styles.sobretituloClaro}>Estamos para acompañarte</p>
                  <h2 id="titulo-ayuda">Pide ayuda para tus tareas cotidianas</h2>
                  <p>Elige una tarea y envía una solicitud real a Manos Amigas.</p>
                  <button type="button" className={styles.botonNaranja} onClick={() => navegar('catalogo')}>Ver tareas disponibles</button>
                </div>
                <span className={styles.corazonGrande} aria-hidden="true">♡</span>
              </section>
              <section aria-labelledby="titulo-accesos">
                <h2 id="titulo-accesos" className={styles.tituloSeccion}>¿Qué necesitas hacer?</h2>
                <div className={styles.grillaAccesos}>
                  <button type="button" className={styles.acceso} onClick={() => navegar('catalogo')}>
                    <span className={styles.accesoIcono} aria-hidden="true">🧹</span><strong>Pedir ayuda</strong><span>Crear una solicitud real</span>
                  </button>
                  <button type="button" className={styles.acceso} onClick={() => navegar('solicitudes')}>
                    <span className={styles.accesoIcono} aria-hidden="true">📋</span><strong>Mis solicitudes</strong><span>Ver solicitudes y postulantes</span>
                  </button>
                  <button type="button" className={styles.acceso} onClick={() => navegar('perfil')}>
                    <span className={styles.accesoIcono} aria-hidden="true">👤</span><strong>Mi perfil</strong><span>Consultar mi cuenta y autorizar familiares</span>
                  </button>
                </div>
              </section>
            </>
          )}
          {vista === 'catalogo' && (
            <section aria-labelledby="titulo-catalogo">
              <div className={ui.tituloFila}>
                <h2 id="titulo-catalogo" className={styles.tituloSeccion}>Tareas disponibles</h2>
                <button type="button" className={styles.botonSecundario} onClick={refrescar}>Actualizar</button>
              </div>
              <p className={styles.textoAyuda}>Estas categorías provienen de SQL Server.</p>
              {cargando && <p role="status">Cargando servicios...</p>}
              {errorCarga && <p className={styles.errorSolicitud} role="alert">{errorCarga}</p>}
              {!cargando && !errorCarga && servicios.length === 0 && <p>No existen servicios activos por ahora.</p>}
              {!cargando && !errorCarga && servicios.length > 0 && (
                <div className={styles.grillaServicios}>
                  {servicios.map(servicio => (
                    <article key={servicio.id} className={styles.servicio}>
                      <span className={styles.servicioIcono} aria-hidden="true">{iconoServicio(servicio.nombre)}</span>
                      <h3>{servicio.nombre}</h3>
                      <p>{servicio.descripcion || 'Tarea cotidiana de apoyo.'}</p>
                      <button type="button" className={styles.botonSecundario} onClick={() => { setSeleccionado(servicio); setVista('nueva'); }}>
                        Elegir esta tarea
                      </button>
                    </article>
                  ))}
                </div>
              )}
              <p className={styles.nota}>Manos Amigas no presta servicios médicos ni tratamientos de salud.</p>
            </section>
          )}
          {vista === 'nueva' && seleccionado && (
            <FormularioSolicitud key={seleccionado.id} servicio={seleccionado}
              onVolver={() => navegar('catalogo')}
              onCreada={() => { refrescar(); navegar('solicitudes'); }} />
          )}
          {vista === 'solicitudes' && (
            <section aria-labelledby="titulo-solicitudes">
              <div className={ui.tituloFila}>
                <h2 id="titulo-solicitudes" className={styles.tituloSeccion}>Mis solicitudes</h2>
                <button type="button" className={styles.botonPrimario} onClick={refrescar}>Actualizar</button>
              </div>
              <p className={styles.textoAyuda}>Estas solicitudes se consultan desde SQL Server y están vinculadas a tu cuenta.</p>
              {cargando && <p role="status">Cargando solicitudes...</p>}
              {errorCarga && <p className={styles.errorSolicitud} role="alert">{errorCarga}</p>}
              {!cargando && !errorCarga && solicitudes.length === 0 && (
                <div className={styles.panelVacio}>
                  <span className={styles.iconoVacio} aria-hidden="true">📋</span>
                  <p>Todavía no tienes solicitudes registradas.</p>
                  <button type="button" className={styles.botonPrimario} onClick={() => navegar('catalogo')}>Pedir ayuda</button>
                </div>
              )}
              {!cargando && !errorCarga && solicitudes.length > 0 && (
                <div className={styles.listaSolicitudes}>
                  {solicitudes.map(sol => (
                    <article className={styles.tarjetaSolicitud} key={sol.id}>
                      <div className={styles.encabezadoSolicitud}>
                        <h3>{iconoServicio(sol.servicio)} {sol.servicio} · #{sol.id}</h3>
                        <span className={ui.etiquetaEstado}>{sol.estado}</span>
                      </div>
                      <p><strong>Fecha:</strong> {fechaBonita(sol.fecha_solicitada)}</p>
                      <p><strong>Duración:</strong> {sol.duracion_horas || 'No indicada'} hora(s)</p>
                      <p><strong>Descripción:</strong> {sol.descripcion || 'Sin descripción'}</p>
                      <div className={ui.acciones}>
                        {sol.estado === 'PENDIENTE' && (
                          <button type="button" className={styles.botonSecundario} onClick={() => cargarPostulantes(sol.id)} disabled={accionEnCurso}>
                            {idPostulantes === sol.id ? 'Ocultar postulantes' : 'Ver postulantes'}
                          </button>
                        )}
                        {['PENDIENTE', 'ASIGNADA'].includes(sol.estado) && (
                          <button type="button" className={ui.botonPeligro} onClick={() => cancelar(sol.id)} disabled={accionEnCurso}>
                            Cancelar solicitud
                          </button>
                        )}
                      </div>
                      {idPostulantes === sol.id && (
                        <div className={ui.postulantes}>
                          <h4>Estudiantes que postularon</h4>
                          {cargandoPostulantes && <p>Cargando postulantes...</p>}
                          {errorPostulantes && <p className={styles.errorSolicitud} role="alert">{errorPostulantes}</p>}
                          {!cargandoPostulantes && !errorPostulantes && postulaciones.length === 0 && <p>Nadie ha postulado todavía.</p>}
                          {!cargandoPostulantes && !errorPostulantes && postulaciones.map(post => (
                            <div key={post.id} className={ui.postulanteFila}>
                              <span>{post.estudiante_nombre} · {post.estado}</span>
                              {post.estado === 'PENDIENTE' && (
                                <button type="button" className={styles.botonPrimario} disabled={accionEnCurso}
                                  onClick={() => aceptar(sol.id, post.id)}>Aceptar</button>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </article>
                  ))}
                </div>
              )}
            </section>
          )}
          {vista === 'seguimiento' && (
            <SeguimientoServicios usuario={usuario} />
          )}
          {vista === 'calificaciones' && (
            <CalificacionesServicios usuario={usuario} />
          )}
          {vista === 'perfil' && (
            <>
              <section className={styles.panelPerfil} aria-labelledby="titulo-perfil">
                <h2 id="titulo-perfil">Mi perfil</h2>
                <p className={styles.textoAyuda}>Información básica de tu cuenta autenticada.</p>
                <dl className={styles.listaPerfil}>
                  <div><dt>Nombre</dt><dd>{usuario?.nombre || 'No disponible'}</dd></div>
                  <div><dt>Tipo de cuenta</dt><dd>Adulto mayor</dd></div>
                  <div><dt>Estado</dt><dd>{usuario?.estado || 'No disponible'}</dd></div>
                </dl>
              </section>
              <VincularFamiliar />
            </>
          )}
        </main>
        <footer className={styles.pie}>Manos Amigas · Solicitudes reales con acceso por rol · Sin pagos implementados</footer>
      </div>
    </div>
  );
}
