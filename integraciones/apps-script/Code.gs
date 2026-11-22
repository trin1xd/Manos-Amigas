/**
 * Manos Amigas — envío de códigos desde el Gmail del proyecto.
 * No pongas contraseñas ni claves en este archivo ni en GitHub.
 * Uso: ejecutar prepararConexion UNA vez y luego publicar como aplicación web.
 */

function prepararConexion() {
  const secreto = Utilities.getUuid().replace(/-/g, '') +
                  Utilities.getUuid().replace(/-/g, '');
  PropertiesService.getScriptProperties().setProperty('MANOS_AMIGAS_SECRET', secreto);
  console.log('MAIL_APPS_SCRIPT_SECRET=' + secreto);
  console.log('Guarda la clave en Render > backend > Environment. No la compartas.');
}

function respuesta_(ok, motivo) {
  // Solo diagnósticos generales. Nunca incluir direcciones, códigos ni claves.
  return ContentService
    .createTextOutput(JSON.stringify({ok: ok, motivo: ok ? null : (motivo || 'error_interno')}))
    .setMimeType(ContentService.MimeType.JSON);
}

function mismoTextoSeguro_(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' ||
      a.length !== b.length || a.length !== 64) return false;
  let diferencia = 0;
  for (let i = 0; i < a.length; i++) {
    diferencia |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return diferencia === 0;
}

function huellaClave_(clave) {
  // Solo para detectar discrepancias; NO se devuelve la clave ni la huella.
  const bytes = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256, clave, Utilities.Charset.UTF_8);
  return bytes.map(b => (b & 255).toString(16).padStart(2, '0')).join('').slice(0, 16);
}

function doPost(e) {
  try {
    const datos = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const clave = PropertiesService.getScriptProperties().getProperty('MANOS_AMIGAS_SECRET');
    if (!clave) return respuesta_(false, 'clave_ausente');

    const fecha = datos.timestamp;
    const destino = datos.to;
    const asunto = datos.subject;
    const cuerpo = datos.body;
    const firma = datos.signature;
    const huellaRecibida = datos.key_fingerprint;
    if (!Number.isSafeInteger(fecha) ||
        typeof destino !== 'string' || destino.length > 255 ||
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(destino) ||
        typeof asunto !== 'string' || !asunto ||
        asunto.length > 150 || /[\r\n]/.test(asunto) ||
        typeof cuerpo !== 'string' || !cuerpo || cuerpo.length > 3000 ||
        typeof firma !== 'string' || !/^[0-9a-f]{64}$/.test(firma)) {
      return respuesta_(false, 'solicitud_invalida');
    }
    if (Math.abs(Date.now() - fecha * 1000) > 120000) {
      return respuesta_(false, 'hora_desincronizada');
    }

    // Comparar identificadores no reversibles antes de HMAC. Si difieren
    // sabemos que las dos configuraciones son distintas. Nunca exponerlos.
    if (typeof huellaRecibida === 'string' && /^[0-9a-f]{16}$/.test(huellaRecibida) &&
        huellaRecibida !== huellaClave_(clave)) {
      return respuesta_(false, 'clave_distinta');
    }

    const mensajeFirmado = fecha + '\n' + destino + '\n' + asunto + '\n' + cuerpo;
    const bytes = Utilities.computeHmacSha256Signature(
      mensajeFirmado, clave, Utilities.Charset.UTF_8);
    const esperado = bytes.map(b => (b & 255).toString(16).padStart(2, '0')).join('');
    if (!mismoTextoSeguro_(esperado, firma)) {
      // Huella idéntica: mismo secreto, pero se firmaron textos diferentes.
      // Con clientes anteriores que no envían huella, dejar motivo genérico.
      return respuesta_(false,
        typeof huellaRecibida === 'string' && huellaRecibida === huellaClave_(clave)
          ? 'firma_no_coincide' : 'firma_invalida');
    }

    // Bloqueo básico de un reenvío accidental de la misma solicitud.
    const cache = CacheService.getScriptCache();
    const llave = 'correo-' + firma;
    if (cache.get(llave)) return respuesta_(false, 'solicitud_duplicada');
    if (MailApp.getRemainingDailyQuota() < 1) return respuesta_(false, 'cuota_agotada');

    try {
      MailApp.sendEmail({
        to: destino,
        subject: asunto,
        body: cuerpo,
        name: 'Manos Amigas'
      });
    } catch (errorCorreo) {
      return respuesta_(false, 'error_gmail');
    }
    cache.put(llave, 'enviado', 180);
    return respuesta_(true);
  } catch (error) {
    // No mostrar el código, la clave ni datos personales en respuestas o logs.
    return respuesta_(false, 'error_interno');
  }
}
