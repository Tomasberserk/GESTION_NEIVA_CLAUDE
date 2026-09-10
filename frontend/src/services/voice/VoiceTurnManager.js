import { WebSpeechProvider } from './stt/WebSpeechProvider'
import { BackendSTTProvider } from './stt/BackendSTTProvider'
import { SpeechSynthesisProvider } from './tts/SpeechSynthesisProvider'
import { voiceTelemetry } from './telemetry/voiceTelemetry'

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

    this._bindProviders()
    console.log('[VOICE-DEBUG][VoiceTurnManager] Instanciación completa. Estado inicial:', this.state, 'Proveedor activo:', this.activeProviderType)
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
        // Anti-carrera: ignorar eventos si el proveedor ya no es el activo
        if (provider !== this.currentSTT) return
        console.log(`[VOICE-DEBUG][VoiceTurnManager][${name}] onSpeechStart disparado. Estado actual: ${this.state}`)
        if (this.state === VoiceTurnState.LISTENING) {
          this._setState(VoiceTurnState.SPEECH_DETECTED)
          voiceTelemetry.recordSpeechDetected()
        } else {
          console.warn(`[VOICE-DEBUG][VoiceTurnManager][${name}] onSpeechStart ignorado porque estado no es LISTENING (es ${this.state})`)
        }
      }

      provider.onTranscript = (transcript, isFinal) => {
        // Anti-carrera: ignorar eventos si el proveedor ya no es el activo
        if (provider !== this.currentSTT) return
        console.log(`[VOICE-DEBUG][VoiceTurnManager][${name}] onTranscript: "${transcript}", isFinal: ${isFinal}, estado: ${this.state}`)
        this.interimTranscript = transcript
        if (this.onTranscriptUpdate) {
          this.onTranscriptUpdate(transcript, isFinal)
        }

        if (isFinal) {
          this.lastTranscript = transcript
          this._finalizarTurnoVocal(transcript)
        } else {
          this._reiniciarTimerSilencio(transcript)
        }
      }

      provider.onError = (err) => {
        // Anti-carrera: ignorar errores huérfanos de proveedores inactivos
        if (provider !== this.currentSTT) return
        console.error(`[VOICE-DEBUG][VoiceTurnManager][${name}] onError recibido:`, err)
        this._handleSTTError(err)
      }

      provider.onEnd = () => {
        // Anti-carrera: si llega un onEnd tardío de un proveedor anterior, descartarlo
        if (provider !== this.currentSTT) {
          console.warn(`[VOICE-DEBUG][VoiceTurnManager][${name}] onEnd tardío descartado (proveedor actual es diferente)`)
          return
        }
        console.log(`[VOICE-DEBUG][VoiceTurnManager][${name}] onEnd recibido. Estado actual: ${this.state}, interim: "${this.interimTranscript}"`)
        if (this.state === VoiceTurnState.LISTENING || this.state === VoiceTurnState.SPEECH_DETECTED) {
          if (this.interimTranscript.trim()) {
            console.log(`[VOICE-DEBUG][VoiceTurnManager][${name}] onEnd con transcripción pendiente -> finalizando turno`)
            this._finalizarTurnoVocal(this.interimTranscript)
          } else {
            console.warn(`[VOICE-DEBUG][VoiceTurnManager][${name}] onEnd sin transcripción -> regresando a READY`)
            this._setState(VoiceTurnState.READY)
          }
        }
      }
    }

    setupSTT(this.webSpeechProvider, 'WebSpeech')
    setupSTT(this.backendSTTProvider, 'BackendSTT')

    // Configurar TTS
    this.tts.onStart = () => {
      console.log('[VOICE-DEBUG][VoiceTurnManager] TTS onStart -> transicionando a SPEAKING')
      this._setState(VoiceTurnState.SPEAKING)
    }

    this.tts.onEnd = () => {
      console.log('[VOICE-DEBUG][VoiceTurnManager] TTS onEnd -> iniciando settling')
      this._iniciarVentanaSettling()
    }

    this.tts.onError = (err) => {
      console.warn('[VOICE-DEBUG][VoiceTurnManager] TTS onError:', err)
      this._iniciarVentanaSettling()
    }
  }

  _reiniciarTimerSilencio(currentText) {
    if (this.speechEndTimer) {
      clearTimeout(this.speechEndTimer)
    }
    console.log('[VOICE-DEBUG][VoiceTurnManager] Programando timer de silencio (1100ms) para:', currentText)
    this.speechEndTimer = setTimeout(() => {
      console.log(`[VOICE-DEBUG][VoiceTurnManager] Timer de silencio expiró. Estado: ${this.state}, texto: "${currentText}"`)
      if (this.state === VoiceTurnState.SPEECH_DETECTED && currentText.trim()) {
        this.currentSTT.stop()
        this._finalizarTurnoVocal(currentText)
      }
    }, 1100)
  }

  _handleSTTError(err) {
    console.warn('[VOICE-DEBUG][VoiceTurnManager] _handleSTTError procesando:', err)
    voiceTelemetry.recordSTTFailure(err.code)

    // Fallback inmediato ante fallo de WebSpeech en cualquier plataforma
    if (this.activeProviderType === 'webspeech') {
      if (err.code === 'aborted' || err.code === 'audio-capture' || err.code === 'network' || err.code === 'start-error') {
        console.info(`[VOICE-DEBUG][VoiceTurnManager] Error en WebSpeech (${err.code}). Conmutando inmediatamente a BackendSTTProvider`)
        this.webSpeechProvider.cancel()
        this.activeProviderType = 'backend'
        this.currentSTT = this.backendSTTProvider
        this.sessionGeneration++
        voiceTelemetry.recordFallbackUsed()
        this.iniciarEscucha()
        return
      }
    }

    if (err.code === 'not-allowed') {
      console.error('[VOICE-DEBUG][VoiceTurnManager] Error not-allowed (permiso de micrófono denegado)')
      this._setState(VoiceTurnState.ERROR, { message: 'Permiso de micrófono denegado.' })
      return
    }

    if (err.code === 'no-speech') {
      console.log('[VOICE-DEBUG][VoiceTurnManager] no-speech detectado -> retornando a READY')
      this._setState(VoiceTurnState.READY)
      return
    }

    this._setState(VoiceTurnState.READY)
  }

  /**
   * Inicia la sesión de voz tras el toque del usuario con saludo de bienvenida opcional.
   */
  async activarSesion(saludar = true) {
    console.log('[VOICE-DEBUG][VoiceTurnManager] activarSesion() llamado. Estado antes:', this.state)
    this._limpiarTimers()
    this.sessionGeneration++
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
   * Abre el micrófono para un turno discreto.
   */
  async iniciarEscucha() {
    console.log('[VOICE-DEBUG][VoiceTurnManager] iniciarEscucha() llamado. Estado actual:', this.state)
    if (this.state === VoiceTurnState.SPEAKING || this.state === VoiceTurnState.SETTLING) {
      console.warn(`[VOICE-DEBUG][VoiceTurnManager] iniciarEscucha() bloqueado por anti-eco (estado=${this.state})`)
      return
    }

    this._limpiarTimers()
    this.interimTranscript = ''
    this._setState(VoiceTurnState.LISTENING)
    this._iniciarWatchdogSTT()

    try {
      console.log('[VOICE-DEBUG][VoiceTurnManager] Invocando this.currentSTT.start()...')
      await this.currentSTT.start()
      console.log('[VOICE-DEBUG][VoiceTurnManager] this.currentSTT.start() completado sin excepción.')
    } catch (err) {
      console.error('[VOICE-DEBUG][VoiceTurnManager] Excepción en currentSTT.start():', err)
      this._handleSTTError({ code: err.name || 'start-error', message: err.message })
    }
  }

  /**
   * Procesa la transcripción final y la envía al backend.
   */
  async _finalizarTurnoVocal(texto) {
    console.log('[VOICE-DEBUG][VoiceTurnManager] _finalizarTurnoVocal() con texto:', texto)
    if (!texto || !texto.trim()) {
      console.warn('[VOICE-DEBUG][VoiceTurnManager] _finalizarTurnoVocal ignorado por texto vacío')
      this._setState(VoiceTurnState.READY)
      return
    }

    this._limpiarTimers()
    this.currentSTT.stop()
    this._setState(VoiceTurnState.PROCESSING, { texto })

    const t0 = Date.now()

    try {
      if (!this.onSendMessage) {
        throw new Error('No hay callback onSendMessage configurado.')
      }

      console.log('[VOICE-DEBUG][VoiceTurnManager] Enviando texto al backend mediante onSendMessage...')
      const res = await this.onSendMessage(texto.trim())
      const latency = Date.now() - t0
      console.log(`[VOICE-DEBUG][VoiceTurnManager] Respuesta recibida en ${latency}ms:`, res)
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
    console.log('[VOICE-DEBUG][VoiceTurnManager] enviarMensajeManual llamado con:', texto)
    this.currentSTT.cancel()
    return this._finalizarTurnoVocal(texto)
  }

  /**
   * Reproduce la respuesta con TTS silenciando el micrófono.
   */
  reproducirRespuesta(texto, siguienteEstado = VoiceTurnState.READY) {
    console.log(`[VOICE-DEBUG][VoiceTurnManager] reproducirRespuesta(): "${texto}", siguienteEstado=${siguienteEstado}`)
    this._limpiarTimers()
    this.currentSTT.cancel()
    this._nextStateAfterSettling = siguienteEstado
    this._setState(VoiceTurnState.SPEAKING)
    this.tts.speak(texto)
  }

  /**
   * Ventana de reposo acústico (250 ms) para absorber ecos de altavoces.
   */
  _iniciarVentanaSettling() {
    console.log('[VOICE-DEBUG][VoiceTurnManager] _iniciarVentanaSettling() iniciada (250ms)')
    this._setState(VoiceTurnState.SETTLING)
    this.settlingTimer = setTimeout(() => {
      const targetState = this._nextStateAfterSettling || VoiceTurnState.READY
      console.log(`[VOICE-DEBUG][VoiceTurnManager] Ventana de settling finalizada. Transicionando a: ${targetState}`)
      this._setState(targetState)

      if (targetState === VoiceTurnState.READY || targetState === VoiceTurnState.CONFIRMING) {
        console.log('[VOICE-DEBUG][VoiceTurnManager] Reanudando escucha tras settling...')
        this.iniciarEscucha()
      }
    }, 250)
  }

  detenerSesion() {
    console.log('[VOICE-DEBUG][VoiceTurnManager] detenerSesion() llamado')
    this._limpiarTimers()
    this.tts.cancel()
    this.currentSTT.cancel()
    this._setState(VoiceTurnState.IDLE)
  }

  /**
   * Detiene inmediatamente la escucha actual y envía el audio/transcripción acumulada (Tap-to-send).
   */
  detenerYEnviar() {
    console.log(`[VOICE-DEBUG][VoiceTurnManager] detenerYEnviar() manual invocado en estado: ${this.state}`)
    if (this.state === VoiceTurnState.LISTENING || this.state === VoiceTurnState.SPEECH_DETECTED) {
      this.currentSTT.stop()
    }
  }

  _iniciarWatchdogSTT() {
    if (this.watchdogTimer) {
      clearTimeout(this.watchdogTimer)
    }
    console.log('[VOICE-DEBUG][VoiceTurnManager] Programando watchdog STT de seguridad (9s)...')
    this.watchdogTimer = setTimeout(() => {
      if (this.state === VoiceTurnState.LISTENING || this.state === VoiceTurnState.SPEECH_DETECTED) {
        console.warn(`[VOICE-DEBUG][VoiceTurnManager] Watchdog STT expiró (9s sin respuesta). Estado actual: ${this.state}`)
        this.currentSTT.stop()
        if (this.interimTranscript && this.interimTranscript.trim()) {
          console.log('[VOICE-DEBUG][VoiceTurnManager] Watchdog finalizando con interimTranscript existente:', this.interimTranscript)
          this._finalizarTurnoVocal(this.interimTranscript)
        } else {
          console.warn('[VOICE-DEBUG][VoiceTurnManager] Watchdog reiniciando estado a READY')
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
  }
}
