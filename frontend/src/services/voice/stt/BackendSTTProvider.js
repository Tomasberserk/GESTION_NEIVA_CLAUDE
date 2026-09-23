import { SpeechInputProvider } from './SpeechInputProvider.js'
import { getSupportedAudioMime } from '../voiceCapabilities.js'

const BASE = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || '/api'

/**
 * Proveedor STT de contingencia que graba audio comprimido (Opus/WebM)
 * y lo envía al backend si la Web Speech API falla o no está disponible.
 */
export class BackendSTTProvider extends SpeechInputProvider {
  constructor() {
    super()
    this.mediaRecorder = null
    this.audioStream = null
    this.audioChunks = []
    this.isRecording = false
    this.mimeType = getSupportedAudioMime() || 'audio/webm'

    // VAD y Temporizadores
    this.audioContext = null
    this.analyser = null
    this.vadInterval = null
    this.silenceTimer = null
    this.maxTimer = null
    this.speechStarted = false
    this.isStarting = false
    this.turnId = null
    this.sessionGeneration = 0
    this.isPendingTranscription = false
  }

  isActive() {
    return !!(this.isStarting || this.isRecording || this.isPendingTranscription)
  }

  async start(turnId = null, sessionGeneration = 0) {
    if (typeof window === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      throw new Error('La grabación de audio no está disponible en este dispositivo.')
    }

    if (this.isRecording || this.isStarting || this.isPendingTranscription) {
      console.warn('[VOICE-LIFECYCLE] BackendSTTProvider.start() ignorado: ya está grabando, iniciando o transcribiendo.')
      return
    }

    this.turnId = turnId
    this.sessionGeneration = sessionGeneration
    this.isStarting = true
    this._stopRequested = false
    this.isPendingTranscription = false
    this._limpiarRecursos()
    this.audioChunks = []
    this.speechStarted = false

    console.log(`[VOICE-STT] BACKEND_START turnId=${this.turnId ?? ''}`)

    try {
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })

      // Guard contra parada solicitada mientras getUserMedia resolvía
      if (this._stopRequested || !this.isStarting) {
        console.warn('[BackendSTTProvider] stop fue solicitado durante arranque de micrófono. Cancelando.')
        this.isStarting = false
        this._limpiarRecursos()
        return
      }

      const options = this.mimeType ? { mimeType: this.mimeType } : {}
      this.mediaRecorder = new MediaRecorder(this.audioStream, options)

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data)
          console.log('[VOICE-STT] AUDIO_CHUNK', {
            turnId: this.turnId,
            size: event.data.size,
            totalChunks: this.audioChunks.length,
          })
        }
      }

      this.mediaRecorder.onstart = () => {
        this.isStarting = false
        this.isRecording = true
        console.log(`[VOICE-STT] BACKEND_RECORDING turnId=${this.turnId ?? ''}`)
        this._iniciarVAD()
      }

      this.mediaRecorder.onstop = async () => {
        const turnId = this.turnId
        const sessionGen = this.sessionGeneration
        this.isRecording = false
        this._limpiarTimers()

        const chunksCount = this.audioChunks.length
        if (chunksCount === 0) {
          console.warn('[VOICE-STT] AUDIO_READY: 0 chunks disponibles', { turnId })
          this.isPendingTranscription = false
          this._limpiarRecursos()
          if (this.onEnd) this.onEnd(turnId, sessionGen)
          return
        }

        this.isPendingTranscription = true
        const audioBlob = new Blob(this.audioChunks, { type: this.mimeType })
        this.audioChunks = []

        console.log('[VOICE-STT] AUDIO_READY', {
          turnId,
          chunks: chunksCount,
          blobSize: audioBlob.size,
          mimeType: audioBlob.type || this.mimeType,
        })

        try {
          const transcript = await this._enviarAudioAlBackend(audioBlob, turnId)
          console.log(`[VOICE-STT] BACKEND_TRANSCRIPT turnId=${turnId ?? ''} transcript="${transcript}"`)
          this.isPendingTranscription = false
          if (this.onTranscript) {
            this.onTranscript(transcript || '', true, turnId, sessionGen)
          }
        } catch (err) {
          this.isPendingTranscription = false
          console.error('[BackendSTTProvider] Error en transcripción:', err)
          if (this.onError) {
            this.onError({
              code: 'backend-stt-error',
              message: err.message || 'Error al transcribir audio en el servidor',
            }, turnId, sessionGen)
          }
        } finally {
          this.isPendingTranscription = false
          this._limpiarRecursos()
          if (this.onEnd) this.onEnd(turnId, sessionGen)
        }
      }

      // Iniciar captura con chunks cada 250ms
      this.mediaRecorder.start(250)

      // Hard cap de seguridad: 5.5 segundos máximo para comandos de voz de mostrador
      this.maxTimer = setTimeout(() => {
        console.info('[BackendSTTProvider] Límite máximo de turno (5.5s) alcanzado. Deteniendo...')
        this.stop(this.turnId)
        if (this.onRequestStop) {
          this.onRequestStop(this.turnId, this.sessionGeneration)
        }
      }, 5500)

      // Timer de seguridad si no hay habla en 4s
      this.initialSilenceTimer = setTimeout(() => {
        if (!this.speechStarted && this.isRecording) {
          console.log('[BackendSTTProvider] Sin habla detectada tras 4s. Deteniendo...')
          this.stop(this.turnId)
          if (this.onRequestStop) {
            this.onRequestStop(this.turnId, this.sessionGeneration)
          }
        }
      }, 4000)

    } catch (err) {
      this.isStarting = false
      this._limpiarRecursos()
      if (this.onError) {
        this.onError({
          code: err.name === 'NotAllowedError' ? 'not-allowed' : 'mic-init-error',
          message: err.message,
        }, this.turnId, this.sessionGeneration)
      }
    }
  }

  _iniciarVAD() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext
      if (!AudioCtx || !this.audioStream) return

      this.audioContext = new AudioCtx()
      if (this.audioContext.state === 'suspended') {
        this.audioContext.resume().catch(() => {})
      }

      const source = this.audioContext.createMediaStreamSource(this.audioStream)
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = 512
      source.connect(this.analyser)

      const buffer = new Float32Array(this.analyser.fftSize)
      const UMBRAL_VOZ = 0.02
      const TIEMPO_SILENCIO_MS = 950

      this.vadInterval = setInterval(() => {
        if (!this.isRecording || !this.analyser) return

        this.analyser.getFloatTimeDomainData(buffer)
        let sum = 0
        for (let i = 0; i < buffer.length; i++) {
          sum += buffer[i] * buffer[i]
        }
        const rms = Math.sqrt(sum / buffer.length)

        if (rms > UMBRAL_VOZ) {
          // Voz detectada
          if (!this.speechStarted) {
            this.speechStarted = true
            console.log('[BackendSTTProvider] VAD: Habla detectada (RMS:', rms.toFixed(4), ')')
            if (this.onSpeechStart) {
              this.onSpeechStart(this.turnId, this.sessionGeneration)
            }
          }
          // Reiniciar timer de silencio si el tendero continúa hablando
          if (this.silenceTimer) {
            clearTimeout(this.silenceTimer)
            this.silenceTimer = null
          }
        } else if (this.speechStarted && !this.silenceTimer) {
          // El tendero terminó de hablar y se mantiene silencio
          this.silenceTimer = setTimeout(() => {
            console.log('[BackendSTTProvider] VAD: Silencio natural detectado (950ms). Deteniendo...')
            this.stop(this.turnId)
            if (this.onRequestStop) {
              this.onRequestStop(this.turnId, this.sessionGeneration)
            }
          }, TIEMPO_SILENCIO_MS)
        }
      }, 100)

    } catch (e) {
      console.warn('[BackendSTTProvider] No se pudo inicializar AnalyserNode VAD, usando timers pasivos:', e)
    }
  }

  requestStop(turnId = null) {
    console.log(`[VOICE-STT] requestStop() invocado en BackendSTTProvider. turnId=${turnId ?? this.turnId ?? ''} isRecording=${this.isRecording}`)
    this._stopRequested = true
    this.stop(turnId)
  }

  stop(turnId = null) {
    this._stopRequested = true
    this.isStarting = false
    this._limpiarTimers()
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop()
      } catch (err) {
        console.warn('[BackendSTTProvider] Error al detener mediaRecorder:', err)
      }
    }
  }

  cancel(turnId = null) {
    this._stopRequested = true
    this.isStarting = false
    this.isPendingTranscription = false
    this._limpiarTimers()
    this.audioChunks = []
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop()
      } catch {
        // Ignorar
      }
    }
    this._limpiarRecursos()
  }

  _limpiarTimers() {
    if (this.vadInterval) {
      clearInterval(this.vadInterval)
      this.vadInterval = null
    }
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer)
      this.silenceTimer = null
    }
    if (this.maxTimer) {
      clearTimeout(this.maxTimer)
      this.maxTimer = null
    }
    if (this.initialSilenceTimer) {
      clearTimeout(this.initialSilenceTimer)
      this.initialSilenceTimer = null
    }
  }

  _limpiarRecursos() {
    this._limpiarTimers()

    if (this.audioContext) {
      try {
        this.audioContext.close().catch(() => {})
      } catch {}
      this.audioContext = null
      this.analyser = null
    }

    if (this.audioStream) {
      this.audioStream.getTracks().forEach((track) => {
        try { track.stop() } catch {}
      })
      this.audioStream = null
    }
  }

  async _enviarAudioAlBackend(blob, turnId = null) {
    const token = localStorage.getItem('access_token')
    const formData = new FormData()
    formData.append('audio', blob, 'voz.webm')

    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const res = await fetch(`${BASE}/agente/transcribir-audio`, {
      method: 'POST',
      headers,
      body: formData,
    })

    let data = null
    try {
      data = await res.json()
    } catch (_) {
      data = {}
    }

    console.log('[VOICE-STT] BACKEND_RESPONSE', {
      turnId: turnId ?? this.turnId,
      status: res.status,
      ok: res.ok,
      data,
    })

    if (!res.ok) {
      throw new Error(`Servidor devolvió código HTTP ${res.status}`)
    }

    return data?.texto || ''
  }
}
