import { useEffect, useState } from 'react';
import styles from './AccessibilityToolbar.module.css';

const read = key => {
  try { return localStorage.getItem(key) === 'true'; } catch { return false; }
};

export default function AccessibilityToolbar() {
  const [abierto, setAbierto] = useState(false);
  const [textoGrande, setTextoGrande] = useState(() => read('manos_amigas_texto_grande'));
  const [altoContraste, setAltoContraste] = useState(() => read('manos_amigas_alto_contraste'));
  const [reducirMovimiento, setReducirMovimiento] = useState(() => read('manos_amigas_reducir_movimiento'));

  useEffect(() => {
    const handler = event => setTextoGrande(Boolean(event.detail));
    window.addEventListener('manos-amigas:texto-grande', handler);
    return () => window.removeEventListener('manos-amigas:texto-grande', handler);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('texto-grande', textoGrande);
    try { localStorage.setItem('manos_amigas_texto_grande', String(textoGrande)); } catch { /* Navegación privada */ }
  }, [textoGrande]);

  useEffect(() => {
    document.documentElement.classList.toggle('alto-contraste', altoContraste);
    try { localStorage.setItem('manos_amigas_alto_contraste', String(altoContraste)); } catch { /* Navegación privada */ }
  }, [altoContraste]);

  useEffect(() => {
    document.documentElement.classList.toggle('reducir-movimiento', reducirMovimiento);
    try { localStorage.setItem('manos_amigas_reducir_movimiento', String(reducirMovimiento)); } catch { /* Navegación privada */ }
  }, [reducirMovimiento]);

  function alternarTexto() {
    setTextoGrande(anterior => {
      const nuevo = !anterior;
      window.dispatchEvent(new CustomEvent('manos-amigas:texto-grande', { detail: nuevo }));
      return nuevo;
    });
  }

  return <aside className={styles.flotante} aria-label="Opciones de accesibilidad">
    <button type="button" className={styles.activador} aria-expanded={abierto}
      aria-controls="manos-accesibilidad-opciones" onClick={() => setAbierto(v => !v)}>
      <span aria-hidden="true">Aa</span> Accesibilidad
    </button>
    {abierto && <div className={styles.panel} id="manos-accesibilidad-opciones">
      <strong>Preferencias de lectura</strong>
      <button type="button" aria-pressed={textoGrande} onClick={alternarTexto}>
        {textoGrande ? '✓ ' : ''}Texto más grande
      </button>
      <button type="button" aria-pressed={altoContraste} onClick={() => setAltoContraste(v => !v)}>
        {altoContraste ? '✓ ' : ''}Mayor contraste
      </button>
      <button type="button" aria-pressed={reducirMovimiento} onClick={() => setReducirMovimiento(v => !v)}>
        {reducirMovimiento ? '✓ ' : ''}Reducir animaciones
      </button>
      <p>Estas preferencias se mantienen al cambiar de perfil y al recargar.</p>
    </div>}
  </aside>;
}
