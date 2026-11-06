import { useState } from 'react';
import { LogoIcon } from '../../components/layout/Header';
import { loginUser } from '../../services/sessionService';
import styles from './Login.module.css';

const CURRENT_YEAR = new Date().getFullYear();

export default function Login({ onNavigateHome, onNavigateRegister, onLoginSuccess, onForgotPassword }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [infoMessage, setInfoMessage] = useState('');
  const [serverError, setServerError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const newErrors = {
      email: '',
      password: '',
    };

    if (!email.trim()) {
      newErrors.email = 'Ingresa tu correo electrónico.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      newErrors.email = 'Ingresa un correo electrónico válido.';
    }

    if (!password) {
      newErrors.password = 'Ingresa tu contraseña.';
    }

    setErrors(newErrors);

    if (newErrors.email || newErrors.password) {
      setInfoMessage('');
      setServerError('');
      return;
    }

    setServerError('');
    setInfoMessage('');
    setIsLoading(true);

    try {
      const data = await loginUser(email.trim(), password);
      setInfoMessage(`¡Bienvenido/a, ${data.user.nombre}! Inicio de sesión correcto.`);
      if (typeof onLoginSuccess === 'function') {
        onLoginSuccess(data.user, data.access_token);
      }
    } catch (err) {
      setServerError(err.message || 'Error al iniciar sesión.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = () => {
    onForgotPassword?.();
  };

  const handleRegisterNotice = () => {
    onNavigateRegister?.();
  };

  return (
    <div className={styles.page}>
      {/* Top navigation bar */}
      <header className={styles.topBar}>
        <div className={`container ${styles.topBarInner}`}>
          {onNavigateHome ? (
            <button
              id="login-back-btn"
              type="button"
              className={styles.backBtn}
              onClick={onNavigateHome}
              aria-label="Volver a la pantalla de inicio"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M19 12H5M5 12L12 19M5 12L12 5"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span>Volver al inicio</span>
            </button>
          ) : (
            <div className={styles.topSpacer} />
          )}

          <div className={styles.miniBrand} aria-hidden="true">
            <span className={styles.miniBrandName}>Manos Amigas</span>
          </div>
        </div>
      </header>

      {/* Main login container */}
      <main className={styles.mainContainer} id="main-content">
        <div className={`container ${styles.contentWrapper}`}>
          <div className={styles.card}>
            {/* Brand Header */}
            <div className={styles.brandHeader}>
              <div className={styles.logoWrap}>
                <LogoIcon className={styles.brandLogo} />
              </div>
              <h2 className={styles.brandTitle}>Manos Amigas</h2>
              <p className={styles.brandTagline}>Apoyo confiable para tu familia</p>
            </div>

            {/* Form Title & Context */}
            <div className={styles.formHeader}>
              <h1 id="login-heading" className={styles.formTitle}>
                Iniciar sesión
              </h1>
              <p className={styles.formSubtitle}>
                Ingresa con tu cuenta para coordinar y supervisar el apoyo cotidiano de tu familiar.
              </p>
            </div>

            {/* Server Error Banner */}
            {serverError && (
              <div
                className={styles.infoBanner}
                style={{ borderColor: '#fca5a5', background: '#fef2f2', color: '#991b1b' }}
                role="alert"
                aria-live="assertive"
              >
                <span className={styles.infoIcon} aria-hidden="true">⚠️</span>
                <p className={styles.infoText}>{serverError}</p>
                <button
                  type="button"
                  className={styles.closeBannerBtn}
                  style={{ color: '#991b1b' }}
                  onClick={() => setServerError('')}
                  aria-label="Cerrar error"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Info / Success message */}
            {infoMessage && (
              <div className={styles.infoBanner} role="status" aria-live="polite">
                <span className={styles.infoIcon} aria-hidden="true">ℹ️</span>
                <p className={styles.infoText}>{infoMessage}</p>
                <button
                  type="button"
                  className={styles.closeBannerBtn}
                  onClick={() => setInfoMessage('')}
                  aria-label="Cerrar mensaje"
                >
                  ✕
                </button>
              </div>
            )}

            {/* Login Form */}
            <form onSubmit={handleSubmit} noValidate className={styles.form}>
              {/* Email field */}
              <div className={styles.fieldGroup}>
                <label htmlFor="login-email" className={styles.label}>
                  Correo electrónico
                </label>
                <div className={styles.inputWrapper}>
                  <svg
                    className={styles.inputIcon}
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                    />
                    <path
                      d="M22 6l-10 7L2 6"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                    />
                  </svg>
                  <input
                    id="login-email"
                    name="email"
                    type="email"
                    inputMode="email"
                    autoComplete="email"
                    placeholder="nombre@ejemplo.com"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (errors.email) {
                        setErrors((prev) => ({ ...prev, email: '' }));
                      }
                      if (serverError) setServerError('');
                    }}
                    className={styles.input}
                    required
                  />
                </div>
                {errors.email && (
                  <p className={styles.fieldError} role="alert">
                    {errors.email}
                  </p>
                )}
              </div>

              {/* Password field */}
              <div className={styles.fieldGroup}>
                <div className={styles.labelRow}>
                  <label htmlFor="login-password" className={styles.label}>
                    Contraseña
                  </label>
                  <button
                    type="button"
                    id="login-forgot-password-btn"
                    className={styles.forgotBtn}
                    onClick={handleForgotPassword}
                    title="Recuperar acceso a mi cuenta"
                  >
                    ¿Olvidaste tu contraseña?
                  </button>
                </div>
                <div className={styles.inputWrapper}>
                  <svg
                    className={styles.inputIcon}
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    aria-hidden="true"
                  >
                    <rect
                      x="3"
                      y="11"
                      width="18"
                      height="11"
                      rx="2"
                      ry="2"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    />
                    <path
                      d="M7 11V7a5 5 0 0 1 10 0v4"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                    />
                  </svg>
                  <input
                    id="login-password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="Tu contraseña"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (errors.password) {
                        setErrors((prev) => ({ ...prev, password: '' }));
                      }
                      if (serverError) setServerError('');
                    }}
                    className={styles.input}
                    required
                  />
                  <button
                    type="button"
                    className={styles.eyeBtn}
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={showPassword ? 'Ocultar contraseña' : 'Ver contraseña'}
                  >
                    {showPassword ? (
                      /* Eye-off icon */
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <path
                          d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    ) : (
                      /* Eye icon */
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <path
                          d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
                          stroke="currentColor"
                          strokeWidth="1.8"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                        <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
                      </svg>
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className={styles.fieldError} role="alert">
                    {errors.password}
                  </p>
                )}
              </div>

              {/* Submit button */}
              <button
                id="login-submit-btn"
                type="submit"
                className={styles.submitBtn}
                aria-label="Iniciar sesión con mi cuenta"
                disabled={isLoading}
              >
                <span>{isLoading ? 'Iniciando sesión...' : 'Iniciar sesión'}</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path
                    d="M5 12h14M12 5l7 7-7 7"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </form>

            {/* Registration option */}
            <div className={styles.registerBox}>
              <p className={styles.registerText}>
                ¿Aún no tienes una cuenta?{' '}
                <button
                  type="button"
                  id="login-register-link-btn"
                  className={styles.registerBtn}
                  onClick={handleRegisterNotice}
                >
                  Regístrate aquí
                </button>
              </p>
            </div>

            {/* Trust and privacy reassuring note */}
            <div className={styles.securityFooter} aria-label="Información de seguridad">
              <span className={styles.securityIcon} aria-hidden="true">🔒</span>
              <span className={styles.securityText}>
                Confianza y tranquilidad para tu familia
              </span>
            </div>
          </div>
        </div>
      </main>

      {/* Discreet footer */}
      <footer className={styles.pageFooter}>
        <p className={styles.footerText}>
          © {CURRENT_YEAR} Manos Amigas · Prototipo en desarrollo
        </p>
      </footer>

    </div>
  );
}
