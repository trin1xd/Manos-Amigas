import styles from './Hero.module.css';
import { LogoIcon } from '../layout/Header';

export default function Hero({
  onLoginClick,
  onCreateAccountClick,
}) {
  return (
    <section
      className={styles.hero}
      aria-labelledby="hero-heading"
    >
      <div className={`container ${styles.heroContent}`}>

        <div className={styles.logoContainer}>
          <LogoIcon className={styles.logo} />
        </div>

        <div className={styles.brand}>
          <h1
            id="hero-heading"
            className={styles.heading}
          >
            Manos Amigas
          </h1>

          <p className={styles.tagline}>
            Ayuda entre generaciones
          </p>
        </div>

        <p className={styles.subtitle}>
          Conectamos a familias con estudiantes universitarios
          verificados para brindar apoyo seguro en tareas del día a día.
        </p>

        <div className={styles.ctas}>
          <button
            type="button"
            className={styles.btnPrimary}
            onClick={onLoginClick}
          >
            Iniciar sesión
          </button>

          <button
            type="button"
            className={styles.btnSecondary}
            onClick={onCreateAccountClick}
          >
            Crear cuenta
          </button>
        </div>

        <div className={styles.accessibility}>
          <button
            type="button"
            className={styles.accessibilityButton}
          >
            <span className={styles.aa}>Aa</span>
            Texto grande
          </button>

          <span className={styles.divider} />

          <button
            type="button"
            className={styles.accessibilityButton}
          >
            <span className={styles.helpIcon}>?</span>
            Ayuda
          </button>
        </div>

      </div>
    </section>
  );
}