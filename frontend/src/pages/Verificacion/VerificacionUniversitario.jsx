import { useEffect, useState } from 'react';
import { consultarVerificacion, solicitarCodigoInstitucional, confirmarCodigoInstitucional } from '../../services/verificacionInstitucionalService';
import styles from './VerificacionUniversitario.module.css';

export default function VerificacionUniversitario() {
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

  async function ejecutar(fn, exito) {
    setOcupado(true);
    setError('');
    setMensaje('');
    try {
      await fn();
      setMensaje(exito);
      setDatos(await consultarVerificacion());
    } catch (e) { setError(e.message || 'No se pudo completar la verificación.'); }
    finally { setOcupado(false); }
  }

  const pendiente = datos?.estado_verificacion === 'PENDIENTE_VERIFICACION';
  return <section className={styles.panel} aria-labelledby="correo-inst-titulo">
    <div className={styles.cabecera}>
      <div>
        <h2 id="correo-inst-titulo">Confirmación de correo institucional</h2>
        <p>Demuestra que tienes acceso a tu correo universitario terminado en @correo.uss.cl.</p>
      </div>
      <button type="button" onClick={actualizar} disabled={cargando || ocupado}>Actualizar</button>
    </div>
    <p className={styles.aviso}>Confirmar este correo <strong>no valida automáticamente identidad, matrícula ni antecedentes</strong>. La revisión de la cuenta es un proceso independiente.</p>
    {error && <p className={styles.error} role="alert">{error}</p>}
    {mensaje && <p className={styles.exito} role="status">{mensaje}</p>}
    {cargando && <p role="status">Consultando estado...</p>}
    {datos && <div className={styles.datos}>
      <p><strong>Correo institucional:</strong> {datos.correo_institucional}</p>
      <p><strong>Correo confirmado:</strong> {datos.correo_confirmado ? 'Sí' : 'No'}</p>
      <p><strong>Estado del perfil:</strong> {datos.estado_verificacion}</p>
      {!datos.dominio_admitido && !datos.correo_confirmado && <p className={styles.aviso}>Solo se aceptan correos terminados en @correo.uss.cl. Si registraste otro, contacta a administración.</p>}
    </div>}
    {datos && pendiente && !datos.correo_confirmado && <div className={styles.bloque}>
      <h3>Confirmar correo</h3>
      <p>Se enviará un código de seis dígitos que caduca en 15 minutos. Máximo cinco intentos por código, cinco envíos al día y 90 segundos entre envíos.</p>
      <button type="button" disabled={ocupado || !datos.dominio_admitido}
        onClick={() => ejecutar(solicitarCodigoInstitucional, 'Código enviado. Revisa tu correo universitario.')}>Enviar código</button>
      <form onSubmit={e => { e.preventDefault(); ejecutar(() => confirmarCodigoInstitucional(codigo), 'Correo institucional confirmado.'); }}>
        <label htmlFor="verificacion-codigo">Código de seis dígitos</label>
        <input id="verificacion-codigo" value={codigo} onChange={e => setCodigo(e.target.value.replace(/\D/g, '').slice(0, 6))}
          maxLength={6} inputMode="numeric" pattern="[0-9]{6}" required autoComplete="one-time-code" />
        <button type="submit" disabled={ocupado || codigo.length !== 6}>Confirmar código</button>
      </form>
    </div>}
    {datos?.correo_confirmado && <p className={styles.exito}>El correo institucional fue confirmado. Tu cuenta no se aprueba automáticamente.</p>}
    {datos && !pendiente && !datos.correo_confirmado && <p className={styles.aviso}>Tu perfil ya tiene una decisión administrativa de pruebas. Este flujo de correo solo está disponible para cuentas pendientes.</p>}
  </section>;
}
