import { SpeechInputProvider } from './SpeechInputProvider.js'
import { SPANISH_LANG_CHAIN } from '../voiceCapabilities.js'

/**
 * Proveedor STT basado en la Web Speech API nativa del navegador.
 * Arquitectura aislada por instancia y generación con protección estricta contra
 * callbacks huérfanos o desincronizados de reconocedores destruidos o abortados.
 */
export class WebSpeechProvider extends SpeechInputProvider {
  constructor(preferredLang = 'es-ES') {
    super()
    this.preferredLang = preferredLang
    this.recognition = null
    this.isListening = false
    this.isStarting = false
    this.isStopping = false
    this._abortRequested = false
    this.langIndex = 0
    this._endResolvers = []
    this._instanceCounter = 0
    this.instanceId = 'ws_0'

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

    if (!SpeechRecognition) {
      console.warn('[VOICE-DEBUG][WebSpeechProvider] SpeechRecognition no soportado en este navegador')
      this.recognition = null
      return
    }

    // Generar identificador único inmutable de esta instancia de recognition
    const instanceId = 'ws_' + (++this._instanceCounter)
    this.instanceId = instanceId

    const rec = new SpeechRecognition()
    rec.continuous = false
    rec.interimResults = true
    rec.maxAlternatives = 1
    rec.lang = SPANISH_LANG_CHAIN[this.langIndex] || this.preferredLang

    rec.onaudiostart = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onaudiostart`)
    }

    rec.onsoundstart = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onsoundstart`)
    }

    rec.onspeechstart = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onspeechstart turnId=${this.turnId}`)
      if (this.onSpeechStart) {
        this.onSpeechStart(this.turnId, this.sessionGeneration, this.generation, instanceId)
      }
    }

    rec.onspeechend = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onspeechend`)
    }

    rec.onsoundend = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onsoundend`)
    }

    rec.onaudioend = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onaudioend`)
    }

    rec.onstart = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onstart`)
      this.isStarting = false
      this.isListening = true
    }

    rec.onresult = (event) => {
      if (this.instanceId !== instanceId) return
      if (!event.results || event.results.length === 0) return

      const lastResult = event.results[event.results.length - 1]
      const transcript = lastResult[0]?.transcript?.trim() || ''
      const isFinal = lastResult.isFinal
      const confidence = lastResult[0]?.confidence

      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] onresult -> "${transcript}" isFinal=${isFinal} conf=${confidence}`)

      if (transcript && this.onTranscript) {
        this.onTranscript(transcript, isFinal, this.turnId, this.sessionGeneration, this.generation, instanceId)
      }
    }

    rec.onerror = (event) => {
      if (this.instanceId !== instanceId) return
      const errCode = event.error || 'unknown'

      // Si fue abort intencional o durante detención/cancelación, absorberlo sin propagar error
      if (errCode === 'aborted' && (this.isStopping || this._abortRequested)) {
        console.log(`[VOICE-LIFECYCLE][WebSpeechProvider][${instanceId}] onerror: 'aborted' esperado (absorbido limpiamente)`)
        return
      }

      console.error(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onerror: ${errCode} - ${event.message}`)

      // Fallback de idioma
      if (errCode === 'language-not-supported' && this.langIndex < SPANISH_LANG_CHAIN.length - 1) {
        this.langIndex++
        rec.lang = SPANISH_LANG_CHAIN[this.langIndex]
        console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] Fallback de idioma a: ${rec.lang}`)
        return
      }

      if (this.onError) {
        this.onError({
          code: errCode,
          message: event.message || `Error de reconocimiento de voz: ${errCode}`,
        }, this.turnId, this.sessionGeneration, this.generation, instanceId)
      }
    }

    rec.onend = () => {
      if (this.instanceId !== instanceId) return
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${instanceId}] EVENTO: onend (isListening era: ${this.isListening})`)
      this.isStarting = false
      this.isListening = false
      this.isStopping = false
      this._abortRequested = false

      // Despertar promesas esperando el cierre asíncrono
      const resolvers = this._endResolvers
      this._endResolvers = []
      resolvers.forEach((resolve) => resolve())

      if (this.onEnd) {
        this.onEnd(this.turnId, this.sessionGeneration, this.generation, instanceId)
      }
    }

    this.recognition = rec
  }

  _detachAndNeutralizeInstance(rec, instanceId) {
    if (!rec) return
    rec.onstart = null
    rec.onspeechstart = null
    rec.onspeechend = null
    rec.onaudiostart = null
    rec.onaudioend = null
    rec.onsoundstart = null
    rec.onsoundend = null
    rec.onresult = null
    rec.onerror = (e) => {
      console.log(`[VOICE-LIFECYCLE][WebSpeechProvider][${instanceId}] onerror en instancia neutralizada (absorbido): ${e?.error}`)
    }
    rec.onend = () => {
      console.log(`[VOICE-LIFECYCLE][WebSpeechProvider][${instanceId}] onend en instancia neutralizada (despertando waiters)`)
      const resolvers = this._endResolvers
      this._endResolvers = []
      resolvers.forEach((resolve) => resolve())
    }
    try {
      rec.abort()
    } catch (_) {}
  }

  _forceResetRecognition() {
    const dyingRec = this.recognition
    const dyingId = this.instanceId
    this.recognition = null
    this._detachAndNeutralizeInstance(dyingRec, dyingId)

    this.isStarting = false
    this.isListening = false
    this.isStopping = false
    this._abortRequested = false

    const resolvers = this._endResolvers
    this._endResolvers = []
    resolvers.forEach((resolve) => resolve())

    this._initRecognition()
  }

  async start(turnId = null, sessionGeneration = 0, providerGeneration = 0) {
    console.log(`[VOICE-DEBUG][WebSpeechProvider] start() invocado. turnId=${turnId} gen=${providerGeneration} isListening=${this.isListening} isStarting=${this.isStarting} isStopping=${this.isStopping}`)
    this.turnId = turnId
    this.sessionGeneration = sessionGeneration
    this.generation = providerGeneration
    this._abortRequested = false

    if (!this.recognition) {
      this._initRecognition()
      if (!this.recognition) {
        const err = new Error('Web Speech API no está soportada en este navegador.')
        console.error('[VOICE-DEBUG][WebSpeechProvider]', err)
        throw err
      }
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
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${this.instanceId}] Ejecutando recognition.start()...`)
      this.recognition.start()
      console.log(`[VOICE-DEBUG][WebSpeechProvider][${this.instanceId}] recognition.start() completado sin excepción sincrónica.`)
    } catch (err) {
      this.isStarting = false
      console.error('[VOICE-DEBUG][WebSpeechProvider] Excepción en recognition.start():', err.name, err.message)
      if (err.name === 'InvalidStateError') {
        console.warn('[VOICE-STT] WebSpeech InvalidStateError: neutralizando instancia y reseteando sin dejar fantasma...')
        this._forceResetRecognition()

        if (this.onError) {
          this.onError({
            code: 'invalid-state',
            message: 'SpeechRecognition ya había iniciado o estado desincronizado (InvalidStateError)',
          }, this.turnId, this.sessionGeneration, this.generation, this.instanceId)
        }
        return
      }
      throw err
    }
  }

  requestStop(turnId = null) {
    console.log(`[VOICE-STT] requestStop() invocado en WebSpeechProvider. turnId=${turnId ?? this.turnId} isListening=${this.isListening} isStopping=${this.isStopping}`)
    if (this.recognition && this.isListening && !this.isStopping) {
      this.isStopping = true
      try {
        this.recognition.stop()
      } catch (err) {
        console.warn('[VOICE-STT] Error en recognition.stop():', err)
      }
    }
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
    console.log(`[VOICE-DEBUG][WebSpeechProvider] cancel() invocado. turnId=${turnId ?? this.turnId} isListening=${this.isListening} isStopping=${this.isStopping}`)
    this._abortRequested = true
    if (this.recognition && this.isActive()) {
      this.isStopping = true
      const dyingRec = this.recognition
      const dyingId = this.instanceId
      this.recognition = null
      this._detachAndNeutralizeInstance(dyingRec, dyingId)
      this.isStarting = false
      this.isListening = false
      this.isStopping = false
      this._initRecognition()
    }
  }

  async abortAndWait(timeoutMs = 800) {
    console.log('[VOICE-DEBUG][WebSpeechProvider] abortAndWait() invocado. isActive:', this.isActive())
    if (!this.isActive() && !this.recognition) return
    this.cancel(this.turnId)
    await this.waitForEnd(timeoutMs)
    if (this.isActive()) {
      console.warn('[VOICE-DEBUG][WebSpeechProvider] abortAndWait timeout excedido, neutralizando instancia y recreando...')
      this._forceResetRecognition()
    }
  }
}
