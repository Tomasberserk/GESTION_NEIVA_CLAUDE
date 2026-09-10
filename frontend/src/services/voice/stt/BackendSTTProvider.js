import { SpeechInputProvider } from './SpeechInputProvider'
import { getSupportedAudioMime } from '../voiceCapabilities'

const BASE = import.meta.env.VITE_API_URL || '/api'

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
  }

  async start() {
    if (typeof window === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      throw new Error('La grabación de audio no está disponible en este dispositivo.')
    }

    this.audioChunks = []
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
        this.isRecording = true
        if (this.onSpeechStart) {
          this.onSpeechStart()
        }
      }

      this.mediaRecorder.onstop = async () => {
        this.isRecording = false
        this._liberarMicrofono()

        if (this.audioChunks.length === 0) {
          if (this.onEnd) this.onEnd()
          return
        }

        const audioBlob = new Blob(this.audioChunks, { type: this.mimeType })
        this.audioChunks = []

        try {
          const transcript = await this._enviarAudioAlBackend(audioBlob)
          if (transcript && this.onTranscript) {
            this.onTranscript(transcript, true)
          }
        } catch (err) {
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

      this.mediaRecorder.start()
    } catch (err) {
      this._liberarMicrofono()
      if (this.onError) {
        this.onError({
          code: err.name === 'NotAllowedError' ? 'not-allowed' : 'mic-init-error',
          message: err.message,
        })
      }
    }
  }

  stop() {
    if (this.mediaRecorder && this.isRecording) {
      try {
        this.mediaRecorder.stop()
      } catch {
        // Ignorar
      }
    }
  }

  cancel() {
    this.audioChunks = []
    if (this.mediaRecorder && this.isRecording) {
      try {
        this.mediaRecorder.stop()
      } catch {
        // Ignorar
      }
    }
    this._liberarMicrofono()
  }

  _liberarMicrofono() {
    if (this.audioStream) {
      this.audioStream.getTracks().forEach((track) => track.stop())
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
