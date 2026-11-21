import { useEffect, useState } from 'react';
import UiIcon from '../../components/ui/UiIcon';
import logoIcono from '../../assets/images/logo-icono.png';
import styles from './AdultoMayorDashboard.module.css';
import ui from './AdultoMayorOperativo.module.css';
import SeguimientoServicios from '../Seguimiento/SeguimientoServicios';
import CalificacionesServicios from '../Calificaciones/CalificacionesServicios';
import ChatServicios from '../Chat/ChatServicios';
import Notificaciones from '../Notificaciones/Notificaciones';
import AgendaServicios from '../Agenda/AgendaServicios';
import { precioReferencialPara } from '../../utils/precioReferencial';
import FichaEstudiante, { NotaFichaEstudiante } from '../../components/FichaEstudiante/FichaEstudiante';
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

const WHATSAPP_NUMERO = '56941679024';

function enlaceWhatsapp(texto) {
  return `https://wa.me/${WHATSAPP_NUMERO}?text=${encodeURIComponent(texto)}`;
}

const SECCIONES = [
  { clave: 'inicio', etiqueta: 'Inicio' },
  { clave: 'catalogo', etiqueta: 'Pedir ayuda' },
  { clave: 'solicitudes', etiqueta: 'Mis solicitudes' },
  { clave: 'seguimiento', etiqueta: 'Seguimiento' },
  { clave: 'calificaciones', etiqueta: 'Calificaciones' },
  { clave: 'chat', etiqueta: 'Chat' },
  { clave: 'avisos', etiqueta: 'Avisos' },
  { clave: 'agenda', etiqueta: 'Agenda' },
  { clave: 'perfil', etiqueta: 'Mi perfil' },
];

const ICONOS = {
  'cortar leña': 'tronco',
  'aseo y orden': 'destellos',
  'tareas del hogar': 'destellos',
  'cocina y comida': 'cubiertos',
  'trámites': 'documento-visto',
  'compras': 'carrito',
  'jardín y huerto': 'hoja',
  'arreglos menores': 'llave inglesa',
  'compañía': 'compania-corazon',
  'acompañamiento': 'compania-corazon',
  'mascotas': 'paw-print',
  'ayuda con tecnología': 'celular-corazon',
  'apoyo digital': 'celular-corazon',
};

function iconoServicio(nombre) {
  const icono = ICONOS[nombre?.toLocaleLowerCase('es-CL')] || 'hand-heart';
  return <UiIcon name={icono} size={24} />;
}

function iconoTarea(nombre) {
  return ICONOS[nombre?.toLocaleLowerCase('es-CL')] || 'hand-heart';
}

const MAPA_SERVICIOS_A_GRUPO = {
  'compras': 'compras-tramites',
  'trámites': 'compras-tramites',
  'acompañamiento': 'compras-tramites',
  'compañía': 'compania',
  'aseo y orden': 'hogar',
  'tareas del hogar': 'hogar',
  'cocina y comida': 'hogar',
  'arreglos menores': 'hogar',
  'cortar leña': 'hogar',
  'jardín y huerto': 'jardin-mascotas',
  'mascotas': 'jardin-mascotas',
  'apoyo digital': 'tecnologia',
  'ayuda con tecnología': 'tecnologia',
};

const GRUPOS_CATALOGO = [
  {
    id: 'compras-tramites',
    nombre: 'Compras y trámites',
    descripcion: 'Súper, banco, citas',
    color: '#22878a',
    icono: 'carrito',
  },
  {
    id: 'compania',
    nombre: 'Compañía',
    descripcion: 'Visitas y paseos',
    color: '#e8648a',
    icono: 'compania-corazon',
  },
  {
    id: 'hogar',
    nombre: 'Hogar',
    descripcion: 'Aseo, cocina, arreglos',
    color: '#7a5cc9',
    icono: 'casa',
  },
  {
    id: 'jardin-mascotas',
    nombre: 'Jardín y mascotas',
    descripcion: 'Plantas y animales',
    color: '#3aa655',
    icono: 'hoja',
  },
  {
    id: 'tecnologia',
    nombre: 'Tecnología',
    descripcion: 'Celular y videollamadas',
    color: '#3b7dd8',
    icono: 'celular-corazon',
  },
];

function procesarCatalogoEnGrupos(serviciosRaw) {
  if (!Array.isArray(serviciosRaw) || serviciosRaw.length === 0) return [];

  // Resolver canónicos:
  // "Tareas del hogar" y "Aseo y orden" -> canónico "Aseo y orden" (prioriza id de "Aseo y orden")
  // "Ayuda con tecnología" y "Apoyo digital" -> canónico "Apoyo digital" (prioriza id de "Apoyo digital")
  const porClaveCanonica = new Map();

  for (const item of serviciosRaw) {
    if (!item || !item.nombre) continue;
    const norm = item.nombre.trim().toLowerCase('es-CL');

    let clave = norm;
    let nombreAMostrar = item.nombre;
    let esCanonicaPrioritaria = false;

    if (norm === 'aseo y orden') {
      clave = 'aseo y orden';
      nombreAMostrar = 'Aseo y orden';
      esCanonicaPrioritaria = true;
    } else if (norm === 'tareas del hogar') {
      clave = 'aseo y orden';
      nombreAMostrar = 'Aseo y orden';
      esCanonicaPrioritaria = false;
    } else if (norm === 'apoyo digital') {
      clave = 'apoyo digital';
      nombreAMostrar = 'Apoyo digital';
      esCanonicaPrioritaria = true;
    } else if (norm === 'ayuda con tecnología') {
      clave = 'apoyo digital';
      nombreAMostrar = 'Apoyo digital';
      esCanonicaPrioritaria = false;
    }

    if (!porClaveCanonica.has(clave)) {
      porClaveCanonica.set(clave, {
        ...item,
        nombre: nombreAMostrar,
        claveCanonica: clave,
        esCanonicaPrioritaria,
      });
    } else if (esCanonicaPrioritaria) {
      porClaveCanonica.set(clave, {
        ...item,
        nombre: nombreAMostrar,
        claveCanonica: clave,
        esCanonicaPrioritaria,
      });
    }
  }

  const grupos = GRUPOS_CATALOGO.map(g => ({
    ...g,
    tareas: [],
  }));

  const grupoOtros = {
    id: 'otros',
    nombre: 'Otros',
    descripcion: 'Otras tareas disponibles',
    color: '#536a73',
    icono: 'hand-heart',
    tareas: [],
  };

  for (const tarea of porClaveCanonica.values()) {
    const grupoId = MAPA_SERVICIOS_A_GRUPO[tarea.claveCanonica];
    const grupoEncontrado = grupos.find(g => g.id === grupoId);
    if (grupoEncontrado) {
      grupoEncontrado.tareas.push(tarea);
    } else {
      grupoOtros.tareas.push(tarea);
    }
  }

  const activos = grupos.filter(g => g.tareas.length > 0);
  if (grupoOtros.tareas.length > 0) {
    activos.push(grupoOtros);
  }

  return activos;
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

function FormularioSolicitud({ servicio, grupo, onVolver, onCreada }) {
  const [campos, setCampos] = useState({ fecha: '', hora: '', duracion_horas: '2', descripcion: '' });
  const [revisando, setRevisando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState('');
  const [creada, setCreada] = useState(null);
  const precio = precioReferencialPara(campos.duracion_horas);
  const colorGrupo = grupo?.color || '#22878a';
  const iconoNombre = iconoTarea(servicio?.nombre);

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
        <button
          type="button"
          className={ui.botonVolverPaso}
          onClick={revisando ? () => setRevisando(false) : onVolver}
          disabled={enviando}
        >
          ← {revisando ? 'Volver al formulario' : 'Atrás'}
        </button>
      )}
      {creada ? (
        <div className={styles.confirmacion} role="status">
          <span className={styles.confirmacionIcono} aria-hidden="true">✓</span>
          <h2 id="titulo-solicitud">Solicitud guardada correctamente</h2>
          <p>¡Listo! Se registró la solicitud <strong>#{creada.id}</strong> con estado <strong>{creada.estado}</strong>.</p>
          <p className={styles.nota}>Ahora los universitarios verificados podrán encontrarla si la fecha sigue vigente. No se ha realizado ningún pago.</p>
          <button type="button" className={ui.botonPaso} style={{ backgroundColor: '#14696a' }} onClick={onCreada}>
            Ver mis solicitudes
          </button>
          <a
            className={ui.botonWhatsapp}
            href={enlaceWhatsapp(
              `Hola, acabo de pedir ayuda en Manos Amigas (solicitud #${creada.id}): ${servicio.nombre}, el ${campos.fecha} a las ${campos.hora}.`
            )}
            target="_blank"
            rel="noopener noreferrer"
          >
            Avisar también por WhatsApp
          </a>
        </div>
      ) : (
        <>
          <span className={ui.indicadorPaso}>Paso 3 de 3</span>
          <h2 className={ui.tituloPaso} id="titulo-solicitud">
            {revisando ? 'Revisar y confirmar solicitud' : 'Cuándo y qué necesitas'}
          </h2>

          <div className={ui.filaTarea} style={{ borderColor: colorGrupo, margin: '16px 0 24px' }}>
            <div className={ui.filaTareaInfo}>
              <div className={ui.circuloIcono} style={{ backgroundColor: colorGrupo }} aria-hidden="true">
                <UiIcon name={iconoNombre} size={32} />
              </div>
              <div>
                <h3 className={ui.nombreTarea}>{servicio.nombre}</h3>
                <p className={ui.descripcionTarea}>{servicio.descripcion || 'Tarea cotidiana de apoyo.'}</p>
              </div>
            </div>
          </div>

          {!revisando ? (
            <form className={ui.formAccesible} onSubmit={revisar}>
              <div className={styles.filaCampos}>
                <label htmlFor="real-fecha">
                  <span>Fecha de la tarea</span>
                  <input
                    id="real-fecha"
                    name="fecha"
                    type="date"
                    required
                    min={fechaInputLocal()}
                    value={campos.fecha}
                    onChange={actualizar}
                  />
                </label>
                <label htmlFor="real-hora">
                  <span>Hora de inicio</span>
                  <input
                    id="real-hora"
                    name="hora"
                    type="time"
                    required
                    value={campos.hora}
                    onChange={actualizar}
                  />
                </label>
              </div>
              <label htmlFor="real-duracion">
                <span>Duración estimada</span>
                <select
                  id="real-duracion"
                  name="duracion_horas"
                  value={campos.duracion_horas}
                  onChange={actualizar}
                >
                  <option value="1">1 hora</option>
                  <option value="2">2 horas</option>
                  <option value="3">3 horas</option>
                </select>
              </label>
              <label htmlFor="real-descripcion">
                <span>Describe qué necesitas</span>
                <textarea
                  id="real-descripcion"
                  name="descripcion"
                  value={campos.descripcion}
                  onChange={actualizar}
                  minLength={10}
                  maxLength={500}
                  rows={4}
                  placeholder="Por ejemplo: necesito ayuda para ordenar la cocina y guardar las compras."
                  required
                />
                <small>De 10 a 500 caracteres. No incluyas datos médicos ni información privada.</small>
              </label>

              {error && <p className={styles.errorSolicitud} role="alert">{error}</p>}

              <div className={ui.precioAccesible}>
                <div>
                  <strong>Precio de referencia</strong>
                  <div style={{ fontSize: '1.15rem' }}>{precio.detalle}</div>
                </div>
                <strong className={ui.montoDestacado}>{precio.monto}</strong>
              </div>
              <p className={ui.aviso}>Este precio es una propuesta que se está validando. Por ahora la solicitud no cobra dinero y no hay un sistema de pagos.</p>

              <div className={ui.accionesAccesibles}>
                <button type="button" className={ui.botonVolverPaso} onClick={onVolver} style={{ margin: 0 }}>
                  Cancelar
                </button>
                <button type="submit" className={ui.botonPaso} style={{ backgroundColor: colorGrupo }}>
                  Revisar datos →
                </button>
              </div>
            </form>
          ) : (
            <div className={ui.formAccesible}>
              <dl className={ui.resumenAccesible}>
                <div className={ui.resumenFila}><dt>Tarea</dt><dd>{servicio.nombre}</dd></div>
                <div className={ui.resumenFila}><dt>Fecha</dt><dd>{campos.fecha}</dd></div>
                <div className={ui.resumenFila}><dt>Hora</dt><dd>{campos.hora}</dd></div>
                <div className={ui.resumenFila}><dt>Duración</dt><dd>{campos.duracion_horas} hora(s)</dd></div>
                <div className={ui.resumenFila}><dt>Descripción</dt><dd>{campos.descripcion.trim()}</dd></div>
                <div className={ui.resumenFila}><dt>Precio de referencia</dt><dd>{precio.monto}</dd></div>
              </dl>
              {error && <p className={styles.errorSolicitud} role="alert">{error}</p>}
              <p className={ui.aviso}>Al confirmar se guardará una solicitud en Manos Amigas. No se realizará un pago.</p>
              <div className={ui.accionesAccesibles}>
                <button type="button" className={ui.botonVolverPaso} onClick={() => setRevisando(false)} disabled={enviando} style={{ margin: 0 }}>
                  ← Editar datos
                </button>
                <button type="button" className={ui.botonPaso} style={{ backgroundColor: colorGrupo }} onClick={confirmar} disabled={enviando}>
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
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [servicios, setServicios] = useState([]);
  const [solicitudes, setSolicitudes] = useState([]);
  const [seleccionado, setSeleccionado] = useState(null);
  const [grupoActivo, setGrupoActivo] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [errorCarga, setErrorCarga] = useState('');
  const [revision, setRevision] = useState(0);
  const [idPostulantes, setIdPostulantes] = useState(null);
  const [postulaciones, setPostulaciones] = useState([]);
  const [cargandoPostulantes, setCargandoPostulantes] = useState(false);
  const [errorPostulantes, setErrorPostulantes] = useState('');
  const [accionEnCurso, setAccionEnCurso] = useState(false);

  const catalogoGrupos = procesarCatalogoEnGrupos(servicios);

  const primerNombre = usuario?.nombre?.trim().split(/\s+/)[0] || '';
  const solicitudesActivas = Array.isArray(solicitudes)
    ? solicitudes.filter(s => ['PENDIENTE', 'ASIGNADA'].includes(s.estado)).length
    : 0;
  const textoSolicitudes = solicitudes.length > 0
    ? (solicitudesActivas > 0
        ? `Tienes ${solicitudesActivas} ${solicitudesActivas === 1 ? 'solicitud activa' : 'solicitudes activas'}`
        : 'Revisa el estado de tus solicitudes')
    : 'Revisa el estado de tus solicitudes y postulantes';

  function seleccionarGrupo(grupo) {
    setGrupoActivo(grupo);
    if (grupo.tareas.length === 1) {
      setSeleccionado(grupo.tareas[0]);
      setVista('nueva');
    }
  }

  function seleccionarTarea(tarea, grupo) {
    setGrupoActivo(grupo);
    setSeleccionado(tarea);
    setVista('nueva');
  }

  function volverDesdeFormulario() {
    setSeleccionado(null);
    if (grupoActivo && grupoActivo.tareas.length === 1) {
      setGrupoActivo(null);
      setVista('catalogo');
    } else {
      setVista('catalogo');
    }
  }

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
    setMenuAbierto(false);
    setVista(destino);
    setSeleccionado(null);
    setGrupoActivo(null);
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
    <div className={styles.pagina} data-manos-panel="true">
      <header className={styles.cabecera}>
        <div className={styles.cabeceraInterior}>
          <div className={styles.marca}><span className={styles.marcaIcono} aria-hidden="true"><img src={logoIcono} alt="" className={ui.logoImg} /></span><span>Manos Amigas</span></div>
          <div className={ui.accionesBarra}>
            <div id="manos-accesibilidad-slot" className={ui.accesibilidadSlot} />
            <button type="button" className={`${styles.cerrarSesion} ${ui.botonSalir}`} onClick={onLogout} aria-label="Cerrar sesión" title="Cerrar sesión">
              <UiIcon name="logout" size={20} />
              <span className={ui.salirTexto}>Cerrar sesión</span>
            </button>
          </div>
        </div>
      </header>
      <div className={styles.contenedor}>
        {vista !== 'inicio' && (
          <div className={styles.presentacion}>
            <p className={styles.sobretitulo}>Espacio de adulto mayor</p>
            <h1>Hola, {nombre}</h1>
            <p>¿En qué podemos ayudarte hoy?</p>
          </div>
        )}
        <div className={styles.layout}>
          <button type="button" className={styles.menuMovil} aria-expanded={menuAbierto}
            aria-controls="navegacion-adulto" onClick={() => setMenuAbierto(abierto => !abierto)}>
            <span aria-hidden="true">☰</span>
            {menuAbierto ? 'Cerrar menú' : '¿Qué quieres hacer?'}
            <span aria-hidden="true">{menuAbierto ? '−' : '+'}</span>
          </button>
          <aside id="navegacion-adulto" className={`${styles.barraLateral} ${menuAbierto ? styles.barraLateralAbierta : ''}`}>
            <div className={styles.encabezadoLateral}>
              <strong>Mi panel</strong>
              <span>Tu ayuda, en un solo lugar</span>
            </div>
            <nav className={styles.navegacion} aria-label="Secciones del panel de adulto mayor">
          {SECCIONES.map(item => (
            <button key={item.clave} type="button" onClick={() => navegar(item.clave)}
              className={`${styles.pestana} ${vista === item.clave || (vista === 'nueva' && item.clave === 'catalogo') ? styles.pestanaActiva : ''}`}
              aria-current={vista === item.clave ? 'page' : undefined}>
              <UiIcon name={item.clave} size={20} /> <span>{item.etiqueta}</span>
            </button>
          ))}
            </nav>
          </aside>
          <div className={styles.panelPrincipal}>
            <main id="contenido-dashboard" className={styles.contenido}>
          {vista === 'inicio' && (
            <section className={ui.seccionInicio} aria-labelledby="titulo-saludo">
              <div className={ui.encabezadoInicio}>
                <h2 id="titulo-saludo" className={ui.saludoInicio}>
                  {primerNombre ? `Hola, ${primerNombre}` : '¡Hola!'}
                </h2>
                <p className={ui.preguntaInicio}>¿En qué podemos ayudarte hoy?</p>
              </div>

              <div className={ui.grillaInicio} role="list" aria-label="Acciones principales">
                <button
                  type="button"
                  className={`${ui.tarjetaInicio} ${ui.tarjetaInicioPrincipal}`}
                  onClick={() => navegar('catalogo')}
                  role="listitem"
                >
                  <div
                    className={ui.circuloIconoGrande}
                    style={{ backgroundColor: '#e98126' }}
                    aria-hidden="true"
                  >
                    <UiIcon name="pedir-ayuda" size={36} />
                  </div>
                  <div className={ui.infoInicio}>
                    <span className={ui.tituloTarjetaInicio}>Pedir ayuda</span>
                    <span className={ui.descripcionTarjetaInicio}>Elige qué necesitas y te ayudamos</span>
                  </div>
                </button>

                <button
                  type="button"
                  className={`${ui.tarjetaInicio} ${ui.tarjetaInicioSecundaria}`}
                  onClick={() => navegar('solicitudes')}
                  role="listitem"
                >
                  <div
                    className={ui.circuloIconoGrande}
                    style={{ backgroundColor: '#14696a' }}
                    aria-hidden="true"
                  >
                    <UiIcon name="solicitudes" size={36} />
                  </div>
                  <div className={ui.infoInicio}>
                    <span className={ui.tituloTarjetaInicio}>Mis solicitudes</span>
                    <span className={ui.descripcionTarjetaInicio}>{textoSolicitudes}</span>
                  </div>
                </button>
                <a
                  className={`${ui.tarjetaInicio} ${ui.tarjetaInicioWhatsapp}`}
                  href={enlaceWhatsapp(
                    `Hola, ${primerNombre ? `soy ${primerNombre}. ` : ''}Necesito ayuda con una tarea. ¿Me pueden ayudar?`
                  )}
                  target="_blank"
                  rel="noopener noreferrer"
                  role="listitem"
                >
                  <div
                    className={ui.circuloIconoGrande}
                    style={{ backgroundColor: '#128c4a' }}
                    aria-hidden="true"
                  >
                    <UiIcon name="chat" size={36} />
                  </div>
                  <div className={ui.infoInicio}>
                    <span className={ui.tituloTarjetaInicio}>Contáctanos por WhatsApp</span>
                    <span className={ui.descripcionTarjetaInicio}>Escríbenos y te respondemos</span>
                  </div>
                </a>
              </div>
            </section>
          )}
          {vista === 'catalogo' && (
            <section aria-labelledby="titulo-catalogo">
              <div className={ui.tituloFila}>
                <h2 id="titulo-catalogo" className={styles.tituloSeccion}>Pedir ayuda</h2>
                <button type="button" className={styles.botonSecundario} onClick={refrescar}>
                  Actualizar
                </button>
              </div>

              {cargando && <p role="status" style={{ fontSize: '1.25rem' }}>Cargando servicios...</p>}
              {errorCarga && <p className={styles.errorSolicitud} role="alert">{errorCarga}</p>}
              {!cargando && !errorCarga && catalogoGrupos.length === 0 && (
                <p style={{ fontSize: '1.25rem' }}>No existen servicios activos por ahora.</p>
              )}

              {!cargando && !errorCarga && catalogoGrupos.length > 0 && (
                <>
                  {!grupoActivo ? (
                    <div>
                      <span className={ui.indicadorPaso}>Paso 1 de 3</span>
                      <h3 className={ui.tituloPaso}>Elige qué tipo de ayuda necesitas</h3>
                      <p className={ui.textoPaso}>Toca un grupo para ver las opciones disponibles.</p>
                      <div className={ui.grillaGrupos} role="list" aria-label="Grupos de ayuda">
                        {catalogoGrupos.map(grupo => (
                          <button
                            key={grupo.id}
                            type="button"
                            className={ui.tarjetaGrupo}
                            onClick={() => seleccionarGrupo(grupo)}
                            style={{ borderColor: grupo.color }}
                            role="listitem"
                          >
                            <div
                              className={ui.circuloIcono}
                              style={{ backgroundColor: grupo.color }}
                              aria-hidden="true"
                            >
                              <UiIcon name={grupo.icono} size={32} />
                            </div>
                            <div className={ui.infoGrupo}>
                              <span className={ui.nombreGrupo}>{grupo.nombre}</span>
                              <span className={ui.descripcionGrupo}>{grupo.descripcion}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <button
                        type="button"
                        className={ui.botonVolverPaso}
                        onClick={() => setGrupoActivo(null)}
                      >
                        ← Volver a categorías
                      </button>
                      <span className={ui.indicadorPaso}>Paso 2 de 3</span>
                      <h3 className={ui.tituloPaso}>Elige la tarea en {grupoActivo.nombre}</h3>
                      <p className={ui.textoPaso}>Selecciona la opción que mejor describa lo que necesitas.</p>

                      <div className={ui.listaTareas} role="list" aria-label={`Tareas en ${grupoActivo.nombre}`}>
                        {grupoActivo.tareas.map(tarea => (
                          <article
                            key={tarea.id}
                            className={ui.filaTarea}
                            style={{ borderColor: grupoActivo.color }}
                            role="listitem"
                          >
                            <div className={ui.filaTareaInfo}>
                              <div
                                className={ui.circuloIcono}
                                style={{ backgroundColor: grupoActivo.color }}
                                aria-hidden="true"
                              >
                                <UiIcon name={iconoTarea(tarea.nombre)} size={32} />
                              </div>
                              <div>
                                <h4 className={ui.nombreTarea}>{tarea.nombre}</h4>
                                <p className={ui.descripcionTarea}>{tarea.descripcion || 'Tarea cotidiana de apoyo.'}</p>
                              </div>
                            </div>
                            <button
                              type="button"
                              className={ui.botonPaso}
                              style={{ backgroundColor: grupoActivo.color }}
                              onClick={() => seleccionarTarea(tarea, grupoActivo)}
                            >
                              Elegir esta tarea →
                            </button>
                          </article>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              <p className={styles.nota}>Manos Amigas no presta servicios médicos ni tratamientos de salud.</p>
            </section>
          )}
          {vista === 'nueva' && seleccionado && (
            <FormularioSolicitud
              key={seleccionado.id}
              servicio={seleccionado}
              grupo={grupoActivo}
              onVolver={volverDesdeFormulario}
              onCreada={() => {
                refrescar();
                setSeleccionado(null);
                setGrupoActivo(null);
                navegar('solicitudes');
              }}
            />
          )}
          {vista === 'solicitudes' && (
            <section aria-labelledby="titulo-solicitudes">
              <div className={ui.tituloFila}>
                <h2 id="titulo-solicitudes" className={styles.tituloSeccion}>Mis solicitudes</h2>
                <button type="button" className={ui.botonActualizar} onClick={refrescar}>↻ Actualizar</button>
              </div>
              {cargando && <p role="status">Cargando solicitudes...</p>}
              {errorCarga && <p className={styles.errorSolicitud} role="alert">{errorCarga}</p>}
              {!cargando && !errorCarga && solicitudes.length === 0 && (
                <div className={styles.panelVacio}>
                  <span className={styles.iconoVacio} aria-hidden="true"><UiIcon name="solicitudes" size={35} /></span>
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
                      <p><strong>Fecha:</strong> {fechaBonita(sol.fecha_solicitada)} · {sol.duracion_horas || 'duración no indicada'}{sol.duracion_horas ? ' hora(s)' : ''}</p>
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
                              <FichaEstudiante postulacion={post} />
                              {post.estado === 'PENDIENTE' && (
                                <button type="button" className={styles.botonPrimario} disabled={accionEnCurso}
                                  onClick={() => aceptar(sol.id, post.id)}>Aceptar</button>
                              )}
                            </div>
                          ))}
                          {!cargandoPostulantes && !errorPostulantes && postulaciones.length > 0 && <NotaFichaEstudiante />}
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
          </div>
        </div>
        <footer className={styles.pie}>Manos Amigas · Solicitudes reales con acceso por rol · Sin pagos implementados</footer>
      </div>
    </div>
  );
}
