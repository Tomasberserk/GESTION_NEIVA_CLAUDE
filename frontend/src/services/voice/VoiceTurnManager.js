import { WebSpeechProvider } from './stt/WebSpeechProvider.js'
import { BackendSTTProvider } from './stt/BackendSTTProvider.js'
import { SpeechSynthesisProvider } from './tts/SpeechSynthesisProvider.js'
import { voiceTelemetry } from './telemetry/voiceTelemetry.js'
import { detectDeviceCapabilities } from './voiceCapabilities.js'

/**
 * Estados formales del VoiceTurnManager.
 */
export const VoiceTurnState = {
  IDLE: 'IDLE',
  READY: 'READY',
  LISTENING: 'LISTENING',
  SPEECH_DETECTED: 'SPEECH_DETECTED',
  PROCESSING: 'PROCESSING',
  SPEAKING: 'SPEAKING',
  SETTLING: 'SETTLING',
  CONFIRMING: 'CONFIRMING',
  ERROR: 'ERROR',
}

/**
 * VoiceTurnManager: Gestor desacoplado de turnos de audio, concurrencia y anti-eco.
 * Arquitectura transaccional de turno único con validación estricta de lifecycle y
 * aislamiento total contra callbacks desfasados o reentrantes.
 */
export class VoiceTurnManager {
  constructor(options = {}) {
    console.log('[VOICE-DEBUG][VoiceTurnManager] Instanciando VoiceTurnManager...')
    this.onStateChange = options.onStateChange || null
    this.onTranscriptUpdate = options.onTranscriptUpdate || null
    this.onAgentResponse = options.onAgentResponse || null
    this.onSendMessage = options.onSendMessage || null

    this.state = VoiceTurnState.IDLE
    this.lastTranscript = ''
    this.interimTranscript = ''
    this.sessionGeneration = 0
    this.turnCounter = 0
    this.currentTurnId = 0
    this.providerCounter = 0
    this.providerGeneration = 0
    this.stopRequested = false
    this.fallbackInProgress = false
    this.turnFinalized = false
    this.isTranscribing = false

    // Proveedores
    this.webSpeechProvider = new WebSpeechProvider()
    this.backendSTTProvider = new BackendSTTProvider()
    this.tts = new SpeechSynthesisProvider()

    // Política Android-First / Mobile-First:
    const dev = detectDeviceCapabilities()
    console.log('[VOICE-CAPABILITIES]', {
      isAndroid: dev.isAndroid,
      isMobile: dev.isMobile,
      userAgent: dev.userAgent,
      platform: dev.platform,
      maxTouchPoints: dev.maxTouchPoints,
      provider: dev.isAndroid || dev.isMobile ? 'BackendSTTProvider' : 'WebSpeechProvider',
    })

    if (dev.isAndroid || dev.isMobile) {
      console.info('[VOICE-DEBUG][VoiceTurnManager] Móvil detectado (Android-First): asignando BackendSTTProvider como primario')
      this.activeProviderType = 'backend'
      this.currentSTT = this.backendSTTProvider
    } else {
      this.activeProviderType = 'webspeech'
      this.currentSTT = this.webSpeechProvider
    }

    // Timers de seguridad
    this.speechEndTimer = null
    this.settlingTimer = null
    this.operationalTimer = null
    this.watchdogTimer = null
    this.stopRequestTimer = null
    this.processingWatchdogTimer = null

    this._bindProviders()
    console.log('[VOICE-DEBUG][VoiceTurnManager] Instanciación completa. Estado inicial:', this.state, 'Proveedor activo:', this.activeProviderType)
  }

  _isTurnActive(turnId, sessionGen = null, providerGen = null) {
    if (turnId !== this.currentTurnId) return false
    if (sessionGen !== null && sessionGen !== this.sessionGeneration) return false
    if (providerGen !== null && providerGen !== this.providerGeneration) return false
    return true
  }

  _logLifecycle(event, details = {}) {
    const timestamp = new Date().toISOString()
    console.log(`[VOICE-LIFECYCLE] ${timestamp} turn=${this.currentTurnId} gen=${this.providerGeneration} session=${this.sessionGeneration} provider=${this.activeProviderType} state=${this.state} event=${event}`, details)
  }

  _logStaleCallback(event, context = {}) {
    console.warn(`[VOICE-LIFECYCLE] IGNORED_STALE_CALLBACK event=${event} callbackTurn=${context.turnId} callbackGen=${context.providerGen} activeTurn=${this.currentTurnId} activeGen=${this.providerGeneration} state=${this.state}`)
  }

  _invalidateCurrentTurn() {
    this.currentTurnId = ++this.turnCounter
    this.providerGeneration = ++this.providerCounter
    this.currentSTT.generation = this.providerGeneration
    this.stopRequested = false
    this.fallbackInProgress = false
    this.turnFinalized = false
    this.isTranscribing = false
    this.interimTranscript = ''
    this._limpiarTimers()
    if (this.currentSTT) {
      try { this.currentSTT.cancel(this.currentTurnId) } catch (_) {}
    }
    this._setState(VoiceTurnState.READY)
  }

  _setState(newState, data = {}) {
    const oldState = this.state
    console.log(`[VOICE-DEBUG][VoiceTurnManager] _setState: [${oldState}] -> [${newState}]`, data)
    if (this.state === newState) {
      console.log(`[VOICE-DEBUG][VoiceTurnManager] _setState ignorado (ya estaba en ${newState})`)
      return
    }
    this.state = newState
    if (this.onStateChange) {
      this.onStateChange(newState, data)
    }
  }

  _bindProviders() {
    console.log('[VOICE-DEBUG][VoiceTurnManager] _bindProviders() configurando callbacks de STT y TTS...')

    const setupSTT = (provider, name) => {
      provider.onRequestStop = (turnId, sessionGen, providerGen) => {
        const resolvedTurnId = turnId ?? this.currentTurnId
        const resolvedSessionGen = sessionGen ?? this.sessionGeneration
        const resolvedProviderGen = providerGen ?? provider.generation

        if (
          provider !== this.currentSTT ||
          !this._isTurnActive(resolvedTurnId, resolvedSessionGen, resolvedProviderGen)
        ) {
          this._logStaleCallback(`onRequestStop [${name}]`, { turnId: resolvedTurnId, providerGen: resolvedProviderGen })
          return
        }

        console.log(`[VOICE-TURN] onRequestStop recibido desde provider [${name}] turnId=${resolvedTurnId}`)
        this.detenerYEnviar()
      }

      provider.onSpeechStart = (turnId, sessionGen, providerGen) => {
        const resolvedTurnId = turnId ?? this.currentTurnId
        const resolvedSessionGen = sessionGen ?? this.sessionGeneration
        const resolvedProviderGen = providerGen ?? provider.generation

        if (
          provider !== this.currentSTT ||
          !this._isTurnActive(resolvedTurnId, resolvedSessionGen, resolvedProviderGen)
        ) {
          this._logStaleCallback(`onSpeechStart [${name}]`, { turnId: resolvedTurnId, providerGen: resolvedProviderGen })
          return
        }

        console.log(`[VOICE-STT] onstart turnId=${resolvedTurnId}`)
        console.log(`[VOICE-TURN] SPEECH_DETECTED turnId=${resolvedTurnId}`)
        if (this.state === VoiceTurnState.LISTENING) {
          this._setState(VoiceTurnState.SPEECH_DETECTED)
          voiceTelemetry.recordSpeechDetected()
        }
      }

      provider.onTranscript = (transcript, isFinal, turnId, sessionGen, providerGen) => {
        const resolvedTurnId = turnId ?? this.currentTurnId
        const resolvedSessionGen = sessionGen ?? this.sessionGeneration
        const resolvedProviderGen = providerGen ?? provider.generation

        if (
          provider !== this.currentSTT ||
          !this._isTurnActive(resolvedTurnId, resolvedSessionGen, resolvedProviderGen)
        ) {
          this._logStaleCallback(`onTranscript [${name}]`, { turnId: resolvedTurnId, providerGen: resolvedProviderGen })
          return
        }

        console.log(`[VOICE-STT] onresult turnId=${resolvedTurnId} transcript="${transcript}" isFinal=${isFinal}`)
        this.interimTranscript = transcript
        if (this.onTranscriptUpdate) {
          this.onTranscriptUpdate(transcript, isFinal)
        }

        if (isFinal || (this.stopRequested && transcript.trim())) {
          console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${resolvedTurnId} texto="${transcript}"`)
          if (this.stopRequestTimer) {
            clearTimeout(this.stopRequestTimer)
            this.stopRequestTimer = null
          }
          this.lastTranscript = transcript
          this._finalizarTurnoVocal(transcript, resolvedTurnId, resolvedSessionGen)
        } else {
          this._reiniciarTimerSilencio(transcript, resolvedTurnId, resolvedSessionGen)
        }
      }

      provider.onError = (err, turnId, sessionGen, providerGen) => {
        const resolvedTurnId = turnId ?? this.currentTurnId
        const resolvedSessionGen = sessionGen ?? this.sessionGeneration
        const resolvedProviderGen = providerGen ?? provider.generation

        if (
          provider !== this.currentSTT ||
          !this._isTurnActive(resolvedTurnId, resolvedSessionGen, resolvedProviderGen)
        ) {
          this._logStaleCallback(`onError [${name}]`, { turnId: resolvedTurnId, providerGen: resolvedProviderGen })
          return
        }

        console.error(`[VOICE-DEBUG][VoiceTurnManager][${name}] onError turnId=${resolvedTurnId}:`, err)
        this._handleSTTError(err, resolvedTurnId, resolvedProviderGen, name, resolvedSessionGen)
      }

      provider.onEnd = (turnId, sessionGen, providerGen) => {
        const resolvedTurnId = turnId ?? this.currentTurnId
        const resolvedSessionGen = sessionGen ?? this.sessionGeneration
        const resolvedProviderGen = providerGen ?? provider.generation

        if (
          provider !== this.currentSTT ||
          !this._isTurnActive(resolvedTurnId, resolvedSessionGen, resolvedProviderGen)
        ) {
          this._logStaleCallback(`onEnd [${name}]`, { turnId: resolvedTurnId, providerGen: resolvedProviderGen })
          return
        }

        console.log(`[VOICE-STT] onend turnId=${resolvedTurnId} interim="${this.interimTranscript}" stopRequested=${this.stopRequested}`)

        // Si hay una transcripción pendiente (ej: BackendSTT subiendo audio), NO volver a READY
        if (this.isTranscribing || this.currentSTT?.isPendingTranscription) {
          console.log(`[VOICE-STT] onend diferido: transcripción en progreso turnId=${resolvedTurnId}, esperando resultado`)
          return
        }

        // Si el turno ya finalizó, ignorar
        if (this.turnFinalized) {
          return
        }

        // Si se solicitó stop pero aún no llegó la transcripción, esperar
        if (this.stopRequested) {
          console.log(`[VOICE-STT] onend tras stopRequested sin transcripción aún turnId=${resolvedTurnId}, esperando transcripción...`)
          return
        }

        // Si estamos en SPEECH_DETECTED
        if (this.state === VoiceTurnState.SPEECH_DETECTED) {
          if (this.interimTranscript && this.interimTranscript.trim()) {
            console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${resolvedTurnId} texto="${this.interimTranscript}"`)
            this._finalizarTurnoVocal(this.interimTranscript, resolvedTurnId, resolvedSessionGen)
          } else {
            console.warn(`[VOICE-TURN] onEnd en SPEECH_DETECTED sin transcripción turnId=${resolvedTurnId}, esperando resultado o watchdog...`)
          }
          return
        }

        // Si estaba en LISTENING puro
        if (this.state === VoiceTurnState.LISTENING) {
          console.warn(`[VOICE-TURN] onEnd sin transcripción turnId=${resolvedTurnId} -> regresando a READY`)
          this._setState(VoiceTurnState.READY)
        }
      }
    }

    setupSTT(this.webSpeechProvider, 'WebSpeech')
    setupSTT(this.backendSTTProvider, 'BackendSTT')

    // Configurar TTS
    this.tts.onStart = () => {
      const turnId = this.currentTurnId
      console.log(`[VOICE-TTS] START turnId=${turnId}`)
      this._setState(VoiceTurnState.SPEAKING)
    }

    this.tts.onEnd = () => {
      const turnId = this.currentTurnId
      console.log(`[VOICE-TTS] END turnId=${turnId}`)
      this._iniciarVentanaSettling(turnId)
    }

    this.tts.onError = (err) => {
      const turnId = this.currentTurnId
      console.warn(`[VOICE-TTS] onError turnId=${turnId}:`, err)
      this._iniciarVentanaSettling(turnId)
    }
  }

  _reiniciarTimerSilencio(currentText, turnId, sessionGen = null) {
    if (this.speechEndTimer) {
      clearTimeout(this.speechEndTimer)
    }
    const resolvedSessionGen = sessionGen ?? this.sessionGeneration
    this.speechEndTimer = setTimeout(() => {
      if (!this._isTurnActive(turnId, resolvedSessionGen)) {
        this._logStaleCallback('speechEndTimer', { turnId })
        return
      }
      if (this.state === VoiceTurnState.SPEECH_DETECTED && currentText.trim()) {
        console.log(`[VOICE-TURN] Timer de silencio expiró turnId=${turnId}. Deteniendo...`)
        this.currentSTT.stop(turnId)
        this._finalizarTurnoVocal(currentText, turnId, resolvedSessionGen)
      }
    }, 1100)
  }

  _handleSTTError(err, turnId, providerGen, name, sessionGen = null) {
    const resolvedSessionGen = sessionGen ?? this.sessionGeneration
    if (!this._isTurnActive(turnId, resolvedSessionGen, providerGen)) {
      this._logStaleCallback(`_handleSTTError [${name}]`, { turnId, providerGen })
      return
    }

    console.warn(`[VOICE-DEBUG][VoiceTurnManager] _handleSTTError procesando turnId=${turnId}:`, err)
    voiceTelemetry.recordSTTFailure(err.code)

    // Caso A: Error no recuperable (permiso denegado)
    if (err.code === 'not-allowed' || err.code === 'permission-denied') {
      console.error(`[VOICE-STT] Permiso de micrófono denegado turnId=${turnId}`)
      this._setState(VoiceTurnState.ERROR, { message: 'Permiso de micrófono denegado.' })
      return
    }

    // Caso B: 'aborted' es el resultado normal de detener o cancelar el reconocedor
    if (err.code === 'aborted') {
      console.log(`[VOICE-LIFECYCLE] aborted recibido e ignorado limpiamente turnId=${turnId}`)
      return
    }

    // Caso C: Fallback a BackendSTT para fallos de red o hardware en WebSpeech
    const esRecuperableWebSpeech = (
      this.activeProviderType === 'webspeech' &&
      (err.code === 'no-speech' ||
       err.code === 'network' ||
       err.code === 'audio-capture' ||
       err.code === 'start-error' ||
       err.code === 'invalid-state')
    )

    if (esRecuperableWebSpeech) {
      if (!this.stopRequested && !this.fallbackInProgress && !this.turnFinalized) {
        console.info(`[VOICE-STT] FALLBACK_DECISION turnId=${turnId} provider=BackendSTT motivo=${err.code}`)
        this._conmutarABackendSTT(turnId, resolvedSessionGen)
        return
      }
    }

    // Si ya estamos en backend o no es recuperable, regresar a READY
    this.isTranscribing = false
    this._setState(VoiceTurnState.READY)
  }

  async _conmutarABackendSTT(turnId, sessionGen = null) {
    const resolvedSessionGen = sessionGen ?? this.sessionGeneration
    if (!this._isTurnActive(turnId, resolvedSessionGen) || this.fallbackInProgress) {
      console.warn(`[VOICE-TURN] Fallback ignorado turnId=${turnId} (activo: ${this.currentTurnId}, en progreso: ${this.fallbackInProgress})`)
      return
    }
    this.fallbackInProgress = true

    // 1. Incrementar providerGeneration de inmediato para descartar cualquier callback residual de WebSpeech
    this.providerGeneration = ++this.providerCounter
    this.activeProviderType = 'backend'
    this.currentSTT = this.backendSTTProvider
    this.backendSTTProvider.generation = this.providerGeneration
    this.stopRequested = false
    this.isTranscribing = false
    this.turnFinalized = false
    this.interimTranscript = ''
    this._setState(VoiceTurnState.LISTENING)

    // 2. Limpiar WebSpeech
    if (typeof this.webSpeechProvider.abortAndWait === 'function') {
      console.log(`[VOICE-TURN] Esperando cierre definitivo de WebSpeech antes de iniciar BackendSTT turnId=${turnId}...`)
      await this.webSpeechProvider.abortAndWait(800)
    } else {
      this.webSpeechProvider.cancel()
    }

    if (!this._isTurnActive(turnId, resolvedSessionGen)) {
      this.fallbackInProgress = false
      return
    }

    voiceTelemetry.recordFallbackUsed()
    console.log(`[VOICE-STT] BACKEND_START turnId=${turnId}`)

    // 3. Reiniciar el watchdog STT con ventana limpia de 9s para BackendSTT
    this._iniciarWatchdogSTT(turnId, resolvedSessionGen)

    try {
      await this.backendSTTProvider.start(turnId, resolvedSessionGen, this.providerGeneration)
      this.fallbackInProgress = false
    } catch (err) {
      this.fallbackInProgress = false
      if (!this._isTurnActive(turnId, resolvedSessionGen)) return
      console.error(`[VOICE-STT] Falló arranque de BackendSTT fallback turnId=${turnId}:`, err)
      this._setState(VoiceTurnState.READY)
    }
  }

  /**
   * Inicia la sesión de voz tras el toque del usuario con saludo de bienvenida opcional.
   */
  async activarSesion(saludar = true) {
    this.sessionGeneration++
    const dev = detectDeviceCapabilities()
    console.log('[VOICE-CAPABILITIES] activarSesion', {
      isAndroid: dev.isAndroid,
      isMobile: dev.isMobile,
      userAgent: dev.userAgent,
      platform: dev.platform,
      maxTouchPoints: dev.maxTouchPoints,
      provider: this.currentSTT?.constructor?.name,
    })
    console.log('[VOICE-DEBUG][VoiceTurnManager] activarSesion() llamado. Estado antes:', this.state)
    this._invalidateCurrentTurn()
    this.tts.cancel()
    this.currentSTT.cancel()
    voiceTelemetry.recordSessionStart()

    // Desbloquear audio del sintetizador (User Interaction Gesture Unlock)
    this.tts.resume()

    if (saludar) {
      console.log('[VOICE-DEBUG][VoiceTurnManager] Reproduciendo saludo inicial con voz...')
      this.reproducirRespuesta('¡Listo, te escucho! ¿Qué vendiste hoy?', VoiceTurnState.READY)
      return
    }

    this._setState(VoiceTurnState.READY)
    console.log('[VOICE-DEBUG][VoiceTurnManager] activarSesion() llamando a iniciarEscucha()...')
    return this.iniciarEscucha()
  }

  /**
   * Abre el micrófono para un turno discreto, blindado con lifecycle guards.
   */
  async iniciarEscucha() {
    const dev = detectDeviceCapabilities()

    // Guard de lifecycle estricto contra reentrancia
    if (
      this.state === VoiceTurnState.LISTENING ||
      this.state === VoiceTurnState.SPEECH_DETECTED ||
      this.currentSTT?.isListening ||
      this.currentSTT?.isStarting ||
      this.currentSTT?.isActive?.()
    ) {
      console.warn('[VOICE-LIFECYCLE] iniciarEscucha ignorado: STT ya activo o iniciando', {
        state: this.state,
        provider: this.currentSTT?.constructor?.name,
        isListening: this.currentSTT?.isListening,
        isStarting: this.currentSTT?.isStarting,
        isActive: this.currentSTT?.isActive?.(),
      })
      return
    }

    if (this.state === VoiceTurnState.SPEAKING || this.state === VoiceTurnState.SETTLING) {
      console.warn(`[VOICE-DEBUG][VoiceTurnManager] iniciarEscucha() bloqueado por anti-eco (estado=${this.state})`)
      return
    }

    // No iniciar mientras WebSpeech esté en proceso de apagado
    if (typeof this.webSpeechProvider.isActive === 'function' && this.webSpeechProvider.isActive()) {
      console.log('[VOICE-DEBUG][VoiceTurnManager] Esperando que WebSpeech complete su cierre previo antes de iniciar nuevo turno...')
      await this.webSpeechProvider.abortAndWait(800)
    }

    this._limpiarTimers()
    const turnId = ++this.turnCounter
    this.currentTurnId = turnId
    const sessionGen = this.sessionGeneration
    this.providerGeneration = ++this.providerCounter
    this.currentSTT.generation = this.providerGeneration
    this.stopRequested = false
    this.fallbackInProgress = false
    this.turnFinalized = false
    this.isTranscribing = false
    this.interimTranscript = ''
    this._setState(VoiceTurnState.LISTENING)

    console.log(`[VOICE-TURN] START_TURN turnId=${turnId}`)
    console.log(`[VOICE-STT] ACTIVE_PROVIDER=${this.activeProviderType} (${this.currentSTT?.constructor?.name})`)
    console.log('[VOICE-CAPABILITIES] iniciarEscucha', {
      isAndroid: dev.isAndroid,
      isMobile: dev.isMobile,
      userAgent: dev.userAgent,
      platform: dev.platform,
      maxTouchPoints: dev.maxTouchPoints,
      provider: this.currentSTT?.constructor?.name,
    })

    if (this.activeProviderType === 'backend') {
      console.log(`[VOICE-STT] BACKEND_START turnId=${turnId}`)
    }

    this._iniciarWatchdogSTT(turnId, sessionGen)

    try {
      await this.currentSTT.start(turnId, sessionGen, this.providerGeneration)
      console.log(`[VOICE-DEBUG][VoiceTurnManager] currentSTT.start() completado turnId=${turnId}`)
    } catch (err) {
      if (!this._isTurnActive(turnId, sessionGen)) {
        this._logStaleCallback('currentSTT.start() exception', { turnId })
        return
      }
      console.error(`[VOICE-DEBUG][VoiceTurnManager] Excepción en currentSTT.start() turnId=${turnId}:`, err)
      this._handleSTTError({ code: err.name || 'start-error', message: err.message }, turnId, this.providerGeneration, this.activeProviderType, sessionGen)
    }
  }

  /**
   * Procesa la transcripción final y la envía al backend (Única ruta transaccional).
   */
  async _finalizarTurnoVocal(texto, turnId, sessionGen = null) {
    if (!this._isTurnActive(turnId, sessionGen)) {
      this._logStaleCallback('_finalizarTurnoVocal', { turnId, sessionGen })
      return
    }

    if (this.turnFinalized) {
      console.warn(`[VOICE-TURN] Turno ya finalizado previamente turnId=${turnId}, ignorando llamada duplicada.`)
      return
    }

    console.log(`[VOICE-DEBUG][VoiceTurnManager] _finalizarTurnoVocal() turnId=${this.currentTurnId} con texto:`, texto)
    if (!texto || !texto.trim()) {
      console.warn(`[VOICE-DEBUG][VoiceTurnManager] _finalizarTurnoVocal ignorado por texto vacío turnId=${this.currentTurnId}`)
      this.isTranscribing = false
      this._setState(VoiceTurnState.READY)
      return
    }

    this.turnFinalized = true
    this.isTranscribing = false
    this._limpiarTimers()
    this.currentSTT.stop(turnId)
    this._setState(VoiceTurnState.PROCESSING, { texto })
    this._iniciarWatchdogProcessing(turnId, sessionGen)

    console.log(`[VOICE-TURN] SEND_MESSAGE turnId=${this.currentTurnId} texto="${texto.trim()}"`)
    const t0 = Date.now()

    try {
      if (!this.onSendMessage) {
        throw new Error('No hay callback onSendMessage configurado.')
      }

      const res = await this.onSendMessage(texto.trim())

      // Guard post-asíncrono obligatorio: si el turno fue invalidado o cambiado mientras se esperaba la respuesta
      if (!this._isTurnActive(turnId, sessionGen) || this.state !== VoiceTurnState.PROCESSING) {
        this._logStaleCallback('onSendMessage_resolved_after_invalidation', { turnId, sessionGen })
        return
      }

      if (this.processingWatchdogTimer) {
        clearTimeout(this.processingWatchdogTimer)
        this.processingWatchdogTimer = null
      }

      const latency = Date.now() - t0
      console.log(`[VOICE-TURN] AGENT_RESPONSE turnId=${this.currentTurnId} latency=${latency}ms:`, res)
      voiceTelemetry.recordBackendResponse(latency)

      if (this.onAgentResponse) {
        this.onAgentResponse(res)
      }

      const respuestaTexto = res.respuesta || 'Operación procesada.'
      const esConfirmacion = res.estado === 'READY_TO_CONFIRM'

      if (res.estado === 'EXECUTED') {
        voiceTelemetry.recordCommandSuccess()
      } else if (res.estado === 'IDLE' && texto.toLowerCase().includes('no')) {
        voiceTelemetry.recordCommandCancelled()
      }

      // Reproducir audio con la respuesta
      this.reproducirRespuesta(respuestaTexto, esConfirmacion ? VoiceTurnState.CONFIRMING : VoiceTurnState.READY)
    } catch (err) {
      if (!this._isTurnActive(turnId, sessionGen) || this.state !== VoiceTurnState.PROCESSING) {
        return
      }
      if (this.processingWatchdogTimer) {
        clearTimeout(this.processingWatchdogTimer)
        this.processingWatchdogTimer = null
      }
      console.error('[VOICE-DEBUG][VoiceTurnManager] Error al procesar mensaje con backend:', err)
      this.reproducirRespuesta(`Hubo un error: ${err.message}`, VoiceTurnState.READY)
    }
  }

  /**
   * Envía un mensaje manual (por ejemplo, al hacer clic en el botón de confirmación táctil).
   */
  async enviarMensajeManual(texto) {
    if (this.state === VoiceTurnState.PROCESSING) {
      console.warn('[VOICE-TURN] enviarMensajeManual ignorado: ya se está procesando un turno')
      return
    }
    const turnId = this.currentTurnId
    const sessionGen = this.sessionGeneration
    console.log(`[VOICE-DEBUG][VoiceTurnManager] enviarMensajeManual llamado turnId=${turnId} con:`, texto)
    this.currentSTT.cancel(turnId)
    return this._finalizarTurnoVocal(texto, turnId, sessionGen)
  }

  /**
   * Reproduce la respuesta con TTS silenciando el micrófono.
   */
  reproducirRespuesta(texto, siguienteEstado = VoiceTurnState.READY) {
    const turnId = this.currentTurnId
    console.log(`[VOICE-TTS] START turnId=${turnId} texto="${texto}", siguienteEstado=${siguienteEstado}`)
    this._limpiarTimers()
    this.currentSTT.cancel(turnId)
    this._nextStateAfterSettling = siguienteEstado
    this._setState(VoiceTurnState.SPEAKING)
    this.tts.speak(texto)
  }

  /**
   * Ventana de reposo acústico (250 ms) para absorber ecos de altavoces.
   */
  _iniciarVentanaSettling(turnId) {
    console.log(`[VOICE-TTS] END turnId=${turnId}`)
    console.log(`[VOICE-TURN] SETTLING turnId=${turnId} (250ms)`)
    this._setState(VoiceTurnState.SETTLING)
    this.settlingTimer = setTimeout(() => {
      if (turnId !== this.currentTurnId) {
        this._logStaleCallback('settlingTimer', { turnId })
        return
      }
      const targetState = this._nextStateAfterSettling || VoiceTurnState.READY
      console.log(`[VOICE-TURN] ${targetState} turnId=${turnId}`)
      this._setState(targetState)

      if (targetState === VoiceTurnState.READY || targetState === VoiceTurnState.CONFIRMING) {
        console.log(`[VOICE-DEBUG][VoiceTurnManager] Reanudando escucha tras settling turnId=${turnId}...`)
        this.iniciarEscucha()
      }
    }, 250)
  }

  detenerSesion() {
    console.log('[VOICE-DEBUG][VoiceTurnManager] detenerSesion() llamado')
    this.sessionGeneration++
    this._invalidateCurrentTurn()
    this.tts.cancel()
    this.currentSTT.cancel()
    this._setState(VoiceTurnState.IDLE)
  }

  /**
   * requestStop / detenerYEnviar: Idempotente y tolerante a retrasos de onresult.
   */
  detenerYEnviar() {
    const turnId = this.currentTurnId
    const sessionGen = this.sessionGeneration
    console.log(`[VOICE-TURN] detenerYEnviar() invocado en estado: ${this.state} turnId=${turnId} stopRequested=${this.stopRequested}`)

    if (!turnId) return

    // Limpiar watchdog de captura STT para que no colisione con PROCESSING
    if (this.watchdogTimer) {
      clearTimeout(this.watchdogTimer)
      this.watchdogTimer = null
    }

    // Si ya se solicitó el stop y ya está en PROCESSING, asegurar parada física del STT y salir
    if (this.stopRequested) {
      if (typeof this.currentSTT?.requestStop === 'function') {
        try { this.currentSTT.requestStop(turnId) } catch (_) {}
      }
      return
    }

    // Si no está escuchando o detectando habla, asegurar parada de STT y salir
    if (this.state !== VoiceTurnState.LISTENING && this.state !== VoiceTurnState.SPEECH_DETECTED) {
      if (typeof this.currentSTT?.requestStop === 'function') {
        try { this.currentSTT.requestStop(turnId) } catch (_) {}
      }
      return
    }

    this.stopRequested = true
    console.log(`[VOICE-TURN] REQUEST_STOP turnId=${turnId}`)
    console.log(`[VOICE-STT] provider.stop turnId=${turnId}`)

    // Si ya tenemos texto interim acumulado, podemos finalizarlo de inmediato
    if (this.interimTranscript && this.interimTranscript.trim()) {
      console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${turnId} (usando interim existente: "${this.interimTranscript}")`)
      this.currentSTT.cancel(turnId)
      this._finalizarTurnoVocal(this.interimTranscript, turnId, sessionGen)
      return
    }

    // BackendSTT: marcar transcripción pendiente, pasar de inmediato a PROCESSING para feedback visual en el orbe
    if (this.activeProviderType === 'backend') {
      this.isTranscribing = true
      this._setState(VoiceTurnState.PROCESSING, { transcripcionEnVuelo: true })
      this._iniciarWatchdogProcessing(turnId, sessionGen)
      if (typeof this.currentSTT.requestStop === 'function') {
        this.currentSTT.requestStop(turnId)
      } else {
        this.currentSTT.stop(turnId)
      }
      return
    }

    // Solicitar stop al provider WebSpeech
    if (typeof this.currentSTT.requestStop === 'function') {
      this.currentSTT.requestStop(turnId)
    } else {
      this.currentSTT.stop(turnId)
    }

    // Si es WebSpeech, esperar hasta 750ms a que entregue onresult antes de declarar que no hubo resultado
    if (this.activeProviderType === 'webspeech') {
      if (this.stopRequestTimer) clearTimeout(this.stopRequestTimer)
      this.stopRequestTimer = setTimeout(() => {
        if (!this._isTurnActive(turnId, sessionGen)) {
          this._logStaleCallback('stopRequestTimer', { turnId })
          return
        }
        if (this.interimTranscript && this.interimTranscript.trim()) {
          console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${turnId} texto="${this.interimTranscript}"`)
          this._finalizarTurnoVocal(this.interimTranscript, turnId, sessionGen)
        } else {
          console.warn(`[VOICE-STT] NO_FINAL_RESULT turnId=${turnId}`)
          // Si el usuario intentó enviar pero nunca hubo audio ni transcripción: volver limpiamente a READY
          this.currentSTT.cancel(turnId)
          this._setState(VoiceTurnState.READY)
        }
      }, 750)
    }
  }

  /**
   * Watchdog STT de seguridad (9s) asociado exclusivamente al turnId y sessionGeneration activos.
   */
  _iniciarWatchdogSTT(turnId, sessionGen = null) {
    if (this.watchdogTimer) {
      clearTimeout(this.watchdogTimer)
    }
    const targetSessionGen = sessionGen ?? this.sessionGeneration
    console.log(`[VOICE-DEBUG][VoiceTurnManager] Programando watchdog STT (9s) turnId=${turnId} sessionGen=${targetSessionGen}`)
    this.watchdogTimer = setTimeout(() => {
      if (!this._isTurnActive(turnId, targetSessionGen)) {
        this._logStaleCallback('watchdogTimer STT', { turnId })
        return
      }
      console.warn(`[VOICE-DEBUG][VoiceTurnManager] Watchdog STT expiró (9s) turnId=${turnId}. Estado: ${this.state}`)

      // Si el turno ya finalizó o pasó a PROCESSING/SPEAKING, ignorar
      if (this.turnFinalized || this.state === VoiceTurnState.PROCESSING || this.state === VoiceTurnState.SPEAKING) {
        return
      }

      // Si hay una transcripción pendiente en progreso (BackendSTT subiendo audio), permitir que finalice
      if (this.isTranscribing || this.currentSTT?.isPendingTranscription) {
        console.log(`[VOICE-TURN] Watchdog STT: transcripción en vuelo para turnId=${turnId}, permitiendo que finalice.`)
        return
      }

      // Si hubo voz detectada
      if (this.state === VoiceTurnState.SPEECH_DETECTED) {
        if (this.interimTranscript && this.interimTranscript.trim()) {
          this.detenerYEnviar()
        } else {
          // Si se detectó ruido o habla pero nunca hubo texto transcribible tras 9s, regresar a READY
          console.warn(`[VOICE-TURN] Watchdog STT: habla detectada pero sin transcripción tras 9s. Reseteando a READY turnId=${turnId}`)
          this.currentSTT.cancel(turnId)
          this._setState(VoiceTurnState.READY)
        }
        return
      }

      // Si estaba en LISTENING (silencio puro tras 9s)
      if (this.state === VoiceTurnState.LISTENING) {
        console.warn(`[VOICE-TURN] Watchdog reiniciando a READY por silencio turnId=${turnId}`)
        this.currentSTT.cancel(turnId)
        this._setState(VoiceTurnState.READY)
      }
    }, 9000)
  }

  _iniciarWatchdogProcessing(turnId, sessionGen = null) {
    if (this.processingWatchdogTimer) {
      clearTimeout(this.processingWatchdogTimer)
      this.processingWatchdogTimer = null
    }
    const targetSessionGen = sessionGen ?? this.sessionGeneration
    this.processingWatchdogTimer = setTimeout(() => {
      if (!this._isTurnActive(turnId, targetSessionGen)) {
        return
      }
      if (this.state === VoiceTurnState.PROCESSING) {
        console.warn(`[VOICE-TURN] Watchdog PROCESSING expiró (15s) turnId=${turnId}. Reseteando a READY...`)
        if (this.currentSTT) this.currentSTT.cancel(turnId)
        this.isTranscribing = false
        this.turnFinalized = true
        this._setState(VoiceTurnState.READY)
      }
    }, 15000)
  }

  _limpiarTimers() {
    if (this.speechEndTimer) {
      clearTimeout(this.speechEndTimer)
      this.speechEndTimer = null
    }
    if (this.settlingTimer) {
      clearTimeout(this.settlingTimer)
      this.settlingTimer = null
    }
    if (this.operationalTimer) {
      clearTimeout(this.operationalTimer)
      this.operationalTimer = null
    }
    if (this.watchdogTimer) {
      clearTimeout(this.watchdogTimer)
      this.watchdogTimer = null
    }
    if (this.stopRequestTimer) {
      clearTimeout(this.stopRequestTimer)
      this.stopRequestTimer = null
    }
    if (this.processingWatchdogTimer) {
      clearTimeout(this.processingWatchdogTimer)
      this.processingWatchdogTimer = null
    }
  }
}
