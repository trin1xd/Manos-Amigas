import { useState } from 'react';
import { solicitarRecuperacion, confirmarRecuperacion } from '../../services/recuperacionService';
import styles from './RecuperarContrasena.module.css';

export default function RecuperarContrasena({ token, onVolver }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [repetir, setRepetir] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [error, setError] = useState('');
  const [completado, setCompletado] = useState(false);

  async function enviar(evento) {
    evento.preventDefault();
    setEnviando(true); setError(''); setMensaje('');
    try {
      if (token) {
        if (password !== repetir) throw new Error('Las contraseñas no coinciden.');
        const resultado = await confirmarRecuperacion(token, password);
        setMensaje(resultado.message);
        setCompletado(true);
        setPassword(''); setRepetir('');
      } else {
        const resultado = await solicitarRecuperacion(email.trim());
        setMensaje(resultado.message);
      }
    } catch (err) { setError(err.message || 'No se pudo completar la solicitud.'); }
    finally { setEnviando(false); }
  }

  return <main className={styles.pagina}>
    <section className={styles.tarjeta} aria-labelledby="recuperacion-titulo">
      <h1 id="recuperacion-titulo">{token ? 'Crear una nueva contraseña' : 'Recuperar contraseña'}</h1>
      <p>{token ? 'Introduce tu nueva contraseña. El enlace solo puede utilizarse una vez.' :
        'Si tienes una cuenta, te enviaremos un enlace de recuperación a tu correo registrado.'}</p>
      {mensaje && <p className={styles.exito} role="status">{mensaje}</p>}
      {error && <p className={styles.error} role="alert">{error}</p>}
      {!completado && <form onSubmit={enviar} className={styles.formulario}>
        {!token ? <>
          <label htmlFor="rec-email">Correo electrónico</label>
          <input id="rec-email" type="email" autoComplete="email" required maxLength="255"
            value={email} onChange={e => setEmail(e.target.value)} />
        </> : <>
          <label htmlFor="rec-password">Nueva contraseña (mínimo 8 caracteres)</label>
          <input id="rec-password" type="password" autoComplete="new-password" minLength="8" maxLength="128" required
            value={password} onChange={e => setPassword(e.target.value)} />
          <label htmlFor="rec-repetir">Repetir nueva contraseña</label>
          <input id="rec-repetir" type="password" autoComplete="new-password" minLength="8" required
            value={repetir} onChange={e => setRepetir(e.target.value)} />
        </>}
        <button type="submit" disabled={enviando}>
          {enviando ? 'Procesando...' : token ? 'Guardar contraseña' : 'Enviar instrucciones'}
        </button>
      </form>}
      <button type="button" className={styles.volver} onClick={onVolver}>Volver a iniciar sesión</button>
      <small>Los enlaces vencen en 20 minutos. Si el correo no llega, revisa spam o consulta la configuración SMTP.</small>
    </section>
  </main>;
}
