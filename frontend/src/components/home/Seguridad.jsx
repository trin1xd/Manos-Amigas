import styles from './Seguridad.module.css';

const garantias = [
  {
    id: 'identidad-verificada',
    icon: '🪪',
    title: 'Estudiantes con identidad verificada',
    description:
      'Validamos la identidad oficial y la condición de estudiante universitario antes del ingreso a la plataforma.',
  },
  {
    id: 'revision-antecedentes',
    icon: '🛡️',
    title: 'Verificación de identidad y antecedentes antes de habilitar el perfil',
    description:
      'Revisión exhaustiva y obligatoria para asegurar que cada apoyo sea brindado con total tranquilidad.',
  },
  {
    id: 'informacion-previa',
    icon: '📋',
    title: 'Información del estudiante antes de aceptar un servicio',
    description:
      'Conoce los datos, carrera y detalles del estudiante antes de confirmar cualquier acompañamiento.',
  },
];

export default function Seguridad() {
  return (
    <section
      id="seguridad"
      className={`section ${styles.section}`}
      aria-labelledby="seguridad-heading"
    >
      <div className="container">
        {/* Header */}
        <div className={`text-center ${styles.sectionHeader}`}>
          <span className={styles.eyebrow}>Seguridad</span>
          <h2 id="seguridad-heading" className={styles.sectionTitle}>
            Tu tranquilidad es nuestra prioridad
          </h2>
          <p className={styles.sectionSubtitle}>
            Un proceso de validación responsable para que tu familiar esté en buenas manos.
          </p>
        </div>

        {/* Compact Security Cards */}
        <div className={styles.securityContainer}>
          <ul className={styles.securityList} aria-label="Garantías de seguridad">
            {garantias.map((item) => (
              <li
                key={item.id}
                id={`garantia-${item.id}`}
                className={styles.securityCard}
              >
                <div className={styles.securityIcon} aria-hidden="true">
                  {item.icon}
                </div>
                <div className={styles.securityContent}>
                  <h3 className={styles.securityTitle}>{item.title}</h3>
                  <p className={styles.securityDesc}>{item.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
