import { useState } from 'react';
import styles from './AdultoMayorDashboard.module.css';

const PRECIO_REFERENCIAL_POR_HORA = 5000; // Solo demostración, no una tarifa definitiva.

function hoyLocal() {
  const fecha = new Date();
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, '0');
  const dia = String(fecha.getDate()).padStart(2, '0');
  return `${anio}-${mes}-${dia}`;
}

export function formatoPesos(valor) {
  return `$${new Intl.NumberFormat('es-CL').format(valor)}`;
}

export function formatoFecha(fecha) {
  // Mediodía local evita que la fecha cambie de día por el huso horario.
  return new Intl.DateTimeFormat('es-CL', { dateStyle: 'long' }).format(new Date(`${fecha}T12:00:00`));
}

export default function SolicitarTarea({ servicio, onVolver, onConfirmar, onVerSolicitudes }) {
  const [campos, setCampos] = useState({ fecha: '', hora: '', duracion: '2', descripcion: '' });
  const [paso, setPaso] = useState('formulario');
  const [error, setError] = useState('');
  const duracion = Number(campos.duracion);
  const precioEstimado = duracion * PRECIO_REFERENCIAL_POR_HORA;

  function actualizar(evento) {
    const { name, value } = evento.target;
    setCampos((actual) => ({ ...actual, [name]: value }));
    setError('');
  }

  function revisar(evento) {
    evento.preventDefault();
    const comienzo = new Date(`${campos.fecha}T${campos.hora}:00`);

    if (!campos.fecha || !campos.hora || Number.isNaN(comienzo.getTime())) {
      setError('Elige una fecha y una hora válidas.');
      return;
    }
    if (comienzo.getTime() <= Date.now()) {
      setError('La fecha y hora deben ser posteriores al momento actual.');
      return;
    }
    if (!campos.descripcion.trim() || campos.descripcion.trim().length < 10) {
      setError('Describe lo que necesitas en al menos 10 caracteres.');
      return;
    }
    setError('');
    setPaso('revisar');
  }

  function confirmar() {
    onConfirmar({
      servicioId: servicio.id,
      servicioNombre: servicio.nombre,
      servicioIcono: servicio.icono,
      fecha: campos.fecha,
      hora: campos.hora,
      duracion,
      descripcion: campos.descripcion.trim(),
      precioEstimado,
    });
    setPaso('completado');
  }

  return (
    <section className={styles.panelSolicitud} aria-labelledby="titulo-solicitud">
      <button type="button" className={styles.volver} onClick={onVolver}>
        <span aria-hidden="true">←</span> Volver a las tareas
      </button>

      {paso === 'completado' ? (
        <div className={styles.confirmacion} role="status">
          <span className={styles.confirmacionIcono} aria-hidden="true">✓</span>
          <h2 id="titulo-solicitud">Solicitud de prueba creada</h2>
          <p>Agregamos la solicitud a <strong>Mis solicitudes</strong> de esta demostración.</p>
          <p className={styles.alertaDemo}>No se guardó en SQL Server, no se realizó ningún cobro y ningún estudiante recibió la solicitud. Se perderá al recargar la página.</p>
          <button type="button" className={styles.botonPrimario} onClick={onVerSolicitudes}>
            Ver mis solicitudes de prueba
          </button>
        </div>
      ) : (
        <>
          <p className={styles.sobretitulo}>Pedir un servicio</p>
          <h2 id="titulo-solicitud" className={styles.tituloSeccion}>
            {paso === 'revisar' ? 'Revisa tu solicitud' : 'Solicitar una tarea'}
          </h2>
          <div className={styles.tareaElegida}>
            <span className={styles.servicioIcono} aria-hidden="true">{servicio.icono}</span>
            <div>
              <strong>{servicio.nombre}</strong>
              <p>{servicio.descripcion}</p>
            </div>
          </div>

          {paso === 'formulario' ? (
            <form className={styles.formularioSolicitud} onSubmit={revisar}>
              <p className={styles.textoAyuda}>Cuéntanos cuándo y en qué necesitas ayuda. Todos los datos de esta pantalla son de demostración.</p>
              <div className={styles.filaCampos}>
                <label className={styles.campo} htmlFor="sol-fecha">
                  <span>Fecha de la tarea</span>
                  <input id="sol-fecha" type="date" name="fecha" value={campos.fecha} min={hoyLocal()} onChange={actualizar} required />
                </label>
                <label className={styles.campo} htmlFor="sol-hora">
                  <span>Hora de inicio</span>
                  <input id="sol-hora" type="time" name="hora" value={campos.hora} onChange={actualizar} required />
                </label>
              </div>
              <label className={styles.campo} htmlFor="sol-duracion">
                <span>Duración estimada</span>
                <select id="sol-duracion" name="duracion" value={campos.duracion} onChange={actualizar} required>
                  <option value="1">1 hora</option>
                  <option value="2">2 horas</option>
                  <option value="3">3 horas</option>
                </select>
              </label>
              <label className={styles.campo} htmlFor="sol-descripcion">
                <span>Describe qué necesitas</span>
                <textarea
                  id="sol-descripcion"
                  name="descripcion"
                  value={campos.descripcion}
                  onChange={actualizar}
                  placeholder="Ejemplo: necesito ayuda para ordenar la cocina y guardar las compras."
                  minLength={10}
                  maxLength={500}
                  rows={4}
                  required
                />
                <small>No incluyas datos médicos ni información privada. Máximo 500 caracteres.</small>
              </label>
              {error && <p className={styles.errorSolicitud} role="alert">{error}</p>}
              <div className={styles.resumenPrecio}>
                <div>
                  <strong>Precio estimado de ejemplo</strong>
                  <span>{duracion} {duracion === 1 ? 'hora' : 'horas'} × {formatoPesos(PRECIO_REFERENCIAL_POR_HORA)}/hora</span>
                </div>
                <strong className={styles.montoPrecio}>{formatoPesos(precioEstimado)}</strong>
              </div>
              <p className={styles.alertaDemo}>Esta tarifa es inventada para probar la interfaz; no representa un precio aprobado ni se realizará un pago.</p>
              <div className={styles.accionesFormulario}>
                <button type="button" className={styles.botonNeutro} onClick={onVolver}>Cancelar</button>
                <button type="submit" className={styles.botonNaranja}>Revisar solicitud</button>
              </div>
            </form>
          ) : (
            <div className={styles.revision}>
              <dl className={styles.resumenDatos}>
                <div><dt>Tarea</dt><dd>{servicio.nombre}</dd></div>
                <div><dt>Fecha</dt><dd>{formatoFecha(campos.fecha)}</dd></div>
                <div><dt>Hora</dt><dd>{campos.hora}</dd></div>
                <div><dt>Duración</dt><dd>{duracion} {duracion === 1 ? 'hora' : 'horas'}</dd></div>
                <div><dt>Descripción</dt><dd>{campos.descripcion.trim()}</dd></div>
                <div><dt>Precio referencial de demostración</dt><dd>{formatoPesos(precioEstimado)}</dd></div>
              </dl>
              <p className={styles.alertaDemo}>Al confirmar solo crearás una solicitud simulada en esta página. No se enviará a personas reales ni se guardará en la base de datos.</p>
              <div className={styles.accionesFormulario}>
                <button type="button" className={styles.botonNeutro} onClick={() => setPaso('formulario')}>Editar datos</button>
                <button type="button" className={styles.botonNaranja} onClick={confirmar}>Confirmar solicitud de prueba</button>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  );
}
