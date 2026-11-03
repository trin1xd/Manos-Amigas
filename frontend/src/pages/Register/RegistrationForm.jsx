import { useState } from 'react';
import {
  registerAdultoMayor,
  registerUniversitario,
  registerFamiliar,
} from '../../services/authService';
import styles from './RegistrationForm.module.css';

const COMMON_FIELDS = [
  { name: 'nombre_completo', label: 'Nombre completo', required: true, maxLength: 150, autoComplete: 'name' },
  { name: 'rut', label: 'RUT', required: true, placeholder: '12.345.678-5', maxLength: 20 },
  { name: 'telefono', label: 'Teléfono', required: true, type: 'tel', placeholder: '+56912345678', maxLength: 20, autoComplete: 'tel' },
  { name: 'email', label: 'Correo electrónico', required: true, type: 'email', maxLength: 255, autoComplete: 'email' },
  { name: 'password', label: 'Contraseña (mínimo 8 caracteres)', required: true, type: 'password', minLength: 8, maxLength: 128, autoComplete: 'new-password' },
];

const SETTINGS = {
  ADULTO_MAYOR: {
    title: 'Registro adulto mayor',
    description: 'Completa tus datos para solicitar ayuda en el hogar.',
    register: registerAdultoMayor,
    fields: [
      ...COMMON_FIELDS,
      { name: 'fecha_nacimiento', label: 'Fecha de nacimiento', required: true, type: 'date' },
      { name: 'direccion', label: 'Dirección del hogar', required: true, maxLength: 255, autoComplete: 'street-address' },
      { name: 'contacto_confianza_nombre', label: 'Nombre del contacto de confianza', required: true, maxLength: 150 },
      { name: 'contacto_confianza_telefono', label: 'Teléfono del contacto de confianza', required: true, type: 'tel', maxLength: 20 },
      { name: 'indicaciones_acceso', label: 'Indicaciones de acceso (opcional)', maxLength: 500, multiline: true, placeholder: 'Timbre, portón, mascota...' },
    ],
  },
  UNIVERSITARIO: {
    title: 'Registro universitario',
    description: 'Tu cuenta quedará pendiente de verificación antes de poder prestar servicios.',
    register: registerUniversitario,
    fields: [
      ...COMMON_FIELDS,
      { name: 'fecha_nacimiento', label: 'Fecha de nacimiento', required: true, type: 'date' },
      { name: 'universidad', label: 'Universidad', required: true, maxLength: 150 },
      { name: 'carrera', label: 'Carrera', required: true, maxLength: 150 },
      { name: 'anio_cursa', label: 'Año que cursas', required: true, type: 'number', min: 1, max: 10 },
      { name: 'correo_institucional', label: 'Correo institucional', required: true, type: 'email', maxLength: 255 },
      { name: 'contacto_emergencia_nombre', label: 'Nombre del contacto de emergencia', required: true, maxLength: 150 },
      { name: 'contacto_emergencia_telefono', label: 'Teléfono del contacto de emergencia', required: true, type: 'tel', maxLength: 20 },
    ],
  },
  FAMILIAR: {
    title: 'Registro familiar',
    description: 'Crea una cuenta para gestionar apoyo para un ser querido.',
    register: registerFamiliar,
    fields: [
      ...COMMON_FIELDS,
      { name: 'parentesco', label: 'Parentesco o relación con el adulto mayor', required: true, maxLength: 100 },
      { name: 'telefono_alternativo', label: 'Teléfono alternativo (opcional)', type: 'tel', maxLength: 20 },
    ],
  },
};

export default function RegistrationForm({ role, onBack, onLogin }) {
  const settings = SETTINGS[role];
  const [form, setForm] = useState({});
  const [fieldErrors, setFieldErrors] = useState({});
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [completed, setCompleted] = useState(false);

  if (!settings) return <p>Perfil de registro desconocido.</p>;

  async function handleSubmit(event) {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setFieldErrors({});
    setMessage('');
    try {
      const result = await settings.register(form);
      if (result?.success) {
        setCompleted(true);
      } else {
        setMessage('No fue posible completar el registro.');
      }
    } catch (error) {
      setFieldErrors(error.fields || {});
      setMessage(error.message || 'No se pudo conectar con el servidor.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.topBar}>
        <button type="button" onClick={onBack} aria-label="Volver a seleccionar perfil" className={styles.back}>←</button>
        <strong>Manos Amigas</strong>
        <span aria-hidden="true" />
      </header>
      <main className={styles.container}>
        <div className={styles.card}>
          {completed ? (
            <div role="status" className={styles.success}>
              <h1>¡Registro completado!</h1>
              <p>{role === 'UNIVERSITARIO'
                ? 'Tu cuenta fue creada y está pendiente de verificación. Todavía no puedes ofrecer servicios.'
                : 'Tu cuenta fue creada correctamente.'}</p>
              <button className={styles.submit} onClick={onLogin}>Ir a iniciar sesión</button>
            </div>
          ) : (
            <>
              <h1>{settings.title}</h1>
              <p className={styles.description}>{settings.description}</p>
              <form onSubmit={handleSubmit}>
                {settings.fields.map((field) => (
                  <div key={field.name} className={styles.field}>
                    <label htmlFor={field.name}>{field.label}</label>
                    {field.multiline ? (
                      <textarea
                        id={field.name}
                        value={form[field.name] ?? ''}
                        onChange={(e) => setForm(prev => ({ ...prev, [field.name]: e.target.value }))}
                        maxLength={field.maxLength}
                        placeholder={field.placeholder}
                        rows={3}
                      />
                    ) : (
                      <input
                        id={field.name}
                        name={field.name}
                        type={field.type || 'text'}
                        value={form[field.name] ?? ''}
                        onChange={(e) => setForm(prev => ({ ...prev, [field.name]: e.target.value }))}
                        required={!!field.required}
                        minLength={field.minLength}
                        maxLength={field.maxLength}
                        min={field.min}
                        max={field.max}
                        autoComplete={field.autoComplete}
                        placeholder={field.placeholder}
                      />
                    )}
                    {fieldErrors[field.name] && <span className={styles.error} role="alert">{fieldErrors[field.name]}</span>}
                  </div>
                ))}
                {message && <p className={styles.errorSummary} role="alert">{message}</p>}
                <button type="submit" className={styles.submit} disabled={submitting}>
                  {submitting ? 'Registrando…' : 'Crear mi cuenta'}
                </button>
              </form>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
