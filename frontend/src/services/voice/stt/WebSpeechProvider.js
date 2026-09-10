import { SpeechInputProvider } from './SpeechInputProvider'
import { SPANISH_LANG_CHAIN } from '../voiceCapabilities'

/**
 * Proveedor STT basado en la Web Speech API nativa del navegador.
 * Ligero, 0 kB de dependencias externas y 0 uso de CPU adicional.
 */
export class WebSpeechProvider extends SpeechInputProvider {
  constructor(preferredLang = 'es-CO') {
    super()
    this.preferredLang = preferredLang
    this.recognition = null
    this.isListening = false
    this.langIndex = 0
    this._initRecognition()
  }

  _initRecognition() {
    const SpeechRecognition = typeof window !== 'undefined'
      ? (window.SpeechRecognition || window.webkitSpeechRecognition)
      : null

    if (!SpeechRecognition) {
      return
    }

    this.recognition = new SpeechRecognition()
    this.recognition.continuous = false
    this.recognition.interimResults = true
    this.recognition.maxAlternatives = 1

    // Seleccionar idioma con fallback de la cadena
    this.recognition.lang = SPANISH_LANG_CHAIN[this.langIndex] || this.preferredLang

    this.recognition.onstart = () => {
      this.isListening = true
      if (this.onSpeechStart) {
        this.onSpeechStart()
      }
    }

    this.recognition.onspeechstart = () => {
      if (this.onSpeechStart) {
        this.onSpeechStart()
      }
    }

    this.recognition.onresult = (event) => {
      if (!event.results || event.results.length === 0) return

      const lastResult = event.results[event.results.length - 1]
      const transcript = lastResult[0]?.transcript?.trim() || ''
      const isFinal = lastResult.isFinal

      if (transcript && this.onTranscript) {
        this.onTranscript(transcript, isFinal)
      }
    }

    this.recognition.onerror = (event) => {
      const errCode = event.error || 'unknown'

      // Si el error es de lenguaje no soportado, intentar con el siguiente en la cadena
      if (errCode === 'language-not-supported' && this.langIndex < SPANISH_LANG_CHAIN.length - 1) {
        this.langIndex++
        this.recognition.lang = SPANISH_LANG_CHAIN[this.langIndex]
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
      this.isListening = false
      if (this.onEnd) {
        this.onEnd()
      }
    }
  }

  async start() {
    if (!this.recognition) {
      throw new Error('Web Speech API no está soportada en este navegador.')
    }

    if (this.isListening) {
      return
    }

    try {
      this.recognition.start()
    } catch (err) {
      // Ignorar error si ya había iniciado
      if (err.name !== 'InvalidStateError') {
        throw err
      }
    }
  }

  stop() {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop()
      } catch {
        // Ignorar
      }
    }
    this.isListening = false
  }

  cancel() {
    if (this.recognition) {
      try {
        this.recognition.abort()
      } catch {
        // Ignorar
      }
    }
    this.isListening = false
  }
}
