import styles from './CreateAccount.module.css';

function HeartIcon() {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
                d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67
        l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23
        l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z"
                fill="currentColor"
            />
        </svg>
    );
}

function StudyIcon() {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
                d="M2.5 9.5 12 4l9.5 5.5L12 15 2.5 9.5Z"
                fill="currentColor"
            />
            <path
                d="M6.5 12.1V16c0 1.9 2.5 3.5 5.5 3.5
        s5.5-1.6 5.5-3.5v-3.9L12 15.3l-5.5-3.2Z"
                fill="currentColor"
            />
        </svg>
    );
}

function FamilyIcon() {
    return (
        <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="8" cy="8" r="3" fill="currentColor" />
            <circle cx="16.5" cy="9" r="2.5" fill="currentColor" />
            <path
                d="M2.8 19c.3-3.7 2.2-5.6 5.2-5.6s4.9 1.9 5.2 5.6H2.8Z"
                fill="currentColor"
            />
            <path
                d="M12.8 19c.2-2.9 1.7-4.5 4.1-4.5
        2.5 0 4 1.6 4.3 4.5h-8.4Z"
                fill="currentColor"
            />
        </svg>
    );
}

export default function CreateAccount({
    onNavigateHome,
}) {
    return (
        <div className={styles.page}>

            <header className={styles.topBar}>
                <button
                    type="button"
                    className={styles.backButton}
                    onClick={onNavigateHome}
                    aria-label="Volver al inicio"
                >
                    ←
                </button>

                <h1 className={styles.topBarTitle}>
                    Crear cuenta
                </h1>

                <div className={styles.spacer} />
            </header>

            <main className={styles.content}>

                <h2 className={styles.heading}>
                    ¿Cómo quieres usar la app?
                </h2>

                <p className={styles.helperText}>
                    Selecciona el perfil que mejor representa cómo usarás Manos Amigas.
                </p>

                <div className={styles.cards}>

                    <button
                        type="button"
                        className={`${styles.card} ${styles.adultCard}`}
                    >
                        <span
                            className={`${styles.icon} ${styles.adultIcon}`}
                        >
                            <HeartIcon />
                        </span>

                        <span className={styles.cardText}>
                            <strong>Soy adulto mayor</strong>
                            <span>
                                Necesito ayuda en mi hogar
                            </span>
                        </span>

                        <span className={styles.chevron}>
                            ›
                        </span>
                    </button>

                    <button
                        type="button"
                        className={`${styles.card} ${styles.studentCard}`}
                    >
                        <span
                            className={`${styles.icon} ${styles.studentIcon}`}
                        >
                            <StudyIcon />
                        </span>

                        <span className={styles.cardText}>
                            <strong>Soy universitario</strong>
                            <span>
                                Quiero ayudar y ganar dinero
                            </span>
                        </span>

                        <span className={styles.chevron}>
                            ›
                        </span>
                    </button>

                    <button
                        type="button"
                        className={`${styles.card} ${styles.familyCard}`}
                    >
                        <span
                            className={`${styles.icon} ${styles.familyIcon}`}
                        >
                            <FamilyIcon />
                        </span>

                        <span className={styles.cardText}>
                            <strong>Soy familiar</strong>
                            <span>
                                Contrato ayuda para un ser querido
                            </span>
                        </span>

                        <span className={styles.chevron}>
                            ›
                        </span>
                    </button>

                </div>

            </main>

        </div>
    );
}