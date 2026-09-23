import { SpeechInputProvider } from './SpeechInputProvider.js'
import { getSupportedAudioMime } from '../voiceCapabilities.js'

const BASE = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || '/api'

/**
 * Proveedor STT de contingencia que graba audio comprimido (Opus/WebM)
 * y lo envía al backend si la Web Speech API falla o no está disponible.
 * Blindado con aislamiento estricto de streams, AbortController para HTTP y
 * protección contra callbacks tardíos o destructivos de turnos anteriores.
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
    this.initialSilenceTimer = null
    this.speechStarted = false
    this.isStarting = false
    this.turnId = null
    this.sessionGeneration = 0
    this.isPendingTranscription = false
    this._stopRequested = false

    // Identidad de instancia y cancelación de red
    this._instanceCounter = 0
    this.instanceId = 'be_0'
    this.abortController = null
  }

  isActive() {
    return !!(this.isStarting || this.isRecording || this.isPendingTranscription)
  }

  async start(turnId = null, sessionGeneration = 0, providerGeneration = 0) {
    if (typeof window === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      throw new Error('La grabación de audio no está disponible en este dispositivo.')
    }

    if (this.isRecording || this.isStarting || this.isPendingTranscription) {
      console.warn('[VOICE-LIFECYCLE] BackendSTTProvider.start() ignorado: ya está grabando, iniciando o transcribiendo.')
      return
    }

    const instanceId = 'be_' + (++this._instanceCounter)
    this.instanceId = instanceId
    this.turnId = turnId
    this.sessionGeneration = sessionGeneration
    this.generation = providerGeneration
    this.isStarting = true
    this._stopRequested = false
    this.isPendingTranscription = false
    this._limpiarRecursos()
    this.audioChunks = []
    this.speechStarted = false

    // Abortar cualquier petición HTTP previa en vuelo
    if (this.abortController) {
      try { this.abortController.abort() } catch (_) {}
    }
    this.abortController = typeof AbortController !== 'undefined' ? new AbortController() : null

    console.log(`[VOICE-STT] BACKEND_START turnId=${this.turnId ?? ''} gen=${providerGeneration} instance=${instanceId}`)

    let stream = null
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })

      // Guard contra turno cancelado o sustituido mientras el usuario otorgaba permiso o getUserMedia resolvía
      if (this._stopRequested || this.instanceId !== instanceId || this.turnId !== turnId) {
        console.warn(`[BackendSTTProvider][${instanceId}] start fue cancelado/sustituido durante getUserMedia. Liberando stream.`)
        this.isStarting = false
        if (stream) {
          stream.getTracks().forEach((t) => { try { t.stop() } catch (_) {} })
        }
        return
      }

      this.audioStream = stream
      const localStream = stream
      const options = this.mimeType ? { mimeType: this.mimeType } : {}
      const recorder = new MediaRecorder(localStream, options)
      this.mediaRecorder = recorder

      recorder.ondataavailable = (event) => {
        if (this.instanceId !== instanceId) return
        if (event.data && event.data.size > 0) {
          this.audioChunks.push(event.data)
          console.log('[VOICE-STT] AUDIO_CHUNK', {
            turnId: this.turnId,
            instanceId,
            size: event.data.size,
            totalChunks: this.audioChunks.length,
          })
        }
      }

      recorder.onstart = () => {
        if (this.instanceId !== instanceId) return
        this.isStarting = false
        this.isRecording = true
        console.log(`[VOICE-STT] BACKEND_RECORDING turnId=${this.turnId ?? ''} instance=${instanceId}`)
        this._iniciarVAD(instanceId, localStream)
      }

      recorder.onstop = async () => {
        const localTurnId = turnId
        const localSessionGen = sessionGeneration
        const localProviderGen = providerGeneration
        const localInstanceId = instanceId

        this.isRecording = false
        this._limpiarTimers()

        // Si fue cancelado antes de tiempo o la instancia ya fue sustituida
        if (this._stopRequested && this.audioChunks.length === 0) {
          console.log(`[VOICE-STT] onstop de instancia cancelada/vaciada ${localInstanceId}`)
          this.isPendingTranscription = false
          if (localStream === this.audioStream) this._limpiarRecursos()
          else localStream.getTracks().forEach((t) => { try { t.stop() } catch (_) {} })
          return
        }

        const chunksCount = this.audioChunks.length
        if (chunksCount === 0 || this.instanceId !== localInstanceId) {
          console.warn('[VOICE-STT] AUDIO_READY: 0 chunks disponibles o instancia desfasada', {
            turnId: localTurnId,
            instanceId: localInstanceId,
            activeInstanceId: this.instanceId,
          })
          this.isPendingTranscription = false
          if (localStream === this.audioStream) this._limpiarRecursos()
          else localStream.getTracks().forEach((t) => { try { t.stop() } catch (_) {} })

          if (this.instanceId === localInstanceId && this.onEnd) {
            this.onEnd(localTurnId, localSessionGen, localProviderGen, localInstanceId)
          }
          return
        }

        this.isPendingTranscription = true
        const audioBlob = new Blob(this.audioChunks, { type: this.mimeType })
        this.audioChunks = []

        console.log('[VOICE-STT] AUDIO_READY', {
          turnId: localTurnId,
          instanceId: localInstanceId,
          chunks: chunksCount,
          blobSize: audioBlob.size,
          mimeType: audioBlob.type || this.mimeType,
        })

        try {
          const transcript = await this._enviarAudioAlBackend(audioBlob, localTurnId, this.abortController?.signal)

          // Guard estricto contra turnos desfasados tras completar la petición HTTP
          if (
            this.instanceId !== localInstanceId ||
            this.turnId !== localTurnId ||
            this.sessionGeneration !== localSessionGen ||
            this.generation !== localProviderGen
          ) {
            console.warn(`[VOICE-LIFECYCLE] Transcripción tardía de BackendSTT descartada (turno=${localTurnId}, activo=${this.turnId})`)
            return
          }

          console.log(`[VOICE-STT] BACKEND_TRANSCRIPT turnId=${localTurnId ?? ''} transcript="${transcript}"`)
          this.isPendingTranscription = false
          if (this.onTranscript) {
            this.onTranscript(transcript || '', true, localTurnId, localSessionGen, localProviderGen, localInstanceId)
          }
        } catch (err) {
          if (err.name === 'AbortError' || this.instanceId !== localInstanceId || this.turnId !== localTurnId) {
            console.log(`[VOICE-LIFECYCLE] Petición de audio abortada o turno desfasado (${localTurnId}): ${err.message}`)
            return
          }
          this.isPendingTranscription = false
          console.error('[BackendSTTProvider] Error en transcripción:', err)
          if (this.onError) {
            this.onError({
              code: 'backend-stt-error',
              message: err.message || 'Error al transcribir audio en el servidor',
            }, localTurnId, localSessionGen, localProviderGen, localInstanceId)
          }
        } finally {
          this.isPendingTranscription = false

          // Cierre seguro: solo limpiar recursos globales si aún pertenecen a esta instancia
          if (this.instanceId === localInstanceId) {
            this._limpiarRecursos()
          } else {
            // Instancia posterior ya activa: solo silenciar el stream local cerrado
            if (localStream && localStream !== this.audioStream) {
              localStream.getTracks().forEach((t) => { try { t.stop() } catch (_) {} })
            }
          }

          if (
            this.instanceId === localInstanceId &&
            this.turnId === localTurnId &&
            this.sessionGeneration === localSessionGen &&
            this.generation === localProviderGen
          ) {
            if (this.onEnd) this.onEnd(localTurnId, localSessionGen, localProviderGen, localInstanceId)
          }
        }
      }

      // Iniciar captura con chunks cada 250ms
      recorder.start(250)

      // Hard cap de seguridad: 5.5 segundos máximo para comandos de voz de mostrador
      this.maxTimer = setTimeout(() => {
        if (this.instanceId !== instanceId) return
        console.info('[BackendSTTProvider] Límite máximo de turno (5.5s) alcanzado. Deteniendo...')
        this.stop(this.turnId)
        if (this.onRequestStop) {
          this.onRequestStop(this.turnId, this.sessionGeneration, this.generation, this.instanceId)
        }
      }, 5500)

      // Timer de seguridad si no hay habla en 4s
      this.initialSilenceTimer = setTimeout(() => {
        if (this.instanceId !== instanceId) return
        if (!this.speechStarted && this.isRecording) {
          console.log('[BackendSTTProvider] Sin habla detectada tras 4s. Deteniendo...')
          this.stop(this.turnId)
          if (this.onRequestStop) {
            this.onRequestStop(this.turnId, this.sessionGeneration, this.generation, this.instanceId)
          }
        }
      }, 4000)

    } catch (err) {
      this.isStarting = false
      if (stream) {
        stream.getTracks().forEach((t) => { try { t.stop() } catch (_) {} })
      }
      this._limpiarRecursos()
      if (this.onError) {
        this.onError({
          code: err.name === 'NotAllowedError' ? 'not-allowed' : 'mic-init-error',
          message: err.message,
        }, this.turnId, this.sessionGeneration, this.generation, this.instanceId)
      }
    }
  }

  _iniciarVAD(instanceId, stream) {
    try {
      const AudioCtx = typeof window !== 'undefined' ? (window.AudioContext || window.webkitAudioContext) : null
      if (!AudioCtx || !stream) return

      const ctx = new AudioCtx()
      this.audioContext = ctx
      if (ctx.state === 'suspended') {
        ctx.resume().catch(() => {})
      }

      const source = ctx.createMediaStreamSource(stream)
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 512
      source.connect(analyser)
      this.analyser = analyser

      const buffer = new Float32Array(analyser.fftSize)
      const UMBRAL_VOZ = 0.02
      const TIEMPO_SILENCIO_MS = 950

      this.vadInterval = setInterval(() => {
        if (this.instanceId !== instanceId || !this.isRecording || !this.analyser) return

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
              this.onSpeechStart(this.turnId, this.sessionGeneration, this.generation, instanceId)
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
            if (this.instanceId !== instanceId) return
            console.log('[BackendSTTProvider] VAD: Silencio natural detectado (950ms). Deteniendo...')
            this.stop(this.turnId)
            if (this.onRequestStop) {
              this.onRequestStop(this.turnId, this.sessionGeneration, this.generation, instanceId)
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

    // Abortar cualquier petición de red pendiente
    if (this.abortController) {
      try { this.abortController.abort() } catch (_) {}
      this.abortController = null
    }

    // Desconectar onstop del recorder para evitar que dispare peticiones HTTP al detenerlo
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.onstop = null
      try {
        this.mediaRecorder.stop()
      } catch (_) {}
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
      } catch (_) {}
      this.audioContext = null
      this.analyser = null
    }

    if (this.audioStream) {
      this.audioStream.getTracks().forEach((track) => {
        try { track.stop() } catch (_) {}
      })
      this.audioStream = null
    }
  }

  async _enviarAudioAlBackend(blob, turnId = null, signal = null) {
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('access_token') : null
    const formData = new FormData()
    formData.append('audio', blob, 'voz.webm')

    const headers = {}
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const fetchOptions = {
      method: 'POST',
      headers,
      body: formData,
    }
    if (signal) {
      fetchOptions.signal = signal
    }

    const res = await fetch(`${BASE}/agente/transcribir-audio`, fetchOptions)

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
