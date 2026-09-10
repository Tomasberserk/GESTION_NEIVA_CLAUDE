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
 * NO conoce reglas de negocio (ventas, precios, base de datos).
 */
export class VoiceTurnManager {
  constructor(options = {}) {
    this.onStateChange = options.onStateChange || null
    this.onTranscriptUpdate = options.onTranscriptUpdate || null
    this.onAgentResponse = options.onAgentResponse || null
    this.onSendMessage = options.onSendMessage || null // (texto) => Promise<{ respuesta: string, estado: string, ... }>

    this.state = VoiceTurnState.IDLE
    this.lastTranscript = ''
    this.interimTranscript = ''
    this.activeProviderType = 'webspeech'

    // Proveedores
    this.webSpeechProvider = new WebSpeechProvider()
    this.backendSTTProvider = new BackendSTTProvider()
    this.currentSTT = this.webSpeechProvider
    this.tts = new SpeechSynthesisProvider()

    // Timers
    this.speechEndTimer = null
    this.settlingTimer = null
    this.operationalTimer = null

    this._bindProviders()
  }

  _setState(newState, data = {}) {
    if (this.state === newState) return
    this.state = newState
    if (this.onStateChange) {
      this.onStateChange(newState, data)
    }
  }

  _bindProviders() {
    // Configurar STT WebSpeech
    const setupSTT = (provider) => {
      provider.onSpeechStart = () => {
        if (this.state === VoiceTurnState.LISTENING) {
          this._setState(VoiceTurnState.SPEECH_DETECTED)
          voiceTelemetry.recordSpeechDetected()
        }
      }

      provider.onTranscript = (transcript, isFinal) => {
        this.interimTranscript = transcript
        if (this.onTranscriptUpdate) {
          this.onTranscriptUpdate(transcript, isFinal)
        }

        if (isFinal) {
          this.lastTranscript = transcript
          this._finalizarTurnoVocal(transcript)
        } else {
          // Timer de silencio (~1000 ms) como política de turno
          this._reiniciarTimerSilencio(transcript)
        }
      }

      provider.onError = (err) => {
        this._handleSTTError(err)
      }

      provider.onEnd = () => {
        if (this.state === VoiceTurnState.LISTENING || this.state === VoiceTurnState.SPEECH_DETECTED) {
          // Si el proveedor terminó y teníamos texto pendiente
          if (this.interimTranscript.trim()) {
            this._finalizarTurnoVocal(this.interimTranscript)
          } else {
            this._setState(VoiceTurnState.READY)
          }
        }
      }
    }

    setupSTT(this.webSpeechProvider)
    setupSTT(this.backendSTTProvider)

    // Configurar TTS
    this.tts.onStart = () => {
      this._setState(VoiceTurnState.SPEAKING)
    }

    this.tts.onEnd = () => {
      this._iniciarVentanaSettling()
    }

    this.tts.onError = (err) => {
      console.warn('TTS Warning:', err)
      this._iniciarVentanaSettling()
    }
  }

  _reiniciarTimerSilencio(currentText) {
    if (this.speechEndTimer) {
      clearTimeout(this.speechEndTimer)
    }
    this.speechEndTimer = setTimeout(() => {
      if (this.state === VoiceTurnState.SPEECH_DETECTED && currentText.trim()) {
        this.currentSTT.stop()
        this._finalizarTurnoVocal(currentText)
      }
    }, 1100)
  }

  _handleSTTError(err) {
    voiceTelemetry.recordSTTFailure(err.code)

    // Fallback a Backend STT si falla por red
    if (err.code === 'network' && this.activeProviderType === 'webspeech') {
      console.info('Cambiando a BackendSTTProvider por error de red en WebSpeech')
      this.activeProviderType = 'backend'
      this.currentSTT = this.backendSTTProvider
      voiceTelemetry.recordFallbackUsed()
      this.iniciarEscucha()
      return
    }

    if (err.code === 'not-allowed') {
      this._setState(VoiceTurnState.ERROR, { message: 'Permiso de micrófono denegado.' })
      return
    }

    if (err.code === 'no-speech') {
      // Silencio normal; retornar a READY sin alertar
      this._setState(VoiceTurnState.READY)
      return
    }

    this._setState(VoiceTurnState.READY)
  }

  /**
   * Inicia la sesión de voz tras el toque del usuario (gesto de activación móvil).
   */
  async activarSesion() {
    this._limpiarTimers()
    this.tts.cancel()
    this.currentSTT.cancel()
    voiceTelemetry.recordSessionStart()
    this._setState(VoiceTurnState.READY)
    return this.iniciarEscucha()
  }

  /**
   * Abre el micrófono para un turno discreto.
   */
  async iniciarEscucha() {
    // Regla anti-eco: jamás escuchar si TTS está hablando o settling
    if (this.state === VoiceTurnState.SPEAKING || this.state === VoiceTurnState.SETTLING) {
      return
    }

    this._limpiarTimers()
    this.interimTranscript = ''
    this._setState(VoiceTurnState.LISTENING)

    try {
      await this.currentSTT.start()
    } catch (err) {
      this._handleSTTError({ code: err.name || 'start-error', message: err.message })
    }
  }

  /**
   * Procesa la transcripción final y la envía al backend.
   */
  async _finalizarTurnoVocal(texto) {
    if (!texto || !texto.trim()) {
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

      const res = await this.onSendMessage(texto.trim())
      const latency = Date.now() - t0
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
      this.reproducirRespuesta(`Hubo un error: ${err.message}`, VoiceTurnState.READY)
    }
  }

  /**
   * Envía un mensaje manual (por ejemplo, al hacer clic en el botón de confirmación táctil).
   */
  async enviarMensajeManual(texto) {
    this.currentSTT.cancel()
    return this._finalizarTurnoVocal(texto)
  }

  /**
   * Reproduce la respuesta con TTS silenciando el micrófono.
   */
  reproducirRespuesta(texto, siguienteEstado = VoiceTurnState.READY) {
    this._limpiarTimers()
    this.currentSTT.cancel() // Micrófono muteado estrictamente
    this._nextStateAfterSettling = siguienteEstado
    this._setState(VoiceTurnState.SPEAKING)
    this.tts.speak(texto)
  }

  /**
   * Ventana de reposo acústico (250 ms) para absorber ecos de altavoces.
   */
  _iniciarVentanaSettling() {
    this._setState(VoiceTurnState.SETTLING)
    this.settlingTimer = setTimeout(() => {
      const targetState = this._nextStateAfterSettling || VoiceTurnState.READY
      this._setState(targetState)

      // Si el estado siguiente es READY o CONFIRMING, reactivar la escucha del siguiente turno
      if (targetState === VoiceTurnState.READY || targetState === VoiceTurnState.CONFIRMING) {
        this.iniciarEscucha()
      }
    }, 250)
  }

  detenerSesion() {
    this._limpiarTimers()
    this.tts.cancel()
    this.currentSTT.cancel()
    this._setState(VoiceTurnState.IDLE)
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
  }
}
