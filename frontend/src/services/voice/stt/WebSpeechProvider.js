import { SpeechInputProvider } from './SpeechInputProvider'
import { SPANISH_LANG_CHAIN } from '../voiceCapabilities'

/**
 * Proveedor STT basado en la Web Speech API nativa del navegador.
 * Instrumentado con logs de diagnóstico para rastreo de eventos.
 */
export class WebSpeechProvider extends SpeechInputProvider {
  constructor(preferredLang = 'es-ES') {
    super()
    this.preferredLang = preferredLang
    this.recognition = null
    this.isListening = false
    this.langIndex = 0
    console.log('[VOICE-DEBUG][WebSpeechProvider] constructor llamado con preferredLang:', preferredLang)
    this._initRecognition()
  }

  _initRecognition() {
    const SpeechRecognition = typeof window !== 'undefined'
      ? (window.SpeechRecognition || window.webkitSpeechRecognition)
      : null

    console.log('[VOICE-DEBUG][WebSpeechProvider] SpeechRecognition constructor disponible:', !!SpeechRecognition)

    if (!SpeechRecognition) {
      console.warn('[VOICE-DEBUG][WebSpeechProvider] SpeechRecognition no soportado en este navegador')
      return
    }

    this.recognition = new SpeechRecognition()
    this.recognition.continuous = false
    this.recognition.interimResults = true
    this.recognition.maxAlternatives = 1

    // Seleccionar idioma con fallback de la cadena (iniciando en es-ES)
    this.recognition.lang = SPANISH_LANG_CHAIN[this.langIndex] || this.preferredLang
    console.log('[VOICE-DEBUG][WebSpeechProvider] recognition configurado con lang:', this.recognition.lang)

    this.recognition.onaudiostart = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onaudiostart (captura de audio iniciada por hardware)')
    }

    this.recognition.onsoundstart = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onsoundstart (sonido detectado por el motor)')
    }

    this.recognition.onspeechstart = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onspeechstart (habla detectada)')
      if (this.onSpeechStart) {
        this.onSpeechStart()
      }
    }

    this.recognition.onspeechend = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onspeechend (fin de habla detectado)')
    }

    this.recognition.onsoundend = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onsoundend (fin de sonido)')
    }

    this.recognition.onaudioend = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onaudioend (captura de audio finalizada)')
    }

    this.recognition.onstart = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onstart (reconocedor activado y escuchando)')
      this.isListening = true
    }

    this.recognition.onresult = (event) => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onresult recibido, results length:', event.results?.length)
      if (!event.results || event.results.length === 0) return

      const lastResult = event.results[event.results.length - 1]
      const transcript = lastResult[0]?.transcript?.trim() || ''
      const isFinal = lastResult.isFinal
      const confidence = lastResult[0]?.confidence

      console.log('[VOICE-DEBUG][WebSpeechProvider] onresult datos -> transcript:', transcript, 'isFinal:', isFinal, 'confidence:', confidence)

      if (transcript && this.onTranscript) {
        this.onTranscript(transcript, isFinal)
      }
    }

    this.recognition.onerror = (event) => {
      const errCode = event.error || 'unknown'
      console.error('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onerror:', errCode, 'mensaje:', event.message)

      // Si el error es de lenguaje no soportado, intentar con el siguiente en la cadena
      if (errCode === 'language-not-supported' && this.langIndex < SPANISH_LANG_CHAIN.length - 1) {
        this.langIndex++
        this.recognition.lang = SPANISH_LANG_CHAIN[this.langIndex]
        console.log('[VOICE-DEBUG][WebSpeechProvider] Fallback de idioma a:', this.recognition.lang)
        return
      }

      if (this.onError) {
        this.onError({
          code: errCode,
          message: event.message || `Error de reconocimiento de voz: ${errCode}`,
        })
      }
    }

    this.recognition.onend = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onend (reconocedor detenido, isListening era:', this.isListening, ')')
      this.isListening = false
      if (this.onEnd) {
        this.onEnd()
      }
    }
  }

  async start() {
    console.log('[VOICE-DEBUG][WebSpeechProvider] start() invocado. isListening actual:', this.isListening, 'recognition existe:', !!this.recognition)

    if (!this.recognition) {
      const err = new Error('Web Speech API no está soportada en este navegador.')
      console.error('[VOICE-DEBUG][WebSpeechProvider]', err)
      throw err
    }

    if (this.isListening) {
      console.warn('[VOICE-DEBUG][WebSpeechProvider] start() ignorado: ya está escuchando.')
      return
    }

    try {
      console.log('[VOICE-DEBUG][WebSpeechProvider] Ejecutando recognition.start()...')
      this.recognition.start()
      console.log('[VOICE-DEBUG][WebSpeechProvider] recognition.start() ejecutado sin lanzar excepción sincrónica.')
    } catch (err) {
      console.error('[VOICE-DEBUG][WebSpeechProvider] Excepción en recognition.start():', err.name, err.message)
      // Ignorar error si ya había iniciado
      if (err.name !== 'InvalidStateError') {
        throw err
      }
    }
  }

  stop() {
    console.log('[VOICE-DEBUG][WebSpeechProvider] stop() invocado. isListening:', this.isListening)
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop()
      } catch (err) {
        console.warn('[VOICE-DEBUG][WebSpeechProvider] Error en stop():', err)
      }
    }
    this.isListening = false
  }

  cancel() {
    console.log('[VOICE-DEBUG][WebSpeechProvider] cancel() invocado. isListening:', this.isListening)
    if (this.recognition) {
      try {
        this.recognition.abort()
      } catch (err) {
        console.warn('[VOICE-DEBUG][WebSpeechProvider] Error en abort():', err)
      }
    }
    this.isListening = false
  }
}
