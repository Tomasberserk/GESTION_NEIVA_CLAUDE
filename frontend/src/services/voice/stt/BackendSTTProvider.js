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
  }

  async start() {
    if (typeof window === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      throw new Error('La grabación de audio no está disponible en este dispositivo.')
    }

    if (this.isRecording || this.isStarting) {
      console.warn('[VOICE-LIFECYCLE] BackendSTTProvider.start() ignorado: ya está grabando o iniciando.')
      return
    }

    this.isStarting = true
    this._limpiarRecursos()
    this.audioChunks = []
    this.speechStarted = false

    try {
      this.audioStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })

      const options = this.mimeType ? { mimeType: this.mimeType } : {}
      this.mediaRecorder = new MediaRecorder(this.audioStream, options)

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data)
        }
      }

      this.mediaRecorder.onstart = () => {
        this.isStarting = false
        this.isRecording = true
        console.log('[VOICE-STT] BACKEND_RECORDING')
        this._iniciarVAD()
      }

      this.mediaRecorder.onstop = async () => {
        this.isRecording = false
        this._limpiarRecursos()

        if (this.audioChunks.length === 0) {
          if (this.onEnd) this.onEnd()
          return
        }

        const audioBlob = new Blob(this.audioChunks, { type: this.mimeType })
        this.audioChunks = []

        try {
          const transcript = await this._enviarAudioAlBackend(audioBlob)
          console.log(`[VOICE-STT] BACKEND_TRANSCRIPT transcript="${transcript}"`)
          if (transcript && this.onTranscript) {
            this.onTranscript(transcript, true)
          }
        } catch (err) {
          console.error('[BackendSTTProvider] Error en transcripción:', err)
          if (this.onError) {
            this.onError({
              code: 'backend-stt-error',
              message: err.message || 'Error al transcribir audio en el servidor',
            })
          }
        } finally {
          if (this.onEnd) this.onEnd()
        }
      }

      // Iniciar captura con chunks cada 250ms
      this.mediaRecorder.start(250)

      // Hard cap de seguridad: 8 segundos máximo para no colgarse nunca
      this.maxTimer = setTimeout(() => {
        console.info('[BackendSTTProvider] Límite máximo de turno (8s) alcanzado. Deteniendo...')
        this.stop()
      }, 8000)

    } catch (err) {
      this.isStarting = false
      this._limpiarRecursos()
      if (this.onError) {
        this.onError({
          code: err.name === 'NotAllowedError' ? 'not-allowed' : 'mic-init-error',
          message: err.message,
        })
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
      const TIEMPO_SILENCIO_MS = 1600

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
              this.onSpeechStart()
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
            console.log('[BackendSTTProvider] VAD: Silencio cómodo detectado (1.6s). Deteniendo...')
            this.stop()
          }, TIEMPO_SILENCIO_MS)
        }
      }, 100)

    } catch (e) {
      console.warn('[BackendSTTProvider] No se pudo inicializar AnalyserNode VAD, usando timers pasivos:', e)
    }
  }

  requestStop() {
    console.log('[VOICE-STT] requestStop() invocado en BackendSTTProvider. isRecording:', this.isRecording)
    this.stop()
  }

  stop() {
    this.isStarting = false
    this._limpiarTimers()
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop()
      } catch {
        // Ignorar
      }
    }
  }

  cancel() {
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

  async _enviarAudioAlBackend(blob) {
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

    if (!res.ok) {
      throw new Error(`Servidor devolvió código HTTP ${res.status}`)
    }

    const data = await res.json()
    return data.texto || ''
  }
}
