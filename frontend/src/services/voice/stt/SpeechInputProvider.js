/**
 * Interfaz base para proveedores de entrada de voz (STT).
 * Define el contrato unificado para WebSpeechProvider y BackendSTTProvider.
 */

export class SpeechInputProvider {
  constructor() {
    this.onSpeechStart = null
    this.onTranscript = null // (text: string, isFinal: boolean) => void
    this.onError = null // (error: { code: string, message: string }) => void
    this.onEnd = null
    this.onRequestStop = null
    this.generation = 0
  }

  async start() {
    throw new Error('start() debe ser implementado por la subclase')
  }

  requestStop() {
    this.stop()
  }

  stop() {
    throw new Error('stop() debe ser implementado por la subclase')
  }

  cancel() {
    throw new Error('cancel() debe ser implementado por la subclase')
  }

  isActive() {
    return false
  }
}
