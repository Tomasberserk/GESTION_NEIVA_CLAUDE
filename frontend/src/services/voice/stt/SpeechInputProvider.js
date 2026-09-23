/**
 * Interfaz base para proveedores de entrada de voz (STT).
 * Define el contrato unificado para WebSpeechProvider y BackendSTTProvider.
 */

export class SpeechInputProvider {
  constructor() {
    this.onSpeechStart = null // (turnId?: number, sessionGen?: number, providerGen?: number, instanceId?: string) => void
    this.onTranscript = null // (text: string, isFinal: boolean, turnId?: number, sessionGen?: number, providerGen?: number, instanceId?: string) => void
    this.onError = null // (error: { code: string, message: string }, turnId?: number, sessionGen?: number, providerGen?: number, instanceId?: string) => void
    this.onEnd = null // (turnId?: number, sessionGen?: number, providerGen?: number, instanceId?: string) => void
    this.onRequestStop = null // (turnId?: number, sessionGen?: number, providerGen?: number, instanceId?: string) => void
    this.generation = 0
    this.turnId = null
    this.sessionGeneration = 0
    this.instanceId = null
  }

  async start(turnId = null, sessionGeneration = 0, providerGeneration = 0) {
    throw new Error('start() debe ser implementado por la subclase')
  }

  requestStop(turnId = null) {
    this.stop(turnId)
  }

  stop(turnId = null) {
    throw new Error('stop() debe ser implementado por la subclase')
  }

  cancel(turnId = null) {
    throw new Error('cancel() debe ser implementado por la subclase')
  }

  isActive() {
    return false
  }
}
