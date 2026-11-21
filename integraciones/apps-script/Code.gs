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

function respuesta_(ok) {
  return ContentService
    .createTextOutput(JSON.stringify({ok: ok}))
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

function doPost(e) {
  try {
    const datos = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const clave = PropertiesService.getScriptProperties().getProperty('MANOS_AMIGAS_SECRET');
    if (!clave) return respuesta_(false);

    const fecha = datos.timestamp;
    const destino = datos.to;
    const asunto = datos.subject;
    const cuerpo = datos.body;
    const firma = datos.signature;
    if (!Number.isSafeInteger(fecha) ||
        Math.abs(Date.now() - fecha * 1000) > 120000 ||
        typeof destino !== 'string' || destino.length > 255 ||
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(destino) ||
        typeof asunto !== 'string' || !asunto ||
        asunto.length > 150 || /[\r\n]/.test(asunto) ||
        typeof cuerpo !== 'string' || !cuerpo || cuerpo.length > 3000 ||
        typeof firma !== 'string' || !/^[0-9a-f]{64}$/.test(firma)) {
      return respuesta_(false);
    }

    const mensajeFirmado = fecha + '\n' + destino + '\n' + asunto + '\n' + cuerpo;
    const bytes = Utilities.computeHmacSha256Signature(mensajeFirmado, clave);
    const esperado = bytes.map(b => (b & 255).toString(16).padStart(2, '0')).join('');
    if (!mismoTextoSeguro_(esperado, firma)) return respuesta_(false);

    // Bloqueo básico de un reenvío accidental de la misma solicitud.
    const cache = CacheService.getScriptCache();
    const llave = 'correo-' + firma;
    if (cache.get(llave)) return respuesta_(false);
    if (MailApp.getRemainingDailyQuota() < 1) return respuesta_(false);

    MailApp.sendEmail({
      to: destino,
      subject: asunto,
      body: cuerpo,
      name: 'Manos Amigas'
    });
    cache.put(llave, 'enviado', 180);
    return respuesta_(true);
  } catch (error) {
    // No mostrar el código, la clave ni datos personales en respuestas o logs.
    return respuesta_(false);
  }
}
