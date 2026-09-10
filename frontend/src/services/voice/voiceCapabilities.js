/**
 * Detección de capacidades de voz para navegadores móviles.
 * Diseñado para ser 100% tolerante a fallos en dispositivos Android económicos.
 */

// Cadena de fallback de idiomas para español
export const SPANISH_LANG_CHAIN = ['es-CO', 'es-419', 'es-ES']

/**
 * Detecta el mejor formato MIME de audio soportado para grabación.
 */
export function getSupportedAudioMime() {
  if (typeof window === 'undefined' || !window.MediaRecorder) {
    return null
  }

  const candidateMimes = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/aac',
    'audio/ogg;codecs=opus',
    'audio/ogg',
  ]

  for (const mime of candidateMimes) {
    try {
      if (window.MediaRecorder.isTypeSupported(mime)) {
        return mime
      }
    } catch {
      // Ignorar excepciones de navegadores antiguos
    }
  }

  return ''
}

/**
 * Detecta capacidades completas del entorno del navegador.
 */
export async function getVoiceCapabilities() {
  const isBrowser = typeof window !== 'undefined'

  const hasSpeechRecognition = isBrowser && !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  const hasSpeechSynthesis = isBrowser && !!window.speechSynthesis
  const hasMediaRecorder = isBrowser && !!window.MediaRecorder
  const supportedMime = getSupportedAudioMime()
  const isOnline = isBrowser ? navigator.onLine : true

  // Detección segura de permisos (navigator.permissions es opcional en algunos navegadores)
  let micPermissionState = 'unknown'
  if (isBrowser && navigator.permissions && typeof navigator.permissions.query === 'function') {
    try {
      const status = await navigator.permissions.query({ name: 'microphone' })
      micPermissionState = status.state // 'granted', 'prompt', 'denied'
    } catch {
      micPermissionState = 'unknown'
    }
  }

  return {
    speechRecognitionAvailable: hasSpeechRecognition,
    speechSynthesisAvailable: hasSpeechSynthesis,
    mediaRecorderAvailable: hasMediaRecorder,
    supportedAudioMime: supportedMime,
    micPermission: micPermissionState,
    isOnline,
    // La voz en la app es viable si al menos tiene Web Speech o MediaRecorder para fallback
    voiceSupported: hasSpeechRecognition || (hasMediaRecorder && !!supportedMime),
    preferredLang: 'es-CO',
  }
}
