import { SpeechInputProvider } from './SpeechInputProvider.js'
import { SPANISH_LANG_CHAIN } from '../voiceCapabilities.js'

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
    this.isStarting = false
    this.isStopping = false
    this.langIndex = 0
    this._endResolvers = []
    console.log('[VOICE-DEBUG][WebSpeechProvider] constructor llamado con preferredLang:', preferredLang)
    this._initRecognition()
  }

  isActive() {
    return this.isStarting || this.isListening || this.isStopping
  }

  waitForEnd(timeoutMs = 800) {
    if (!this.isActive()) {
      return Promise.resolve()
    }
    return new Promise((resolve) => {
      let resolved = false
      const timer = setTimeout(() => {
        if (resolved) return
        resolved = true
        const idx = this._endResolvers.indexOf(resolveWrapper)
        if (idx !== -1) this._endResolvers.splice(idx, 1)
        this.isStarting = false
        this.isListening = false
        this.isStopping = false
        resolve()
      }, timeoutMs)

      const resolveWrapper = () => {
        if (resolved) return
        resolved = true
        clearTimeout(timer)
        resolve()
      }
      this._endResolvers.push(resolveWrapper)
    })
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
        this.onSpeechStart(this.turnId, this.sessionGeneration)
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
      this.isStarting = false
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
        this.onTranscript(transcript, isFinal, this.turnId, this.sessionGeneration)
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
        }, this.turnId, this.sessionGeneration)
      }
    }

    this.recognition.onend = () => {
      console.log('[VOICE-DEBUG][WebSpeechProvider] EVENTO: onend (reconocedor detenido, isListening era:', this.isListening, ')')
      this.isStarting = false
      this.isListening = false
      this.isStopping = false

      // Despertar promesas esperando el cierre asíncrono
      const resolvers = this._endResolvers
      this._endResolvers = []
      resolvers.forEach((resolve) => resolve())

      if (this.onEnd) {
        this.onEnd(this.turnId, this.sessionGeneration)
      }
    }
  }

  _forceResetRecognition() {
    if (this.recognition) {
      try {
        this.recognition.onstart = null
        this.recognition.onend = null
        this.recognition.onerror = null
        this.recognition.onresult = null
        this.recognition.onspeechstart = null
        this.recognition.onspeechend = null
        this.recognition.onaudiostart = null
        this.recognition.onaudioend = null
        this.recognition.onsoundstart = null
        this.recognition.onsoundend = null
        this.recognition.abort()
      } catch (_) {}
    }
    this._initRecognition()
    this.isStarting = false
    this.isListening = false
    this.isStopping = false

    const resolvers = this._endResolvers
    this._endResolvers = []
    resolvers.forEach((resolve) => resolve())
  }

  async start(turnId = null, sessionGeneration = 0) {
    console.log('[VOICE-DEBUG][WebSpeechProvider] start() invocado. turnId:', turnId, 'isListening:', this.isListening, 'isStarting:', this.isStarting, 'isStopping:', this.isStopping)
    this.turnId = turnId
    this.sessionGeneration = sessionGeneration

    if (!this.recognition) {
      const err = new Error('Web Speech API no está soportada en este navegador.')
      console.error('[VOICE-DEBUG][WebSpeechProvider]', err)
      throw err
    }

    // Guard de lifecycle estricto contra reentrancia
    if (this.isListening || this.isStarting) {
      console.warn('[VOICE-LIFECYCLE] WebSpeechProvider.start() ignorado: STT ya está activo o iniciando.', {
        isListening: this.isListening,
        isStarting: this.isStarting,
      })
      return
    }

    if (this.isStopping) {
      console.warn('[VOICE-LIFECYCLE] WebSpeechProvider.start(): esperando cierre definitivo de sesión previa...')
      await this.waitForEnd(800)
      if (this.isActive()) {
        console.warn('[VOICE-LIFECYCLE] WebSpeechProvider.start(): forzando reinicio tras timeout de cierre.')
        this._forceResetRecognition()
      }
    }

    this.isStarting = true

    try {
      console.log('[VOICE-DEBUG][WebSpeechProvider] Ejecutando recognition.start()...')
      this.recognition.start()
      console.log('[VOICE-DEBUG][WebSpeechProvider] recognition.start() ejecutado sin lanzar excepción sincrónica.')
    } catch (err) {
      this.isStarting = false
      console.error('[VOICE-DEBUG][WebSpeechProvider] Excepción en recognition.start():', err.name, err.message)
      if (err.name === 'InvalidStateError') {
        // Transición de recuperación controlada, NO dejar un WebSpeech fantasma
        console.warn('[VOICE-STT] WebSpeech InvalidStateError: recognition already started en Chrome. Neutralizando instancia y reseteando sin dejar fantasma...')
        this._forceResetRecognition()

        if (this.onError) {
          this.onError({
            code: 'invalid-state',
            message: 'SpeechRecognition ya había iniciado o estado desincronizado (InvalidStateError)',
          }, this.turnId, this.sessionGeneration)
        }
        return
      }
      throw err
    }
  }

  requestStop(turnId = null) {
    console.log('[VOICE-STT] requestStop() invocado en WebSpeechProvider. turnId:', turnId ?? this.turnId, 'isListening:', this.isListening, 'isStopping:', this.isStopping)
    if (this.recognition && this.isListening && !this.isStopping) {
      this.isStopping = true
      try {
        this.recognition.stop()
      } catch (err) {
        console.warn('[VOICE-STT] Error en recognition.stop():', err)
      }
    }
    // isListening=false solamente en onend
  }

  stop(turnId = null) {
    this.requestStop(turnId)
  }

  async stopAndWait(timeoutMs = 800) {
    this.requestStop(this.turnId)
    await this.waitForEnd(timeoutMs)
    if (this.isActive()) {
      this._forceResetRecognition()
    }
  }

  cancel(turnId = null) {
    console.log('[VOICE-DEBUG][WebSpeechProvider] cancel() invocado. turnId:', turnId ?? this.turnId, 'isListening:', this.isListening, 'isStopping:', this.isStopping)
    if (this.recognition && this.isActive()) {
      this.isStopping = true
      try {
        this.recognition.abort()
      } catch (err) {
        console.warn('[VOICE-DEBUG][WebSpeechProvider] Error en abort():', err)
      }
    }
    // isListening=false solamente en onend
  }

  async abortAndWait(timeoutMs = 800) {
    console.log('[VOICE-DEBUG][WebSpeechProvider] abortAndWait() invocado. isActive:', this.isActive())
    if (!this.isActive()) return
    this.cancel(this.turnId)
    await this.waitForEnd(timeoutMs)
    if (this.isActive()) {
      console.warn('[VOICE-DEBUG][WebSpeechProvider] abortAndWait timeout excedido, neutralizando instancia y recreando...')
      this._forceResetRecognition()
    }
  }
}
