import styles from './DashboardLayout.module.css';

/**
 * Estructura visual compartida por los paneles de UNIVERSITARIO y FAMILIAR.
 * La autenticación y la comprobación del rol se hacen en App.jsx / Flask.
 */
export default function DashboardLayout({
  usuario,
  onLogout,
  tituloRol,
  subtitulo,
  navegacion,
  vista,
  onCambiarVista,
  children,
}) {
  const primerNombre = usuario?.nombre?.trim().split(/\s+/)[0] || 'Bienvenido/a';

  return (
    <div className={styles.pagina}>
      <a className={styles.saltar} href="#contenido-panel">Saltar al contenido</a>
      <header className={styles.barra}>
        <div className={styles.barraInterior}>
          <div className={styles.marca}>
            <span className={styles.logo} aria-hidden="true">♥</span>
            <span>
              <strong>Manos Amigas</strong>
              <small>Apoyo confiable para tu familia</small>
            </span>
          </div>
          <button className={styles.salir} type="button" onClick={onLogout}>
            Cerrar sesión <span aria-hidden="true">↗</span>
          </button>
        </div>
      </header>

      <div className={styles.contenedor}>
        <div className={styles.bienvenida}>
          <div>
            <p className={styles.sobretitulo}>Espacio de {tituloRol.toLowerCase()}</p>
            <h1>Hola, {primerNombre} <span aria-hidden="true">👋</span></h1>
            <p className={styles.subtitulo}>{subtitulo}</p>
          </div>
          <span className={styles.etiquetaRol}>{tituloRol}</span>
        </div>

        <nav className={styles.navegacion} aria-label={`Secciones del panel de ${tituloRol.toLowerCase()}`}>
          {navegacion.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`${styles.pestana} ${vista === item.id ? styles.activa : ''}`}
              aria-current={vista === item.id ? 'page' : undefined}
              onClick={() => onCambiarVista(item.id)}
            >
              <span aria-hidden="true">{item.icono}</span> {item.nombre}
            </button>
          ))}
        </nav>

        <main id="contenido-panel" className={styles.contenido}>{children}</main>
        <footer className={styles.pie}>
          <span>Manos Amigas · Panel {tituloRol.toLowerCase()}</span>
          <span>Los servicios y las solicitudes reales se conectarán en una próxima etapa.</span>
        </footer>
      </div>
    </div>
  );
}
