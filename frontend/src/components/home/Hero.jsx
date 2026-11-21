/* MANOS AMIGAS UI V6 - ACCESIBILIDAD INTEGRADA */
import { useEffect, useState } from 'react';
import styles from './Hero.module.css';
import { LogoIcon } from '../layout/Header';
import AccessibilityToolbar from '../accessibility/AccessibilityToolbar';

export default function Hero({
  onLoginClick,
  onCreateAccountClick,
  onDemoClick,
}) {
  const [textoGrande, setTextoGrande] = useState(() => {
    try {
      return typeof window !== 'undefined' && localStorage.getItem('manos_amigas_texto_grande') === 'true';
    } catch {
      return false;
    }
  });
  const [mostrarAyuda, setMostrarAyuda] = useState(false);
  const [demoCargando, setDemoCargando] = useState('');
  const [errorDemo, setErrorDemo] = useState('');
  const feria = import.meta.env.VITE_MODO_FERIA === 'true';

  async function probarComo(rol) {
    if (demoCargando) return;
    setErrorDemo('');
    setDemoCargando(rol);
    try {
      await onDemoClick(rol);
    } catch (e) {
      setErrorDemo(e.message || 'No pudimos iniciar la demostración.');
    } finally {
      setDemoCargando('');
    }
  }

  useEffect(() => {
    const sincronizarTexto = (evento) => setTextoGrande(Boolean(evento.detail));
    window.addEventListener('manos-amigas:texto-grande', sincronizarTexto);
    return () => window.removeEventListener('manos-amigas:texto-grande', sincronizarTexto);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('texto-grande', textoGrande);
    try {
      localStorage.setItem('manos_amigas_texto_grande', String(textoGrande));
    } catch {
      // Preferencia solo durante la sesión si el navegador bloquea el almacenamiento.
    }
  }, [textoGrande]);

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
          {feria
            ? 'Estás en una demostración académica con cuentas ficticias. Explora cómo se solicitan y coordinan ayudas, sin servicios reales.'
            : 'Conectamos a familias con estudiantes universitarios verificados para brindar apoyo seguro en tareas del día a día.'}
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

        {feria && (
          <div className={styles.feriaPanel}>
            <strong>¿Quieres probar la aplicación?</strong>
            <p>Entra sin registrarte ni usar datos personales. Todo es una demostración.</p>
            <button type="button" className={styles.feriaBoton}
              onClick={() => probarComo('ADULTO_MAYOR')} disabled={!!demoCargando}>
              {demoCargando === 'ADULTO_MAYOR' ? 'Ingresando...' : 'Probar como adulto mayor'}
            </button>
            <button type="button" className={styles.feriaBoton}
              onClick={() => probarComo('UNIVERSITARIO')} disabled={!!demoCargando}>
              {demoCargando === 'UNIVERSITARIO' ? 'Ingresando...' : 'Probar como universitario'}
            </button>
            {errorDemo && <p role="alert" className={styles.feriaError}>{errorDemo}</p>}
          </div>
        )}

        <div className={styles.accessibility}>
          <div id="manos-accesibilidad-home" className={styles.accesibilidadIntegrada}>
            <AccessibilityToolbar integrada />
          </div>
          <button
            type="button"
            className={styles.accessibilityButton}
            aria-expanded={mostrarAyuda}
            aria-controls="ayuda-inicio"
            onClick={() => setMostrarAyuda(valor => !valor)}
          >
            <span className={styles.helpIcon}>?</span>
            Ayuda
          </button>
        </div>

        {mostrarAyuda && (
          <div id="ayuda-inicio" className={styles.panelAyuda} role="region" aria-label="Ayuda para comenzar">
            <strong>¿Cómo comenzar?</strong>
            <p>Selecciona «Crear cuenta» y elige tu perfil: adulto mayor, universitario o familiar.</p>
            <p>Si ya tienes una cuenta, presiona «Iniciar sesión» con tu correo y contraseña.</p>
            <p>Manos Amigas es un prototipo de apoyo cotidiano; no ofrece atención médica ni servicios de emergencia.</p>
          </div>
        )}

      </div>
    </section>
  );
}