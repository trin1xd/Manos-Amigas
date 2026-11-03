import { useState } from 'react';
import styles from './AdultoMayorDashboard.module.css';
import SolicitarTarea, { formatoFecha, formatoPesos } from './SolicitarTarea';

// Catálogo temporal del prototipo. Las tareas y precios definitivos vendrán del backend.
const SERVICIOS_DEMO = [
  { id: 'lena', icono: '🪵', nombre: 'Cortar leña', descripcion: 'Cortar, apilar y acercar la leña a la estufa.' },
  { id: 'aseo', icono: '🧹', nombre: 'Aseo y orden', descripcion: 'Limpiar, ordenar y ayudar con tareas del hogar.' },
  { id: 'cocina', icono: '🥣', nombre: 'Cocina y comida', descripcion: 'Preparar comidas sencillas o ayudar con la cocina.' },
  { id: 'tramites', icono: '📄', nombre: 'Trámites', descripcion: 'Acompañamiento en trámites cotidianos.' },
  { id: 'compras', icono: '🛍️', nombre: 'Compras', descripcion: 'Ayuda con compras en el supermercado o feria.' },
  { id: 'jardin', icono: '🌿', nombre: 'Jardín y huerto', descripcion: 'Regar plantas y cuidar el jardín.' },
  { id: 'arreglos', icono: '🛠️', nombre: 'Arreglos menores', descripcion: 'Ayuda con ajustes simples en el hogar.' },
  { id: 'compania', icono: '💛', nombre: 'Compañía', descripcion: 'Conversar, pasear o compartir actividades.' },
  { id: 'mascotas', icono: '🐾', nombre: 'Mascotas', descripcion: 'Pasear mascotas y ayudar con su cuidado cotidiano.' },
  { id: 'tecnologia', icono: '📱', nombre: 'Ayuda con tecnología', descripcion: 'Aprender a usar el celular o hacer videollamadas.' },
];

const SECCIONES = [
  { clave: 'inicio', etiqueta: 'Inicio' },
  { clave: 'catalogo', etiqueta: 'Pedir ayuda' },
  { clave: 'solicitudes', etiqueta: 'Mis solicitudes' },
  { clave: 'perfil', etiqueta: 'Mi perfil' },
];

export default function AdultoMayorDashboard() {
  const [vista, setVista] = useState('inicio');
  const [servicioElegido, setServicioElegido] = useState(null);
  const [solicitudesDemo, setSolicitudesDemo] = useState([]);

  function navegar(destino) {
    setVista(destino);
    if (destino !== 'nueva-solicitud') setServicioElegido(null);
  }

  function elegirServicio(servicio) {
    setServicioElegido(servicio);
    setVista('nueva-solicitud');
  }

  function confirmarSolicitud(datos) {
    // Solo memoria local de React: no hace peticiones a Flask ni guarda datos.
    setSolicitudesDemo((previas) => [
      { ...datos, id: `demo-${previas.length + 1}` },
      ...previas,
    ]);
  }

  return (
    <div className={styles.pagina}>
      <header className={styles.cabecera}>
        <div className={styles.cabeceraInterior}>
          <div className={styles.marca}>
            <span className={styles.marcaIcono} aria-hidden="true">♥</span>
            <span>Manos Amigas</span>
          </div>
          <span className={styles.demoEtiqueta}>Vista de demostración</span>
        </div>
      </header>

      <div className={styles.contenedor}>
        <div className={styles.presentacion}>
          <p className={styles.sobretitulo}>Espacio de adulto mayor</p>
          <h1>Hola, Rosa <span aria-hidden="true">👋</span></h1>
          <p>¿En qué podemos ayudarte hoy?</p>
        </div>

        <nav className={styles.navegacion} aria-label="Secciones del panel de adulto mayor">
          {SECCIONES.map(({ clave, etiqueta }) => (
            <button
              className={`${styles.pestana} ${((vista === 'nueva-solicitud' && clave === 'catalogo') || vista === clave) ? styles.pestanaActiva : ''}`}
              key={clave}
              type="button"
              aria-current={((vista === 'nueva-solicitud' && clave === 'catalogo') || vista === clave) ? 'page' : undefined}
              onClick={() => navegar(clave)}
            >
              {etiqueta}
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
                  <p>Selecciona el tipo de apoyo que necesitas y completa una solicitud.</p>
                  <button type="button" className={styles.botonNaranja} onClick={() => navegar('catalogo')}>
                    Ver tareas disponibles
                  </button>
                </div>
                <span className={styles.corazonGrande} aria-hidden="true">♡</span>
              </section>

              <section aria-labelledby="titulo-accesos">
                <h2 id="titulo-accesos" className={styles.tituloSeccion}>¿Qué necesitas hacer?</h2>
                <div className={styles.grillaAccesos}>
                  <button type="button" className={styles.acceso} onClick={() => navegar('catalogo')}>
                    <span aria-hidden="true" className={styles.accesoIcono}>🧹</span>
                    <strong>Pedir ayuda</strong>
                    <span>Explorar tareas para tu hogar</span>
                  </button>
                  <button type="button" className={styles.acceso} onClick={() => navegar('solicitudes')}>
                    <span aria-hidden="true" className={styles.accesoIcono}>📋</span>
                    <strong>Mis solicitudes</strong>
                    <span>Consultar solicitudes de demostración</span>
                  </button>
                  <button type="button" className={styles.acceso} onClick={() => navegar('perfil')}>
                    <span aria-hidden="true" className={styles.accesoIcono}>👤</span>
                    <strong>Mi perfil</strong>
                    <span>Revisar tus datos de ejemplo</span>
                  </button>
                </div>
              </section>
            </>
          )}

          {vista === 'catalogo' && (
            <section aria-labelledby="titulo-catalogo">
              <h2 id="titulo-catalogo" className={styles.tituloSeccion}>Tareas disponibles</h2>
              <p className={styles.textoAyuda}>Elige una tarea para completar una solicitud de demostración.</p>
              <div className={styles.grillaServicios}>
                {SERVICIOS_DEMO.map((servicio) => (
                  <article key={servicio.id} className={styles.servicio}>
                    <span className={styles.servicioIcono} aria-hidden="true">{servicio.icono}</span>
                    <h3>{servicio.nombre}</h3>
                    <p>{servicio.descripcion}</p>
                    <button type="button" className={styles.botonSecundario} onClick={() => elegirServicio(servicio)}>
                      Elegir esta tarea
                    </button>
                  </article>
                ))}
              </div>
              <p className={styles.nota}>No incluye tareas médicas: curaciones, inyecciones, medicamentos ni tratamientos de salud.</p>
            </section>
          )}

          {vista === 'nueva-solicitud' && servicioElegido && (
            <SolicitarTarea
              servicio={servicioElegido}
              onVolver={() => navegar('catalogo')}
              onConfirmar={confirmarSolicitud}
              onVerSolicitudes={() => navegar('solicitudes')}
            />
          )}

          {vista === 'solicitudes' && (
            <section aria-labelledby="titulo-solicitudes">
              <h2 id="titulo-solicitudes" className={styles.tituloSeccion}>Mis solicitudes</h2>
              <p className={styles.alertaDemo}>Estas solicitudes son simuladas y solo existen mientras esta página esté abierta. No están guardadas en SQL Server ni se han enviado a estudiantes.</p>
              {solicitudesDemo.length === 0 ? (
                <div className={styles.panelVacio}>
                  <span className={styles.iconoVacio} aria-hidden="true">📋</span>
                  <p>Todavía no has creado solicitudes de demostración.</p>
                  <button type="button" className={styles.botonPrimario} onClick={() => navegar('catalogo')}>
                    Explorar tareas
                  </button>
                </div>
              ) : (
                <div className={styles.listaSolicitudes}>
                  {solicitudesDemo.map((solicitud) => (
                    <article className={styles.tarjetaSolicitud} key={solicitud.id}>
                      <div className={styles.encabezadoSolicitud}>
                        <h3>{solicitud.servicioIcono} {solicitud.servicioNombre}</h3>
                        <span className={styles.estadoDemo}>Simulada</span>
                      </div>
                      <p><strong>Fecha:</strong> {formatoFecha(solicitud.fecha)} · {solicitud.hora}</p>
                      <p><strong>Duración:</strong> {solicitud.duracion} {solicitud.duracion === 1 ? 'hora' : 'horas'}</p>
                      <p><strong>Descripción:</strong> {solicitud.descripcion}</p>
                      <p><strong>Precio referencial de ejemplo:</strong> {formatoPesos(solicitud.precioEstimado)}</p>
                    </article>
                  ))}
                  <button type="button" className={styles.botonPrimario} onClick={() => navegar('catalogo')}>
                    Pedir otra tarea de prueba
                  </button>
                </div>
              )}
            </section>
          )}

          {vista === 'perfil' && (
            <section className={styles.panelPerfil} aria-labelledby="titulo-perfil">
              <h2 id="titulo-perfil">Mi perfil</h2>
              <p className={styles.textoAyuda}>Información ficticia solo para comprobar el diseño.</p>
              <dl className={styles.listaPerfil}>
                <div><dt>Nombre</dt><dd>Rosa (ejemplo)</dd></div>
                <div><dt>Tipo de cuenta</dt><dd>Adulto mayor</dd></div>
                <div><dt>Contacto de confianza</dt><dd>Se administra durante el registro</dd></div>
              </dl>
              <p className={styles.nota}>La dirección y los contactos personales no se muestran en esta demo. Más adelante se cargarán de forma segura desde el backend.</p>
            </section>
          )}
        </main>
        <footer className={styles.pie}>Manos Amigas · Dashboard de demostración · Sin datos personales reales</footer>
      </div>
    </div>
  );
}
