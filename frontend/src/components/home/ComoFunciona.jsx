import styles from './ComoFunciona.module.css';

const steps = [
  {
    id: 1,
    title: 'Solicita el apoyo que necesitas',
    description:
      'Indica la tarea o acompañamiento que requiere tu familiar (compras, trámites o compañía).',
  },
  {
    id: 2,
    title: 'Encuentra un estudiante verificado',
    description:
      'Revisa perfiles validados por la plataforma con información clara antes de coordinar.',
  },
  {
    id: 3,
    title: 'Coordina y recibe el apoyo',
    description:
      'Acuerda el horario y recibe el apoyo con puntualidad, seguridad y calidez.',
  },
];

export default function ComoFunciona() {
  return (
    <section
      id="como-funciona"
      className={`section ${styles.section}`}
      aria-labelledby="como-funciona-heading"
    >
      <div className="container">
        {/* Section header */}
        <div className={`text-center ${styles.sectionHeader}`}>
          <span className={styles.eyebrow}>Paso a paso</span>
          <h2 id="como-funciona-heading" className={styles.sectionTitle}>
            ¿Cómo funciona?
          </h2>
          <p className={styles.sectionSubtitle}>
            En tres pasos sencillos tu familiar recibe el apoyo que necesita.
          </p>
        </div>

        {/* 3 compact vertical steps in mobile */}
        <ol className={styles.stepsGrid} aria-label="Pasos del proceso">
          {steps.map((step) => (
            <li key={step.id} className={styles.stepCard}>
              <div className={styles.stepNumber} aria-label={`Paso ${step.id}`}>
                {step.id}
              </div>
              <div className={styles.stepBody}>
                <span className={styles.stepLabel}>Paso {step.id}</span>
                <h3 className={styles.stepTitle}>{step.title}</h3>
                <p className={styles.stepDesc}>{step.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
