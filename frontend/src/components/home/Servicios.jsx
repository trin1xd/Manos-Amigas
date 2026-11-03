import styles from './Servicios.module.css';

const services = [
  {
    id: 'compras',
    emoji: '🛒',
    title: 'Compras',
    description: 'Supermercado, farmacia y tiendas locales.',
  },
  {
    id: 'tramites',
    emoji: '📋',
    title: 'Trámites',
    description: 'Gestiones bancarias, médicas y notariales.',
  },
  {
    id: 'tareas-del-hogar',
    emoji: '🏠',
    title: 'Tareas del hogar',
    description: 'Organización, cocina y tareas cotidianas.',
  },
  {
    id: 'tecnologia',
    emoji: '📱',
    title: 'Apoyo digital',
    description: 'Uso de celular, videollamadas y apps.',
  },
  {
    id: 'transporte',
    emoji: '🚗',
    title: 'Acompañamiento',
    description: 'Traslados a citas médicas o diligencias.',
  },
  {
    id: 'compania',
    emoji: '💬',
    title: 'Compañía',
    description: 'Visitas amigables, paseos y conversación.',
  },
];

export default function Servicios() {
  return (
    <section
      id="servicios"
      className={`section section-alt ${styles.section}`}
      aria-labelledby="servicios-heading"
    >
      <div className="container">
        {/* Header */}
        <div className={`text-center ${styles.sectionHeader}`}>
          <span className={styles.eyebrow}>Servicios</span>
          <h2 id="servicios-heading" className={styles.sectionTitle}>
            ¿En qué podemos ayudarte?
          </h2>
          <p className={styles.sectionSubtitle}>
            Asistencia cercana y confiable adaptada a cada necesidad.
          </p>
        </div>

        {/* 2-column mobile app grid */}
        <div className={styles.servicesGrid} role="list" aria-label="Servicios disponibles">
          {services.map((service) => (
            <article
              key={service.id}
              id={`service-${service.id}`}
              className={styles.serviceCard}
              role="listitem"
            >
              <div className={styles.emojiWrap} aria-hidden="true">
                <span className={styles.emoji}>{service.emoji}</span>
              </div>
              <div className={styles.cardContent}>
                <h3 className={styles.cardTitle}>{service.title}</h3>
                <p className={styles.cardDesc}>{service.description}</p>
              </div>
            </article>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className={`text-center ${styles.bottomCta}`}>
          <p className={styles.bottomCtaText}>
            ¿Tienes otra necesidad?{' '}
            <span className={styles.bottomCtaLink}>Cuéntanos y lo coordinamos</span>
          </p>
        </div>
      </div>
    </section>
  );
}
