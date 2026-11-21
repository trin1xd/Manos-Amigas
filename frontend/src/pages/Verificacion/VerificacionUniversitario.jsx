import { useEffect, useState } from 'react';
import { consultarVerificacion, solicitarCodigoInstitucional, confirmarCodigoInstitucional } from '../../services/verificacionInstitucionalService';
import styles from './VerificacionUniversitario.module.css';

export default function VerificacionUniversitario({ onVerificacionCompleta }) {
  const feria = import.meta.env.VITE_MODO_FERIA === 'true';
  const [datos, setDatos] = useState(null);
  const [codigo, setCodigo] = useState('');
  const [cargando, setCargando] = useState(true);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');

  async function actualizar() {
    setCargando(true);
    setError('');
    try { setDatos(await consultarVerificacion()); }
    catch (e) { setError(e.message || 'No se pudo obtener el estado del correo.'); }
    finally { setCargando(false); }
  }

  useEffect(() => {
    let activo = true;
    consultarVerificacion().then(d => { if (activo) setDatos(d); })
      .catch(e => { if (activo) setError(e.message || 'No se pudo obtener el estado del correo.'); })
      .finally(() => { if (activo) setCargando(false); });
    return () => { activo = false; };
  }, []);

  async function ejecutar(fn, exito, refrescarPerfil = false) {
    setOcupado(true);
    setError('');
    setMensaje('');
    try {
      const resultado = await fn();
      setMensaje(exito);
      setDatos(await consultarVerificacion());
      if (refrescarPerfil && resultado?.estado_verificacion === 'VERIFICADO') {
        await onVerificacionCompleta?.();
      }
    } catch (e) { setError(e.message || 'No se pudo completar la verificación.'); }
    finally { setOcupado(false); }
  }

  const pendiente = datos?.estado_verificacion === 'PENDIENTE_VERIFICACION';
  const habilitadoFeria = feria && datos?.estado_verificacion === 'VERIFICADO' && !datos?.correo_confirmado && !pendiente;
  const perfilFicticio = feria && datos?.correo_institucional?.endsWith('@demo.invalid');
  return <section className={styles.panel} aria-labelledby="correo-inst-titulo">
    <div className={styles.cabecera}>
      <div>
        <h2 id="correo-inst-titulo">{habilitadoFeria ? 'Tu perfil de prueba está habilitado' : feria ? 'Verifica tu correo para probar la aplicación' : 'Confirmación de correo institucional'}</h2>
        {!habilitadoFeria && <p>{feria ? 'Te enviaremos un código de seis dígitos al correo con el que te registraste. También puedes usar Gmail u Outlook.' : 'Demuestra que tienes acceso a tu correo universitario terminado en @correo.uss.cl.'}</p>}
      </div>
      <button type="button" onClick={actualizar} disabled={cargando || ocupado}>Actualizar</button>
    </div>
    {!habilitadoFeria && <p className={styles.aviso}>{feria ? 'En esta demostración, confirmar el código habilita las tareas inmediatamente, sin revisión del administrador. Esto solo confirma que tienes acceso al correo, no tu identidad ni tu matrícula.' : 'Confirmar este correo no valida automáticamente identidad, matrícula ni antecedentes. La revisión de la cuenta es un proceso independiente.'}</p>}
    {error && <p className={styles.error} role="alert">{error}</p>}
    {mensaje && <p className={styles.exito} role="status">{mensaje}</p>}
    {cargando && <p role="status">Consultando estado...</p>}
    {perfilFicticio && <p className={styles.exito}>¡Perfil de prueba habilitado! Puedes explorar las solicitudes y postulaciones sin confirmar ningún correo.</p>}
    {datos && !perfilFicticio && <div className={styles.datos}>
      <ul className={styles.fichas}>
        <li><strong>{feria ? 'Correo registrado:' : 'Correo institucional:'}</strong> {datos.correo_institucional}</li>
        <li><strong>Correo confirmado:</strong> {datos.correo_confirmado ? 'Sí' : 'No'}</li>
        <li><strong>Estado del perfil:</strong> {datos.estado_verificacion}</li>
      </ul>
      {!datos.dominio_admitido && !datos.correo_confirmado && <p className={styles.aviso}>{feria ? 'Esta cuenta no tiene un correo real para recibir códigos. Puedes probar las tareas directamente con el perfil ficticio.' : 'Solo se aceptan correos terminados en @correo.uss.cl. Si registraste otro, contacta a administración.'}</p>}
    </div>}
    {datos && pendiente && !datos.correo_confirmado && <div className={styles.bloque}>
      <h3>Confirmar correo</h3>
      <p>Se enviará un código de seis dígitos que caduca en 15 minutos. Máximo cinco intentos por código, cinco envíos al día y 90 segundos entre envíos.</p>
      <button type="button" disabled={ocupado || !datos.dominio_admitido}
        onClick={() => ejecutar(solicitarCodigoInstitucional, 'Código enviado. Revisa tu correo y la carpeta de spam.')}>Enviar código</button>
      <form onSubmit={e => { e.preventDefault(); ejecutar(() => confirmarCodigoInstitucional(codigo), feria ? '¡Correo confirmado! Tu cuenta ya puede postular a las tareas de la feria.' : 'Correo institucional confirmado.', true); }}>
        <label htmlFor="verificacion-codigo">Código de seis dígitos</label>
        <input id="verificacion-codigo" value={codigo} onChange={e => setCodigo(e.target.value.replace(/\D/g, '').slice(0, 6))}
          maxLength={6} inputMode="numeric" pattern="[0-9]{6}" required autoComplete="one-time-code" />
        <button type="submit" disabled={ocupado || codigo.length !== 6}>Confirmar código</button>
      </form>
    </div>}
    {datos?.correo_confirmado && !perfilFicticio && <p className={styles.exito}>{feria ? '¡Correo confirmado! Tu perfil quedó habilitado para probar la aplicación.' : 'El correo institucional fue confirmado. Tu cuenta no se aprueba automáticamente.'}</p>}
    {datos && !perfilFicticio && !pendiente && !datos.correo_confirmado && <p className={styles.aviso}>{feria && datos.estado_verificacion === 'VERIFICADO' ? 'Demo de feria: tu perfil ya está habilitado y no necesitas confirmar ningún correo. Confirmar un correo no valida identidad ni matrícula.' : 'Tu perfil ya tiene una decisión anterior. Los códigos están disponibles para cuentas pendientes.'}</p>}
  </section>;
}
