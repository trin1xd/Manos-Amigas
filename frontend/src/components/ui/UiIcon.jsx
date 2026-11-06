/** Iconografía SVG coherente para Manos Amigas. Sin dependencias externas. */
const TRAZOS = {
  inicio: <><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/></>,
  oportunidades: <><path d="M4 21h16"/><path d="m7 17 9-13 3 3-9 13"/><path d="m14 6 4 4"/></>,
  catalogo: <><path d="M4 21h16"/><path d="m7 17 9-13 3 3-9 13"/><path d="m14 6 4 4"/></>,
  'pedir-ayuda': <><path d="M4 12h4l3 4 2-3h7"/><path d="M4 17c2 2 4 4 8 4s6-2 8-4"/><path d="M12 2v6m-3-3h6"/></>,
  postulaciones: <><rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V2h6v2M9 10h6M9 14h6M9 18h3"/></>,
  solicitudes: <><rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V2h6v2M9 10h6M9 14h6M9 18h3"/></>,
  seguimiento: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  calificaciones: <><path d="m12 2 3 6.4 7 .9-5.1 5 .9 7-5.8-3.1-5.8 3.1.9-7-5.1-5 7-.9z"/></>,
  chat: <><path d="M20 11.5a8.5 8.5 0 0 1-8.5 8.5c-1.5 0-3-.4-4.3-1.1L3 20l1.1-4.1A8.5 8.5 0 1 1 20 11.5Z"/><path d="M8 11h8"/></>,
  avisos: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></>,
  disponibilidad: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6M17 2v6M3 10h18m-12 6 2 2 4-4"/></>,
  agenda: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6M17 2v6M3 10h18M8 15h3M14 15h2"/></>,
  verificacion: <><path d="m12 2 8 4v6c0 5-3.4 8.4-8 10-4.6-1.6-8-5-8-10V6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/></>,
  perfil: <><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/></>,
  adultos: <><circle cx="9" cy="8" r="3"/><path d="M3 21v-2c0-3 2.5-5 6-5s6 2 6 5v2M17 5a3 3 0 0 1 0 6M17 14c2.5 0 4 2 4 5v2"/></>,
  nueva: <><path d="M12 5v14M5 12h14"/><circle cx="12" cy="12" r="10"/></>,
  'graduation-cap': <><path d="m2 9 10-5 10 5-10 5z"/><path d="M6 11v5c4 3 8 3 12 0v-5M22 9v7"/></>,
  heart: <path d="M20.8 8.6c0 4.2-8.8 10-8.8 10s-8.8-5.8-8.8-10a4.8 4.8 0 0 1 8.8-2.4 4.8 4.8 0 0 1 8.8 2.4Z"/>,
  'hand-heart': <><path d="M3 16h4l3 3h5l6-5a2 2 0 0 0-3-3l-4 3"/><path d="M3 12h4l3 2h4"/><path d="M12 3c2-3 6 0 4 3l-4 4-4-4c-2-3 2-6 4-3Z"/></>,
  'shopping-bag': <><rect x="4" y="8" width="16" height="13" rx="2"/><path d="M8 9V6a4 4 0 0 1 8 0v3"/></>,
  'book-open': <><path d="M12 6c-3-2-6-2-9-1v14c3-1 6-1 9 1 3-2 6-2 9-1V5c-3-1-6-1-9 1ZM12 6v14"/></>,
  leaf: <><path d="M20 4C9 3 3 8 4 16c4 4 12 2 16-12Z"/><path d="M4 21c2-6 6-10 12-13"/></>,
  wrench: <><path d="M21 6a6 6 0 0 1-8 7l-7 7a2 2 0 1 1-3-3l7-7a6 6 0 0 1 7-8l-4 4 4 4z"/></>,
  'paw-print': <><circle cx="7" cy="7" r="1.5"/><circle cx="12" cy="5" r="1.5"/><circle cx="17" cy="7" r="1.5"/><path d="M12 12c-3 0-7 4-7 6 0 3 3 3 7 1 4 2 7 2 7-1 0-2-4-6-7-6Z"/></>,
  smartphone: <><rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4"/></>,
  'utensils': <><path d="M4 2v8c0 3 5 3 5 0V2M6.5 2v20M17 22V2c-4 2-4 9-4 12h4"/></>,
  'file-text': <><path d="M7 2h7l5 5v15H5V2zM14 2v6h5M9 13h6M9 17h6"/></>,
  accessibility: <><circle cx="12" cy="4" r="2"/><path d="M4 9h16M12 9v12m-5-6-3 6m13-6 3 6"/></>,
  moon: <path d="M20.3 15A8.7 8.7 0 0 1 9 3.7 8.7 8.7 0 1 0 20.3 15Z"/>,
  sun: <><circle cx="12" cy="12" r="4"/><path d="M12 1v2m0 18v2M1 12h2m18 0h2M4 4l2 2m12 12 2 2M20 4l-2 2M6 18l-2 2"/></>,
  'chevron-down': <path d="m6 9 6 6 6-6"/>,
  menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
  arrow: <path d="M5 12h14m-6-6 6 6-6 6"/>,
  circle: <circle cx="12" cy="12" r="8"/>,
};

export default function UiIcon({ name = 'circle', size = 22, className }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      className={className}
      style={{ flexShrink: 0, verticalAlign: 'middle' }}
    >
      {TRAZOS[name] || TRAZOS.circle}
    </svg>
  );
}
