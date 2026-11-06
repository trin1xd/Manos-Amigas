import { useState } from 'react';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import styles from '../../components/dashboard/DashboardLayout.module.css';
import TareasDisponibles from './TareasDisponibles';
import MisPostulaciones from './MisPostulaciones';
import SeguimientoServicios from '../Seguimiento/SeguimientoServicios';
import CalificacionesServicios from '../Calificaciones/CalificacionesServicios';
import ChatServicios from '../Chat/ChatServicios';

const NAVEGACION = [
  { id: 'inicio', nombre: 'Inicio', icono: '🏠' },
  { id: 'oportunidades', nombre: 'Tareas', icono: '🧹' },
  { id: 'postulaciones', nombre: 'Mis postulaciones', icono: '📋' },
  { id: 'seguimiento', nombre: 'Seguimiento', icono: '🕒' },
  { id: 'calificaciones', nombre: 'Calificaciones', icono: '⭐' },
  { id: 'chat', nombre: 'Chat', icono: '💬' },
  { id: 'perfil', nombre: 'Mi perfil', icono: '👤' },
];

const ESTADOS = {
  PENDIENTE_VERIFICACION: {
    etiqueta: 'Pendiente de verificación',
    descripcion: 'Tu registro está creado. Todavía no puedes aceptar tareas hasta completar la verificación.',
    estilo: '',
  },
  VERIFICADO: {
    etiqueta: 'Perfil verificado',
    descripcion: 'Tu perfil figura como verificado. Ya puedes revisar las tareas disponibles y postular.',
    estilo: styles.estadoOk,
  },
  RECHAZADO: {
    etiqueta: 'Verificación rechazada',
    descripcion: 'Tu verificación figura como rechazada. La opción de presentar nuevos antecedentes todavía está en desarrollo.',
    estilo: styles.estadoAlerta,
  },
  SUSPENDIDO: {
    etiqueta: 'Verificación suspendida',
    descripcion: 'Tu verificación figura como suspendida. No podrás ofrecer ayuda mientras mantenga ese estado.',
    estilo: styles.estadoAlerta,
  },
};

export default function UniversitarioDashboard({ usuario, onLogout }) {
  const [vista, setVista] = useState('inicio');
  const estado = ESTADOS[usuario?.estado_verificacion] || {
    etiqueta: 'Verificación sin información',
    descripcion: 'No pudimos determinar el estado de verificación de tu perfil. No se habilitan tareas.',
    estilo: styles.estadoAlerta,
  };

  return (
    <DashboardLayout
      usuario={usuario}
      onLogout={onLogout}
      tituloRol="Universitario"
      subtitulo="Tu espacio para ayudar a otras personas de forma responsable."
      navegacion={NAVEGACION}
      vista={vista}
      onCambiarVista={setVista}
    >
      {vista === 'inicio' && (
        <>
          <section className={styles.hero} aria-labelledby="titulo-universitario">
            <div>
              <p className={styles.heroEyebrow}>Tu comunidad cuenta contigo</p>
              <h2 id="titulo-universitario">Conecta tu tiempo con una buena causa</h2>
              <p>Consulta tu estado de verificación y prepárate para ayudar en tareas cotidianas no médicas.</p>
            </div>
            <span className={styles.heroIcono} aria-hidden="true">🎓</span>
          </section>

          <section className={styles.panel} aria-labelledby="titulo-verificacion">
            <h2 id="titulo-verificacion">Estado de tu cuenta</h2>
            <div className={styles.separacion}>
              <span className={`${styles.estado} ${estado.estilo}`}>● {estado.etiqueta}</span>
            </div>
            <p className={styles.estadoTexto}>{estado.descripcion}</p>
          </section>

          <section className={styles.separacion} aria-labelledby="titulo-acciones-universitario">
            <h2 id="titulo-acciones-universitario" className={styles.tituloSeccion}>¿Qué quieres revisar?</h2>
            <div className={styles.rejilla}>
              <article className={styles.tarjeta}>
                <span className={styles.tarjetaIcono} aria-hidden="true">🧹</span>
                <h3>Explorar tareas</h3>
                <p>Revisa las solicitudes abiertas de adultos mayores y postula cuando tu perfil esté verificado.</p>
                <button type="button" className={styles.tarjetaBoton} onClick={() => setVista('oportunidades')}>
                  Ver sección de tareas <span aria-hidden="true">→</span>
                </button>
              </article>
              <article className={styles.tarjeta}>
                <span className={styles.tarjetaIcono} aria-hidden="true">📋</span>
                <h3>Mis postulaciones</h3>
                <p>Sigue el estado de tus postulaciones: pendientes, aceptadas o rechazadas.</p>
                <button type="button" className={styles.tarjetaBoton} onClick={() => setVista('postulaciones')}>
                  Ver mis postulaciones <span aria-hidden="true">→</span>
                </button>
              </article>
            </div>
          </section>

          <section className={styles.separacion} aria-labelledby="titulo-pasos-uni">
            <h2 id="titulo-pasos-uni" className={styles.tituloSeccion}>Cómo funcionará</h2>
            <div className={styles.pasos}>
              <div className={styles.paso}><span className={styles.pasoNumero}>1</span><strong>Crea tu cuenta</strong><p>Regístrate con tus datos universitarios.</p></div>
              <div className={styles.paso}><span className={styles.pasoNumero}>2</span><strong>Verifica tu perfil</strong><p>La validación deberá completarse antes de ofrecer servicios.</p></div>
              <div className={styles.paso}><span className={styles.pasoNumero}>3</span><strong>Ayuda con una tarea</strong><p>Solo cuando las tareas y postulaciones estén habilitadas.</p></div>
            </div>
          </section>
          <p className={styles.aviso}>Manos Amigas no presta servicios médicos, no asigna tareas automáticamente en esta versión y no realiza pagos desde este panel.</p>
        </>
      )}

      {vista === 'oportunidades' && (
        <TareasDisponibles usuario={usuario} onLogout={onLogout} />
      )}

      {vista === 'postulaciones' && (
        <MisPostulaciones onLogout={onLogout} />
      )}

      {vista === 'seguimiento' && (
        <SeguimientoServicios usuario={usuario} />
      )}
      {vista === 'calificaciones' && (
        <CalificacionesServicios usuario={usuario} />
      )}
      {vista === 'chat' && (
        <ChatServicios usuario={usuario} />
      )}
      {vista === 'perfil' && (
        <section className={styles.panel} aria-labelledby="uni-perfil">
          <h2 id="uni-perfil">Mi perfil universitario</h2>
          <p>Datos básicos recuperados desde tu sesión autenticada.</p>
          <dl className={styles.datos}>
            <div><dt>Nombre</dt><dd>{usuario?.nombre || 'No disponible'}</dd></div>
            <div><dt>Tipo de cuenta</dt><dd>Universitario</dd></div>
            <div><dt>Estado de cuenta</dt><dd>{usuario?.estado || 'No disponible'}</dd></div>
            <div><dt>Verificación</dt><dd>{estado.etiqueta}</dd></div>
          </dl>
          <p className={styles.aviso}>La universidad, carrera y los documentos de verificación no están disponibles en el endpoint de perfil actual; no se inventan esos datos.</p>
        </section>
      )}
    </DashboardLayout>
  );
}
