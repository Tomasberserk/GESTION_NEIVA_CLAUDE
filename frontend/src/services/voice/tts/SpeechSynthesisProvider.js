/**
 * Adaptador de Text-to-Speech (TTS) nativo del navegador.
 * Soporta carga asíncrona de voces en Android (onvoiceschanged)
 * y filtrado inteligente de español latino/colombiano.
 */

export class SpeechSynthesisProvider {
  constructor() {
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null
    this.voices = []
    this.selectedVoice = null
    this.isSpeaking = false
    this.onStart = null
    this.onEnd = null
    this.onError = null

    this._initVoices()
  }

  _initVoices() {
    if (!this.synth) return

    const loadVoices = () => {
      this.voices = this.synth.getVoices()
      this._selectBestSpanishVoice()
    }

    loadVoices()

    // En Android Chrome las voces cargan con retraso asíncrono
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = loadVoices
    }
  }

  _selectBestSpanishVoice() {
    if (!this.voices || this.voices.length === 0) return

    // Preferencias en orden: es-CO -> es-419 -> es-US -> es-ES -> cualquier 'es'
    const priorities = ['es-CO', 'es-419', 'es-US', 'es-ES', 'es']

    for (const langCode of priorities) {
      const match = this.voices.find(
        (v) => v.lang && v.lang.toLowerCase().replace('_', '-').startsWith(langCode.toLowerCase())
      )
      if (match) {
        this.selectedVoice = match
        return
      }
    }

    // Si no hay español explícito, tomar la primera voz por defecto
    this.selectedVoice = this.voices[0] || null
  }

  speak(text) {
    if (!this.synth) {
      if (this.onEnd) this.onEnd()
      return
    }

    // Cancelar cualquier audio en reproducción previa
    this.cancel()

    // Limpiar texto para lectura natural (remover asteriscos markdown, corchetes, etc.)
    const cleanText = text
      .replace(/[*_#`~]/g, '')
      .replace(/\[\d+\]/g, '')
      .replace(/\s+/g, ' ')
      .trim()

    if (!cleanText) {
      if (this.onEnd) this.onEnd()
      return
    }

    const utterance = new SpeechSynthesisUtterance(cleanText)
    if (this.selectedVoice) {
      utterance.voice = this.selectedVoice
      utterance.lang = this.selectedVoice.lang || 'es-CO'
    } else {
      utterance.lang = 'es-CO'
    }

    // Velocidad ligeramente más viva (1.05) para dinamismo en tienda
    utterance.rate = 1.05
    utterance.pitch = 1.0

    utterance.onstart = () => {
      this.isSpeaking = true
      if (this.onStart) {
        this.onStart()
      }
    }

    utterance.onend = () => {
      this.isSpeaking = false
      if (this.onEnd) {
        this.onEnd()
      }
    }

    utterance.onerror = (event) => {
      this.isSpeaking = false
      // No disparar error fatal si fue una cancelación intencional
      if (event.error !== 'interrupted' && event.error !== 'canceled') {
        if (this.onError) {
          this.onError({ code: event.error, message: 'Fallo al reproducir audio' })
        }
      }
      if (this.onEnd) {
        this.onEnd()
      }
    }

    try {
      this.synth.speak(utterance)
    } catch {
      this.isSpeaking = false
      if (this.onEnd) this.onEnd()
    }
  }

  cancel() {
    if (this.synth) {
      try {
        this.synth.cancel()
      } catch {
        // Ignorar
      }
    }
    this.isSpeaking = false
  }
}
