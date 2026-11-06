/* MANOS AMIGAS UI V6 - ACCESIBILIDAD INTEGRADA */
import { StrictMode, useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './modo-oscuro.css'
import App from './App.jsx'
import AccessibilityToolbar from './components/accessibility/AccessibilityToolbar'

// El botón vive DENTRO del Hero en Inicio. En el resto de las vistas,
// la misma barra se ubica en el panel o en un alojamiento al final de la página.
function AccesibilidadFueraDePortada() {
  const [mostrar, setMostrar] = useState(false);
  useEffect(() => {
    const raiz = document.getElementById('root');
    const actualizar = () => setMostrar(!document.getElementById('manos-accesibilidad-home'));
    actualizar();
    if (!raiz) return undefined;
    const observador = new MutationObserver(actualizar);
    observador.observe(raiz, { childList: true, subtree: true });
    return () => observador.disconnect();
  }, []);
  return mostrar ? <AccessibilityToolbar /> : null;
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
    <div id="manos-accesibilidad-fallback" />
    <AccesibilidadFueraDePortada />
  </StrictMode>,
)
