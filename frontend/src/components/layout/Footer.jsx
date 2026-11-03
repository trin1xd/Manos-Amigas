import styles from './Footer.module.css';

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className={styles.footer} role="contentinfo">
      <div className="container">
        <div className={styles.footerGrid}>
          {/* Brand column */}
          <div className={styles.brandCol}>
            <div className={styles.brandName}>Manos Amigas</div>
            <p className={styles.brandDesc}>
              Conectamos familias con estudiantes universitarios verificados
              para apoyar a personas mayores con calidez y confianza.
            </p>
            <div className={styles.socialLinks} aria-label="Redes sociales">
              <a href="#" id="footer-instagram" className={styles.socialLink} aria-label="Instagram">
                <svg viewBox="0 0 24 24" fill="none"><rect x="2" y="2" width="20" height="20" rx="5" stroke="currentColor" strokeWidth="2"/><circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="2"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor"/></svg>
              </a>
              <a href="#" id="footer-facebook" className={styles.socialLink} aria-label="Facebook">
                <svg viewBox="0 0 24 24" fill="none"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </a>
              <a href="#" id="footer-whatsapp" className={styles.socialLink} aria-label="WhatsApp">
                <svg viewBox="0 0 24 24" fill="none"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              </a>
            </div>
          </div>

          {/* Links columns */}
          <nav className={styles.linksCol} aria-label="Plataforma">
            <h4 className={styles.colTitle}>Plataforma</h4>
            <ul>
              <li><a href="#como-funciona">¿Cómo funciona?</a></li>
              <li><a href="#servicios">Servicios</a></li>
              <li><a href="#">Para estudiantes</a></li>
              <li><a href="#">Para familias</a></li>
            </ul>
          </nav>

          <nav className={styles.linksCol} aria-label="Soporte">
            <h4 className={styles.colTitle}>Soporte</h4>
            <ul>
              <li><a href="#">Preguntas frecuentes</a></li>
              <li><a href="#">Centro de ayuda</a></li>
              <li><a href="#">Contáctanos</a></li>
            </ul>
          </nav>

          <nav className={styles.linksCol} aria-label="Legal">
            <h4 className={styles.colTitle}>Legal</h4>
            <ul>
              <li><a href="#">Términos de uso</a></li>
              <li><a href="#">Privacidad</a></li>
              <li><a href="#">Verificación</a></li>
            </ul>
          </nav>
        </div>

        {/* Bottom bar */}
        <div className={styles.bottomBar}>
          <p className={styles.copyright}>
            © {year} Manos Amigas. Hecho con ❤️ para quienes más lo necesitan.
          </p>
          <p className={styles.madeWith}>
            Plataforma en desarrollo — Prototipo académico
          </p>
        </div>
      </div>
    </footer>
  );
}
