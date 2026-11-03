import styles from './Header.module.css';

export function LogoIcon({ className }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      fill="none"
      aria-hidden="true"
      className={className || styles.logoIcon}
    >
      {/* Background circle */}
      <circle cx="32" cy="32" r="32" fill="url(#logoGrad)" />
      {/* Hands forming a heart */}
      <g transform="translate(10, 12)">
        {/* Left hand */}
        <path
          d="M8 26 C6 22, 4 18, 8 14 C10 12, 13 12, 15 15 L22 24"
          stroke="white"
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Right hand */}
        <path
          d="M36 26 C38 22, 40 18, 36 14 C34 12, 31 12, 29 15 L22 24"
          stroke="white"
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Heart formed by hands */}
        <path
          d="M22 24 C22 24, 10 32, 22 40 C34 32, 22 24, 22 24Z"
          fill="white"
          opacity="0.9"
        />
        {/* Small decorative heart at top */}
        <circle cx="22" cy="8" r="3" fill="white" opacity="0.6" />
      </g>
      <defs>
        <linearGradient id="logoGrad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#F97316" />
          <stop offset="100%" stopColor="#FBBF24" />
        </linearGradient>
      </defs>
    </svg>
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


