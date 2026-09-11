import { WebSpeechProvider } from './stt/WebSpeechProvider.js'
import { BackendSTTProvider } from './stt/BackendSTTProvider.js'
import { SpeechSynthesisProvider } from './tts/SpeechSynthesisProvider.js'
import { voiceTelemetry } from './telemetry/voiceTelemetry.js'

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
 * VoiceTurnManager: Gestor desacoplado de turnos de audio y anti-eco.
 * Instrumentado con logs de diagnóstico paso a paso.
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
    this.stopRequested = false

    // Proveedores
    this.webSpeechProvider = new WebSpeechProvider()
    this.backendSTTProvider = new BackendSTTProvider()
    this.tts = new SpeechSynthesisProvider()

    // Política Android-First / Mobile-First:
    const isMobile = typeof navigator !== 'undefined' && /Android|iPhone|iPad|iPod/i.test(navigator.userAgent || '')
    if (isMobile) {
      console.info('[VOICE-DEBUG][VoiceTurnManager] Móvil detectado: asignando BackendSTTProvider como primario')
      this.activeProviderType = 'backend'
      this.currentSTT = this.backendSTTProvider
    } else {
      this.activeProviderType = 'webspeech'
      this.currentSTT = this.webSpeechProvider
    }

    // Timers
    this.speechEndTimer = null
    this.settlingTimer = null
    this.operationalTimer = null
    this.watchdogTimer = null
    this.stopRequestTimer = null

    this._bindProviders()
    console.log('[VOICE-DEBUG][VoiceTurnManager] Instanciación completa. Estado inicial:', this.state, 'Proveedor activo:', this.activeProviderType)
  }

  _invalidateCurrentTurn() {
    this.currentTurnId = ++this.turnCounter
    this.stopRequested = false
    this._limpiarTimers()
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
      provider.onSpeechStart = () => {
        const turnId = this.currentTurnId
        if (provider !== this.currentSTT) {
          console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED onSpeechStart de proveedor inactivo [${name}] turnId=${turnId}`)
          return
        }
        console.log(`[VOICE-STT] onstart turnId=${turnId}`)
        console.log(`[VOICE-TURN] SPEECH_DETECTED turnId=${turnId}`)
        if (this.state === VoiceTurnState.LISTENING) {
          this._setState(VoiceTurnState.SPEECH_DETECTED)
          voiceTelemetry.recordSpeechDetected()
        }
      }

      provider.onTranscript = (transcript, isFinal) => {
        const turnId = this.currentTurnId
        if (provider !== this.currentSTT) {
          console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED onTranscript de proveedor inactivo [${name}] turnId=${turnId}`)
          return
        }
        console.log(`[VOICE-STT] onresult turnId=${turnId} transcript="${transcript}" isFinal=${isFinal}`)
        this.interimTranscript = transcript
        if (this.onTranscriptUpdate) {
          this.onTranscriptUpdate(transcript, isFinal)
        }

        if (isFinal || (this.stopRequested && transcript.trim())) {
          console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${turnId} texto="${transcript}"`)
          if (this.stopRequestTimer) {
            clearTimeout(this.stopRequestTimer)
            this.stopRequestTimer = null
          }
          this.lastTranscript = transcript
          this._finalizarTurnoVocal(transcript, turnId)
        } else {
          this._reiniciarTimerSilencio(transcript, turnId)
        }
      }

      provider.onError = (err) => {
        const turnId = this.currentTurnId
        if (provider !== this.currentSTT) {
          console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED onError de proveedor inactivo [${name}] turnId=${turnId}`)
          return
        }
        console.error(`[VOICE-DEBUG][VoiceTurnManager][${name}] onError turnId=${turnId}:`, err)
        this._handleSTTError(err, turnId)
      }

      provider.onEnd = () => {
        const turnId = this.currentTurnId
        if (provider !== this.currentSTT) {
          console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED onEnd tardío turnId=${turnId} (proveedor actual es diferente)`)
          return
        }
        console.log(`[VOICE-STT] onend turnId=${turnId} interim="${this.interimTranscript}" stopRequested=${this.stopRequested}`)

        if (this.state === VoiceTurnState.LISTENING || this.state === VoiceTurnState.SPEECH_DETECTED) {
          if (this.interimTranscript && this.interimTranscript.trim()) {
            console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${turnId} texto="${this.interimTranscript}"`)
            this._finalizarTurnoVocal(this.interimTranscript, turnId)
          } else if (this.stopRequested) {
            console.log(`[VOICE-STT] onend tras stopRequested sin transcripción aún turnId=${turnId}, esperando timer...`)
          } else {
            console.warn(`[VOICE-TURN] onEnd sin transcripción turnId=${turnId} -> regresando a READY`)
            this._setState(VoiceTurnState.READY)
          }
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

  _reiniciarTimerSilencio(currentText, turnId) {
    if (this.speechEndTimer) {
      clearTimeout(this.speechEndTimer)
    }
    this.speechEndTimer = setTimeout(() => {
      if (turnId !== this.currentTurnId) {
        console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED speechEndTimer turnId=${turnId} currentTurnId=${this.currentTurnId}`)
        return
      }
      if (this.state === VoiceTurnState.SPEECH_DETECTED && currentText.trim()) {
        console.log(`[VOICE-TURN] Timer de silencio expiró turnId=${turnId}. Deteniendo...`)
        this.currentSTT.stop()
        this._finalizarTurnoVocal(currentText, turnId)
      }
    }, 1100)
  }

  _handleSTTError(err, turnId) {
    if (turnId && turnId !== this.currentTurnId) {
      console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED _handleSTTError turnId=${turnId} currentTurnId=${this.currentTurnId}`)
      return
    }
    console.warn(`[VOICE-DEBUG][VoiceTurnManager] _handleSTTError procesando turnId=${turnId}:`, err)
    voiceTelemetry.recordSTTFailure(err.code)

    // Fallback inmediato ante fallo de WebSpeech en cualquier plataforma (conservando el mismo turnId)
    if (this.activeProviderType === 'webspeech') {
      if (err.code === 'aborted' || err.code === 'audio-capture' || err.code === 'network' || err.code === 'start-error') {
        console.info(`[VOICE-STT] FALLBACK_BACKEND turnId=${turnId} por error WebSpeech (${err.code})`)
        this._conmutarABackendSTT(turnId)
        return
      }
    }

    if (err.code === 'not-allowed') {
      console.error('[VOICE-DEBUG][VoiceTurnManager] Error not-allowed (permiso denegado)')
      this._setState(VoiceTurnState.ERROR, { message: 'Permiso de micrófono denegado.' })
      return
    }

    if (err.code === 'no-speech') {
      console.log(`[VOICE-DEBUG][VoiceTurnManager] no-speech detectado turnId=${turnId} -> retornando a READY`)
      this._setState(VoiceTurnState.READY)
      return
    }

    this._setState(VoiceTurnState.READY)
  }

  async _conmutarABackendSTT(turnId) {
    if (turnId !== this.currentTurnId) {
      console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED _conmutarABackendSTT turnId=${turnId} currentTurnId=${this.currentTurnId}`)
      return
    }
    this.webSpeechProvider.cancel()
    this.activeProviderType = 'backend'
    this.currentSTT = this.backendSTTProvider
    this.stopRequested = false
    voiceTelemetry.recordFallbackUsed()

    try {
      console.log(`[VOICE-TURN] provider.start turnId=${turnId} (BackendSTT fallback)`)
      await this.backendSTTProvider.start()
    } catch (err) {
      if (turnId !== this.currentTurnId) return
      this._setState(VoiceTurnState.READY)
    }
  }

  /**
   * Inicia la sesión de voz tras el toque del usuario con saludo de bienvenida opcional.
   */
  async activarSesion(saludar = true) {
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
    console.log('[VOICE-DEBUG][VoiceTurnManager] iniciarEscucha() llamado. Estado actual:', this.state)

    // Guard de lifecycle estricto contra reentrancia
    if (
      this.state === VoiceTurnState.LISTENING ||
      this.state === VoiceTurnState.SPEECH_DETECTED ||
      this.currentSTT?.isListening ||
      this.currentSTT?.isStarting
    ) {
      console.warn('[VOICE-LIFECYCLE] iniciarEscucha ignorado: STT ya activo o iniciando', {
        state: this.state,
        provider: this.currentSTT?.constructor?.name,
        isListening: this.currentSTT?.isListening,
        isStarting: this.currentSTT?.isStarting,
      })
      return
    }

    if (this.state === VoiceTurnState.SPEAKING || this.state === VoiceTurnState.SETTLING) {
      console.warn(`[VOICE-DEBUG][VoiceTurnManager] iniciarEscucha() bloqueado por anti-eco (estado=${this.state})`)
      return
    }

    this._limpiarTimers()
    const turnId = ++this.turnCounter
    this.currentTurnId = turnId
    this.stopRequested = false
    this.interimTranscript = ''
    this._setState(VoiceTurnState.LISTENING)

    console.log(`[VOICE-TURN] START_TURN turnId=${turnId}`)
    console.log(`[VOICE-TURN] provider.start turnId=${turnId}`)
    this._iniciarWatchdogSTT(turnId)

    try {
      await this.currentSTT.start()
      console.log(`[VOICE-DEBUG][VoiceTurnManager] currentSTT.start() completado turnId=${turnId}`)
    } catch (err) {
      if (turnId !== this.currentTurnId) {
        console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED en start() exception turnId=${turnId} currentTurnId=${this.currentTurnId}`)
        return
      }
      console.error(`[VOICE-DEBUG][VoiceTurnManager] Excepción en currentSTT.start() turnId=${turnId}:`, err)
      this._handleSTTError({ code: err.name || 'start-error', message: err.message }, turnId)
    }
  }

  /**
   * Procesa la transcripción final y la envía al backend (Única ruta transaccional).
   */
  async _finalizarTurnoVocal(texto, turnId) {
    if (turnId && turnId !== this.currentTurnId) {
      console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED _finalizarTurnoVocal turnId=${turnId} currentTurnId=${this.currentTurnId}`)
      return
    }
    console.log(`[VOICE-DEBUG][VoiceTurnManager] _finalizarTurnoVocal() turnId=${this.currentTurnId} con texto:`, texto)
    if (!texto || !texto.trim()) {
      console.warn(`[VOICE-DEBUG][VoiceTurnManager] _finalizarTurnoVocal ignorado por texto vacío turnId=${this.currentTurnId}`)
      this._setState(VoiceTurnState.READY)
      return
    }

    this._limpiarTimers()
    this.currentSTT.stop()
    this._setState(VoiceTurnState.PROCESSING, { texto })

    console.log(`[VOICE-TURN] SEND_MESSAGE turnId=${this.currentTurnId} texto="${texto.trim()}"`)
    const t0 = Date.now()

    try {
      if (!this.onSendMessage) {
        throw new Error('No hay callback onSendMessage configurado.')
      }

      const res = await this.onSendMessage(texto.trim())
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
      console.error('[VOICE-DEBUG][VoiceTurnManager] Error al procesar mensaje con backend:', err)
      this.reproducirRespuesta(`Hubo un error: ${err.message}`, VoiceTurnState.READY)
    }
  }

  /**
   * Envía un mensaje manual (por ejemplo, al hacer clic en el botón de confirmación táctil).
   */
  async enviarMensajeManual(texto) {
    const turnId = this.currentTurnId
    console.log(`[VOICE-DEBUG][VoiceTurnManager] enviarMensajeManual llamado turnId=${turnId} con:`, texto)
    this.currentSTT.cancel()
    return this._finalizarTurnoVocal(texto, turnId)
  }

  /**
   * Reproduce la respuesta con TTS silenciando el micrófono.
   */
  reproducirRespuesta(texto, siguienteEstado = VoiceTurnState.READY) {
    const turnId = this.currentTurnId
    console.log(`[VOICE-TTS] START turnId=${turnId} texto="${texto}", siguienteEstado=${siguienteEstado}`)
    this._limpiarTimers()
    this.currentSTT.cancel()
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
        console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED settlingTimer turnId=${turnId} currentTurnId=${this.currentTurnId}`)
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
    console.log(`[VOICE-TURN] detenerYEnviar() invocado en estado: ${this.state} turnId=${turnId} stopRequested=${this.stopRequested}`)

    // Idempotencia: si no hay turno activo, o no está escuchando, o ya fue solicitado el stop: ignorar
    if (
      !turnId ||
      (this.state !== VoiceTurnState.LISTENING && this.state !== VoiceTurnState.SPEECH_DETECTED) ||
      this.stopRequested
    ) {
      console.warn(`[VOICE-TURN] detenerYEnviar ignorado (no activo o ya solicitado stop) turnId=${turnId}`)
      return
    }

    this.stopRequested = true
    console.log(`[VOICE-TURN] REQUEST_STOP turnId=${turnId}`)
    console.log(`[VOICE-STT] provider.stop turnId=${turnId}`)

    // Si ya tenemos texto interim acumulado, podemos finalizarlo de inmediato
    if (this.interimTranscript && this.interimTranscript.trim()) {
      console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${turnId} (usando interim existente: "${this.interimTranscript}")`)
      this.currentSTT.cancel()
      this._finalizarTurnoVocal(this.interimTranscript, turnId)
      return
    }

    // Solicitar stop al provider
    if (typeof this.currentSTT.requestStop === 'function') {
      this.currentSTT.requestStop()
    } else {
      this.currentSTT.stop()
    }

    // Si es WebSpeech, esperar hasta 750ms a que entregue onresult antes de declarar que no hubo resultado
    if (this.activeProviderType === 'webspeech') {
      if (this.stopRequestTimer) clearTimeout(this.stopRequestTimer)
      this.stopRequestTimer = setTimeout(() => {
        if (turnId !== this.currentTurnId) {
          console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED stopRequestTimer turnId=${turnId} currentTurnId=${this.currentTurnId}`)
          return
        }
        if (this.interimTranscript && this.interimTranscript.trim()) {
          console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${turnId} texto="${this.interimTranscript}"`)
          this._finalizarTurnoVocal(this.interimTranscript, turnId)
        } else {
          console.warn(`[VOICE-STT] NO_FINAL_RESULT turnId=${turnId}`)
          console.info(`[VOICE-STT] FALLBACK_BACKEND turnId=${turnId}`)
          this._conmutarABackendSTT(turnId)
        }
      }, 750)
    }
  }

  /**
   * Watchdog STT de seguridad (9s) asociado exclusivamente al turnId activo.
   * NUNCA ejecuta start() indiscriminadamente.
   */
  _iniciarWatchdogSTT(turnId) {
    if (this.watchdogTimer) {
      clearTimeout(this.watchdogTimer)
    }
    console.log(`[VOICE-DEBUG][VoiceTurnManager] Programando watchdog STT (9s) turnId=${turnId}`)
    this.watchdogTimer = setTimeout(() => {
      if (turnId !== this.currentTurnId) {
        console.warn(`[VOICE-TURN] STALE_CALLBACK_IGNORED watchdog expiró para turnId=${turnId} (currentTurnId=${this.currentTurnId})`)
        return
      }
      console.warn(`[VOICE-DEBUG][VoiceTurnManager] Watchdog STT expiró (9s) turnId=${turnId}. Estado: ${this.state}`)

      // Watchdog de recuperación: NUNCA llama a start(). Solo cierra de forma segura si el turno se colgó.
      if (this.state === VoiceTurnState.LISTENING || this.state === VoiceTurnState.SPEECH_DETECTED) {
        this.currentSTT.stop()
        if (this.interimTranscript && this.interimTranscript.trim()) {
          console.log(`[VOICE-TURN] TRANSCRIPT_FINAL turnId=${turnId} (watchdog)`)
          this._finalizarTurnoVocal(this.interimTranscript, turnId)
        } else {
          console.warn(`[VOICE-TURN] Watchdog reiniciando a READY turnId=${turnId}`)
          this._setState(VoiceTurnState.READY)
        }
      }
    }, 9000)
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
  }
}
