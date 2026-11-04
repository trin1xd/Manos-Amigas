import { useState } from 'react';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import styles from '../../components/dashboard/DashboardLayout.module.css';

const NAVEGACION = [
  { id: 'inicio', nombre: 'Inicio', icono: '🏠' },
  { id: 'adultos', nombre: 'Personas a cargo', icono: '💛' },
  { id: 'solicitudes', nombre: 'Solicitudes', icono: '📋' },
  { id: 'perfil', nombre: 'Mi perfil', icono: '👤' },
];

export default function FamiliarDashboard({ usuario, onLogout }) {
  const [vista, setVista] = useState('inicio');

  return (
    <DashboardLayout
      usuario={usuario}
      onLogout={onLogout}
      tituloRol="Familiar / acompañante"
      subtitulo="Organiza y acompaña el apoyo cotidiano de tus seres queridos."
      navegacion={NAVEGACION}
      vista={vista}
      onCambiarVista={setVista}
    >
      {vista === 'inicio' && (
        <>
          <section className={styles.hero} aria-labelledby="familiar-bienvenida">
            <div>
              <p className={styles.heroEyebrow}>Cuidar también es acompañar</p>
              <h2 id="familiar-bienvenida">Más tranquilidad para tu familia</h2>
              <p>Este será tu espacio para acompañar la organización de tareas cotidianas de un adulto mayor, con permisos y privacidad.</p>
            </div>
            <span className={styles.heroIcono} aria-hidden="true">💛</span>
          </section>

          <section className={styles.panel} aria-labelledby="familiar-estado">
            <h2 id="familiar-estado">Vinculación familiar</h2>
            <div className={styles.separacion}>
              <span className={styles.estado}>◷ Función pendiente de implementación</span>
            </div>
            <p className={styles.estadoTexto}>Tu cuenta ya está activa, pero aún no se pueden consultar ni administrar los vínculos con adultos mayores desde la aplicación.</p>
          </section>

          <section className={styles.separacion} aria-labelledby="familiar-acciones">
            <h2 id="familiar-acciones" className={styles.tituloSeccion}>Tu espacio de acompañamiento</h2>
            <div className={styles.rejilla}>
              <article className={styles.tarjeta}>
                <span className={styles.tarjetaIcono} aria-hidden="true">💛</span>
                <h3>Personas a cargo</h3>
                <p>Consulta cómo se mostrarán los adultos mayores asociados a tu cuenta una vez habilitada la vinculación.</p>
                <button type="button" className={styles.tarjetaBoton} onClick={() => setVista('adultos')}>
                  Ver personas a cargo <span aria-hidden="true">→</span>
                </button>
              </article>
              <article className={styles.tarjeta}>
                <span className={styles.tarjetaIcono} aria-hidden="true">📋</span>
                <h3>Seguimiento de solicitudes</h3>
                <p>Más adelante podrás ver las solicitudes que tengas permiso de gestionar o supervisar.</p>
                <button type="button" className={styles.tarjetaBoton} onClick={() => setVista('solicitudes')}>
                  Ver solicitudes <span aria-hidden="true">→</span>
                </button>
              </article>
            </div>
          </section>

          <section className={styles.separacion} aria-labelledby="familiar-pasos">
            <h2 id="familiar-pasos" className={styles.tituloSeccion}>Cómo funcionará</h2>
            <div className={styles.pasos}>
              <div className={styles.paso}><span className={styles.pasoNumero}>1</span><strong>Vincula a tu familiar</strong><p>La asociación requerirá autorización y validación.</p></div>
              <div className={styles.paso}><span className={styles.pasoNumero}>2</span><strong>Coordina ayuda</strong><p>Solicita tareas cotidianas desde el perfil autorizado.</p></div>
              <div className={styles.paso}><span className={styles.pasoNumero}>3</span><strong>Supervisa</strong><p>Consulta el avance de las solicitudes de tu familiar.</p></div>
            </div>
          </section>
          <p className={styles.aviso}>En esta etapa no se muestran direcciones, teléfonos ni contactos de adultos mayores. Esos datos requieren permisos y endpoints protegidos.</p>
        </>
      )}

      {vista === 'adultos' && (
        <section className={`${styles.panel} ${styles.vacio}`} aria-labelledby="familiar-adultos">
          <span className={styles.vacioIcono} aria-hidden="true">💛</span>
          <h2 id="familiar-adultos">Personas a cargo</h2>
          <p>La base de datos contempla la relación entre un familiar y un adulto mayor, pero la función para consultar o crear vínculos todavía no está implementada.</p>
          <p className={styles.aviso}>No se puede afirmar desde esta pantalla si hay vínculos registrados. Primero necesitamos un endpoint que consulte tus relaciones autorizadas.</p>
        </section>
      )}

      {vista === 'solicitudes' && (
        <section className={`${styles.panel} ${styles.vacio}`} aria-labelledby="familiar-solicitudes">
          <span className={styles.vacioIcono} aria-hidden="true">📋</span>
          <h2 id="familiar-solicitudes">Seguimiento de solicitudes</h2>
          <p>Podrás seguir las solicitudes de los adultos mayores vinculados a tu cuenta cuando exista una API segura de solicitudes y relaciones familiares.</p>
          <p className={styles.aviso}>No se están consultando ni creando solicitudes reales en esta sección.</p>
        </section>
      )}

      {vista === 'perfil' && (
        <section className={styles.panel} aria-labelledby="familiar-perfil">
          <h2 id="familiar-perfil">Mi perfil de acompañante</h2>
          <p>Datos básicos recuperados desde tu sesión autenticada.</p>
          <dl className={styles.datos}>
            <div><dt>Nombre</dt><dd>{usuario?.nombre || 'No disponible'}</dd></div>
            <div><dt>Tipo de cuenta</dt><dd>Familiar</dd></div>
            <div><dt>Estado de cuenta</dt><dd>{usuario?.estado || 'No disponible'}</dd></div>
          </dl>
          <p className={styles.aviso}>El parentesco y los datos privados de los adultos mayores no están disponibles en el endpoint actual de perfil.</p>
        </section>
      )}
    </DashboardLayout>
  );
}
