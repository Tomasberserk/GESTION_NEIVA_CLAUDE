/**
 * Detección de capacidades de voz para navegadores móviles.
 * Diseñado para ser 100% tolerante a fallos en dispositivos Android económicos.
 */

// Cadena de fallback de idiomas para español (es-ES es el más universal en servidores Google)
export const SPANISH_LANG_CHAIN = ['es-ES', 'es-419', 'es-CO']

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
 * Detecta características del dispositivo y sistema operativo de forma exhaustiva.
 */
export function detectDeviceCapabilities() {
  if (typeof window === 'undefined' || typeof navigator === 'undefined') {
    return {
      isAndroid: false,
      isMobile: false,
      userAgent: 'server',
      platform: 'unknown',
      maxTouchPoints: 0,
    }
  }

  const ua = navigator.userAgent || ''
  const platform = navigator.platform || ''
  const maxTouchPoints = navigator.maxTouchPoints || 0

  // 1. Detección estricta de Android (UA o UserAgentData API)
  const isAndroid = /Android/i.test(ua) ||
    (typeof navigator.userAgentData !== 'undefined' && navigator.userAgentData?.platform === 'Android')

  // 2. Detección general de móvil / tablet
  const isMobile = isAndroid ||
    /iPhone|iPad|iPod/i.test(ua) ||
    (typeof navigator.userAgentData !== 'undefined' && !!navigator.userAgentData?.mobile) ||
    (maxTouchPoints > 1 && /Macintosh|Linux/i.test(ua))

  return {
    isAndroid,
    isMobile,
    userAgent: ua,
    platform,
    maxTouchPoints,
  }
}

/**
 * Detecta capacidades completas del entorno del navegador.
 */
export async function getVoiceCapabilities() {
  const isBrowser = typeof window !== 'undefined'
  const device = detectDeviceCapabilities()

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
    isAndroid: device.isAndroid,
    isMobile: device.isMobile,
    device,
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

