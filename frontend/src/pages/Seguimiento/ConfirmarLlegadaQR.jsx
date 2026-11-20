import { useState } from 'react';
import { confirmarLlegadaPorQr } from '../../services/seguimientoService';
import styles from './ConfirmarLlegadaQR.module.css';

// El enlace del QR nunca registra la llegada automáticamente.
// Siempre requiere que el estudiante asignado inicie sesión y confirme.
export default function ConfirmarLlegadaQR({ token, usuario, onVolver, onCambiarCuenta }) {
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState('');

  async function confirmar() {
    setEnviando(true);
    setError('');
    try {
      const llegada = await confirmarLlegadaPorQr(token);
      setResultado(llegada);
    } catch (err) {
      setError(err.message || 'No pudimos confirmar la llegada.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className={styles.pagina}>
      <section className={styles.tarjeta} aria-labelledby="titulo-qr-llegada">
        <h1 id="titulo-qr-llegada">Confirmar llegada</h1>
        {usuario?.rol !== 'UNIVERSITARIO' ? (
          <>
            <p>Este código debe abrirlo el universitario asignado al servicio.</p>
            <p>La sesión actual no es de universitario. Cambia de cuenta para continuar.</p>
            <button type="button" onClick={onCambiarCuenta}>Iniciar sesión como universitario</button>
          </>
        ) : resultado ? (
          <>
            <p className={styles.exito} role="status">
              ¡Llegada registrada para el servicio #{resultado.id}!
            </p>
            <p>Ya puedes continuar con el inicio del servicio desde Seguimiento.</p>
          </>
        ) : (
          <>
            <p>Hola, {usuario.nombre}. Confirma solo si realmente llegaste al lugar acordado.</p>
            <p>Este código es temporal. La confirmación se guardará en el historial del servicio.</p>
            {error && <p className={styles.error} role="alert">{error}</p>}
            <button type="button" onClick={confirmar} disabled={enviando}>
              {enviando ? 'Confirmando...' : 'Confirmar mi llegada'}
            </button>
          </>
        )}
        <button type="button" className={styles.volver} onClick={onVolver}>Volver a Manos Amigas</button>
      </section>
    </main>
  );
}
