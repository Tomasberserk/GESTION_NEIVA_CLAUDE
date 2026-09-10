/**
 * Registrador de telemetría ligero para el Modo Voz.
 * Buffer en memoria volátil; localStorage solo como almacenamiento auxiliar no bloqueante.
 */

class VoiceTelemetryManager {
  constructor() {
    this.buffer = []
    this.maxBufferSize = 50
    this.metrics = {
      sessionsStarted: 0,
      speechDetectedCount: 0,
      sttSuccessCount: 0,
      sttFailureCount: 0,
      backendCalls: 0,
      commandsCompleted: 0,
      commandsCancelled: 0,
      fallbacksUsed: 0,
    }
  }

  _record(eventType, details = {}) {
    const entry = {
      type: eventType,
      timestamp: Date.now(),
      details,
    }

    this.buffer.push(entry)
    if (this.buffer.length > this.maxBufferSize) {
      this.buffer.shift()
    }

    // Guardado no bloqueante en localStorage (opcional)
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        localStorage.setItem('voice_telemetry_summary', JSON.stringify(this.metrics))
      }
    } catch {
      // Ignorar si el storage está lleno o bloqueado
    }
  }

  recordSessionStart() {
    this.metrics.sessionsStarted++
    this._record('SESSION_START')
  }

  recordSpeechDetected() {
    this.metrics.speechDetectedCount++
    this._record('SPEECH_DETECTED')
  }

  recordSTTSuccess(latencyMs = 0) {
    this.metrics.sttSuccessCount++
    this._record('STT_SUCCESS', { latencyMs })
  }

  recordSTTFailure(code = 'unknown') {
    this.metrics.sttFailureCount++
    this._record('STT_FAILURE', { code })
  }

  recordBackendResponse(latencyMs = 0) {
    this.metrics.backendCalls++
    this._record('BACKEND_RESPONSE', { latencyMs })
  }

  recordCommandSuccess() {
    this.metrics.commandsCompleted++
    this._record('COMMAND_SUCCESS')
  }

  recordCommandCancelled() {
    this.metrics.commandsCancelled++
    this._record('COMMAND_CANCELLED')
  }

  recordFallbackUsed() {
    this.metrics.fallbacksUsed++
    this._record('FALLBACK_USED')
  }

  getMetrics() {
    const totalCommands = this.metrics.commandsCompleted + this.metrics.commandsCancelled + this.metrics.sttFailureCount
    const successRate = totalCommands > 0
      ? Math.round((this.metrics.commandsCompleted / totalCommands) * 100)
      : 100

    return {
      ...this.metrics,
      voice_command_success_rate: `${successRate}%`,
    }
  }
}

export const voiceTelemetry = new VoiceTelemetryManager()
