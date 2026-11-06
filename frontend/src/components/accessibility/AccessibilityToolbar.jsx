/* MANOS AMIGAS UI V6 - ACCESIBILIDAD INTEGRADA */
/* MANOS AMIGAS UI V5 | PORTADA Y ACENTOS */
import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import UiIcon from '../ui/UiIcon';
import styles from './AccessibilityToolbar.module.css';

const read = key => {
  try { return localStorage.getItem(key) === 'true'; } catch { return false; }
};

/** Un solo control de accesibilidad para toda la aplicación.
 * Se ubica en el panel cuando está disponible; en las pantallas públicas
 * permanece dentro del flujo normal de la página, nunca sobre el contenido. */
export default function AccessibilityToolbar({ integrada = false }) {
  const [destino, setDestino] = useState(null);
  const [abierto, setAbierto] = useState(false);
  const [textoGrande, setTextoGrande] = useState(() => read('manos_amigas_texto_grande'));
  const [altoContraste, setAltoContraste] = useState(() => read('manos_amigas_alto_contraste'));
  const [reducirMovimiento, setReducirMovimiento] = useState(() => read('manos_amigas_reducir_movimiento'));
  const [modoOscuro, setModoOscuro] = useState(() => read('manos_amigas_modo_oscuro'));

  useEffect(() => {
    if (integrada) return undefined;
    const raiz = document.getElementById('root');
    const actualizar = () => {
      const nodo = document.getElementById('manos-accesibilidad-slot') || document.getElementById('manos-accesibilidad-home') || document.getElementById('manos-accesibilidad-fallback');
      setDestino(anterior => anterior === nodo ? anterior : nodo);
    };
    actualizar();
    if (!raiz) return undefined;
    const observador = new MutationObserver(actualizar);
    observador.observe(raiz, { childList: true, subtree: true });
    // Reubicar la barra si el navegador cambia entre móvil y escritorio.
    window.addEventListener('resize', actualizar);
    window.addEventListener('pageshow', actualizar);
    return () => {
      observador.disconnect();
      window.removeEventListener('resize', actualizar);
      window.removeEventListener('pageshow', actualizar);
    };
  }, [integrada]);

  useEffect(() => {
    const handler = event => setTextoGrande(Boolean(event.detail));
    window.addEventListener('manos-amigas:texto-grande', handler);
    return () => window.removeEventListener('manos-amigas:texto-grande', handler);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('texto-grande', textoGrande);
    try { localStorage.setItem('manos_amigas_texto_grande', String(textoGrande)); } catch { /* Almacenamiento deshabilitado */ }
  }, [textoGrande]);

  useEffect(() => {
    document.documentElement.classList.toggle('alto-contraste', altoContraste);
    try { localStorage.setItem('manos_amigas_alto_contraste', String(altoContraste)); } catch { /* Almacenamiento deshabilitado */ }
  }, [altoContraste]);

  useEffect(() => {
    document.documentElement.classList.toggle('reducir-movimiento', reducirMovimiento);
    try { localStorage.setItem('manos_amigas_reducir_movimiento', String(reducirMovimiento)); } catch { /* Almacenamiento deshabilitado */ }
  }, [reducirMovimiento]);

  useEffect(() => {
    document.documentElement.classList.toggle('modo-oscuro', modoOscuro);
    try { localStorage.setItem('manos_amigas_modo_oscuro', String(modoOscuro)); } catch { /* Almacenamiento deshabilitado */ }
  }, [modoOscuro]);

  function alternarTexto() {
    setTextoGrande(anterior => {
      const nuevo = !anterior;
      window.dispatchEvent(new CustomEvent('manos-amigas:texto-grande', { detail: nuevo }));
      return nuevo;
    });
  }

  const esPortada = integrada || destino?.id === 'manos-accesibilidad-home';
  if (!integrada && !destino) return null;
  const contenido = (
    <aside className={`${styles.contenedor} ${esPortada ? styles.portada : ''}`} aria-label="Opciones de accesibilidad">
      <button
        type="button"
        className={styles.activador}
        aria-expanded={abierto}
        aria-controls="manos-accesibilidad-opciones"
        onClick={() => setAbierto(anterior => !anterior)}
      >
        <UiIcon name="accessibility" size={19} />
        <span>Accesibilidad</span>
        <UiIcon name="chevron-down" size={16} />
      </button>
      {abierto && <div className={styles.panel} id="manos-accesibilidad-opciones">
        <strong>Preferencias de visualización</strong>
        <button type="button" aria-pressed={modoOscuro} onClick={() => setModoOscuro(v => !v)}>
          <UiIcon name={modoOscuro ? 'sun' : 'moon'} size={19} />
          {modoOscuro ? 'Usar modo claro' : 'Activar modo oscuro'}
        </button>
        <button type="button" aria-pressed={textoGrande} onClick={alternarTexto}>
          <span className={styles.simbolo} aria-hidden="true">A+</span> Texto más grande
        </button>
        <button type="button" aria-pressed={altoContraste} onClick={() => setAltoContraste(v => !v)}>
          <span className={styles.simbolo} aria-hidden="true">◐</span> Mayor contraste
        </button>
        <button type="button" aria-pressed={reducirMovimiento} onClick={() => setReducirMovimiento(v => !v)}>
          <span className={styles.simbolo} aria-hidden="true">−</span> Reducir animaciones
        </button>
        <p>Las preferencias se guardan en este navegador.</p>
      </div>}
    </aside>
  );
  return integrada ? contenido : createPortal(contenido, destino);
}
