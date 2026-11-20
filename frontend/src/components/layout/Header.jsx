import styles from './Header.module.css';
import logoIcono from '../../assets/images/logo-icono.png';

export function LogoIcon({ className }) {
  return (
    <img
      src={logoIcono}
      alt=""
      aria-hidden="true"
      className={className || styles.logoIcon}
    />
  );
}

export default function Header({ onLoginClick }) {
  return (
    <header className={styles.header} role="banner">
      <div className={`container ${styles.headerInner}`}>
        {/* Logo + Brand */}
        <div className={styles.brand}>
          <LogoIcon />
          <div className={styles.brandText}>
            <span className={styles.brandName}>Manos Amigas</span>
            <span className={styles.brandTagline}>Apoyo para tu familia</span>
          </div>
        </div>

        {/* Desktop Nav actions */}
        <nav className={styles.nav} aria-label="Navegación principal">
          <a href="#como-funciona" className={styles.navLink}>¿Cómo funciona?</a>
          <a href="#seguridad" className={styles.navLink}>Seguridad</a>
          <a href="#servicios" className={styles.navLink}>Servicios</a>
        </nav>

        {/* Action: Iniciar sesión visible on mobile and desktop */}
        <div className={styles.headerActions}>
          <button
            id="header-login-btn"
            className={styles.loginBtn}
            title={onLoginClick ? "Ir a iniciar sesión" : "Próximamente — funcionalidad en desarrollo"}
            aria-label="Iniciar sesión"
            type="button"
            onClick={onLoginClick}
          >
            Iniciar sesión
          </button>
        </div>
      </div>
    </header>
  );
}