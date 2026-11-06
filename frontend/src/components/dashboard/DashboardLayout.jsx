import { useState } from 'react';
import styles from './DashboardLayout.module.css';

// Conserva los mismos identificadores de vista: cambia solo la presentación del menú.
const GRUPOS = [
  {
    titulo: 'Principal',
    vistas: ['inicio', 'oportunidades', 'adultos', 'solicitudes', 'nueva', 'postulaciones', 'seguimiento'],
  },
  {
    titulo: 'Comunicación y agenda',
    vistas: ['chat', 'avisos', 'disponibilidad', 'agenda', 'calificaciones'],
  },
  {
    titulo: 'Mi cuenta',
    vistas: ['verificacion', 'perfil'],
  },
];

function agruparNavegacion(navegacion) {
  const grupos = GRUPOS.map((grupo) => ({
    titulo: grupo.titulo,
    items: navegacion.filter((item) => grupo.vistas.includes(item.id)),
  })).filter((grupo) => grupo.items.length > 0);

  const conocidos = new Set(GRUPOS.flatMap((grupo) => grupo.vistas));
  const otros = navegacion.filter((item) => !conocidos.has(item.id));
  if (otros.length) grupos.push({ titulo: 'Otras secciones', items: otros });

  return grupos;
}

/**
 * Estructura visual compartida por UNIVERSITARIO y FAMILIAR.
 * La autenticación, los permisos y las llamadas a la API siguen en App.jsx y Flask.
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
  const [menuAbierto, setMenuAbierto] = useState(false);
  const primerNombre = usuario?.nombre?.trim().split(/\s+/)[0] || 'Bienvenido/a';
  const grupos = agruparNavegacion(navegacion);
  const vistaActual = navegacion.find((item) => item.id === vista)?.nombre || 'Mi panel';

  function cambiarVista(id) {
    onCambiarVista(id);
    setMenuAbierto(false);
  }

  return (
    <div className={styles.pagina}>
      <a className={styles.saltar} href="#contenido-panel">Saltar al contenido</a>

      <header className={styles.barra}>
        <div className={styles.barraInterior}>
          <div className={styles.marca}>
            <span className={styles.logo} aria-hidden="true">♥</span>
            <span>
              <strong>Manos Amigas</strong>
              <small>Ayuda entre generaciones</small>
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
            <p className={styles.sobretitulo}>Tu espacio · {tituloRol}</p>
            <h1>Hola, {primerNombre} <span aria-hidden="true">👋</span></h1>
            <p className={styles.subtitulo}>{subtitulo}</p>
          </div>
          <span className={styles.etiquetaRol}>{tituloRol}</span>
        </div>

        <div className={styles.layout}>
          <button
            type="button"
            className={styles.menuMovil}
            aria-expanded={menuAbierto}
            aria-controls="navegacion-panel"
            onClick={() => setMenuAbierto((abierto) => !abierto)}
          >
            <span aria-hidden="true">☰</span>
            <span>{menuAbierto ? 'Ocultar secciones' : 'Ver secciones del panel'}</span>
            <span aria-hidden="true">{menuAbierto ? '−' : '+'}</span>
          </button>

          <aside
            id="navegacion-panel"
            className={`${styles.barraLateral} ${menuAbierto ? styles.barraLateralAbierta : ''}`}
          >
            <div className={styles.encabezadoLateral}>
              <strong>Mi panel</strong>
              <span>Explora tus secciones</span>
            </div>
            <nav className={styles.navegacion} aria-label={`Secciones del panel de ${tituloRol.toLowerCase()}`}>
              {grupos.map((grupo) => (
                <div className={styles.grupoNavegacion} key={grupo.titulo}>
                  <p className={styles.grupoTitulo}>{grupo.titulo}</p>
                  {grupo.items.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      className={`${styles.pestana} ${vista === item.id ? styles.activa : ''}`}
                      aria-current={vista === item.id ? 'page' : undefined}
                      onClick={() => cambiarVista(item.id)}
                    >
                      <span className={styles.iconoNavegacion} aria-hidden="true">{item.icono}</span>
                      <span>{item.nombre}</span>
                    </button>
                  ))}
                </div>
              ))}
            </nav>
          </aside>

          <div className={styles.panelPrincipal}>
            <div className={styles.cabeceraVista}>
              <span className={styles.etiquetaVista}>ESTÁS EN</span>
              <p>{vistaActual}</p>
            </div>
            <main id="contenido-panel" className={styles.contenido}>{children}</main>
            <footer className={styles.pie}>
              <span>Manos Amigas · {tituloRol}</span>
              <span>Un espacio para conectar y acompañar.</span>
            </footer>
          </div>
        </div>
      </div>
    </div>
  );
}
