import { useState } from 'react';
import styles from './AdultoMayorDashboard.module.css';

// Datos de ejemplo para diseñar la interfaz. NO provienen de SQL Server.
const SERVICIOS_DEMO = [
  { id: 'aseo', icono: '🧹', nombre: 'Aseo y orden', descripcion: 'Ayuda para mantener la casa ordenada.' },
  { id: 'compras', icono: '🛍️', nombre: 'Compras', descripcion: 'Apoyo con compras del supermercado o feria.' },
  { id: 'compania', icono: '💛', nombre: 'Compañía', descripcion: 'Conversar, pasear o compartir actividades.' },
  { id: 'tecnologia', icono: '📱', nombre: 'Ayuda con tecnología', descripcion: 'Aprender a usar el celular o hacer videollamadas.' },
  { id: 'jardin', icono: '🌿', nombre: 'Jardín y huerto', descripcion: 'Regar plantas y cuidar el jardín.' },
  { id: 'cocina', icono: '🥣', nombre: 'Cocina y comida', descripcion: 'Ayuda para preparar comidas sencillas.' },
];

const SECCIONES = [
  { clave: 'inicio', etiqueta: 'Inicio' },
  { clave: 'catalogo', etiqueta: 'Pedir ayuda' },
  { clave: 'solicitudes', etiqueta: 'Mis solicitudes' },
  { clave: 'perfil', etiqueta: 'Mi perfil' },
];

export default function AdultoMayorDashboard() {
  const [vista, setVista] = useState('inicio');
  const [aviso, setAviso] = useState('');

  function navegar(destino) {
    setVista(destino);
    setAviso('');
  }

  function consultarServicio(nombre) {
    setAviso(`“${nombre}” está disponible como ejemplo. La creación real de solicitudes se implementará en una etapa posterior.`);
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
              className={`${styles.pestana} ${vista === clave ? styles.pestanaActiva : ''}`}
              key={clave}
              type="button"
              aria-current={vista === clave ? 'page' : undefined}
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
                    <span>Consultar servicios solicitados</span>
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
              <p className={styles.textoAyuda}>Elige una tarea. En esta demostración todavía no se crean solicitudes reales.</p>
              <div className={styles.grillaServicios}>
                {SERVICIOS_DEMO.map((servicio) => (
                  <article key={servicio.id} className={styles.servicio}>
                    <span className={styles.servicioIcono} aria-hidden="true">{servicio.icono}</span>
                    <h3>{servicio.nombre}</h3>
                    <p>{servicio.descripcion}</p>
                    <button type="button" className={styles.botonSecundario} onClick={() => consultarServicio(servicio.nombre)}>
                      Elegir esta tarea
                    </button>
                  </article>
                ))}
              </div>
              {aviso && <p className={styles.aviso} role="status">{aviso}</p>}
              <p className={styles.nota}>Manos Amigas no ofrece servicios médicos, medicamentos ni tratamientos de salud.</p>
            </section>
          )}

          {vista === 'solicitudes' && (
            <section className={styles.panelVacio} aria-labelledby="titulo-solicitudes">
              <span className={styles.iconoVacio} aria-hidden="true">📋</span>
              <h2 id="titulo-solicitudes">Mis solicitudes</h2>
              <p>Este es el espacio donde podrás consultar los servicios que hayas pedido.</p>
              <p className={styles.textoAyuda}>En la demostración no se muestran solicitudes reales.</p>
              <button type="button" className={styles.botonPrimario} onClick={() => navegar('catalogo')}>Explorar tareas</button>
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
