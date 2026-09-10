import { useState, useEffect, useRef, useCallback } from 'react'
import { VoiceTurnManager, VoiceTurnState } from '../services/voice/VoiceTurnManager'
import { agentService } from '../services/agentService'

/**
 * Hook para integrar el VoiceTurnManager en cualquier componente React.
 * Mantiene la sincronización de estado y expone métodos determinísticos.
 */
export function useVoiceAgent() {
  const [voiceState, setVoiceState] = useState(VoiceTurnState.IDLE)
  const [transcript, setTranscript] = useState('')
  const [lastResponse, setLastResponse] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)

  const managerRef = useRef(null)

  useEffect(() => {
    const manager = new VoiceTurnManager({
      onStateChange: (newState, data) => {
        setVoiceState(newState)
        if (newState === VoiceTurnState.ERROR && data.message) {
          setErrorMessage(data.message)
        } else if (newState !== VoiceTurnState.ERROR) {
          setErrorMessage(null)
        }
      },
      onTranscriptUpdate: (text) => {
        setTranscript(text)
      },
      onAgentResponse: (res) => {
        setLastResponse(res)
      },
      onSendMessage: async (text) => {
        return await agentService.enviarMensaje(text)
      },
    })

    managerRef.current = manager

    return () => {
      manager.detenerSesion()
    }
  }, [])

  const activarModoVoz = useCallback(async () => {
    setTranscript('')
    setErrorMessage(null)
    if (managerRef.current) {
      await managerRef.current.activarSesion()
    }
  }, [])

  const desactivarModoVoz = useCallback(() => {
    if (managerRef.current) {
      managerRef.current.detenerSesion()
    }
    setTranscript('')
  }, [])

  // Confirmación táctil (comparte el mismo camino transaccional)
  const confirmarOperacion = useCallback(async () => {
    if (managerRef.current) {
      await managerRef.current.enviarMensajeManual('sí, dale')
    }
  }, [])

  const cancelarOperacion = useCallback(async () => {
    if (managerRef.current) {
      await managerRef.current.enviarMensajeManual('cancelar')
    }
  }, [])

  const seleccionarOpcion = useCallback(async (opcionTexto) => {
    if (managerRef.current) {
      await managerRef.current.enviarMensajeManual(opcionTexto)
    }
  }, [])

  return {
    voiceState,
    transcript,
    lastResponse,
    errorMessage,
    activarModoVoz,
    desactivarModoVoz,
    confirmarOperacion,
    cancelarOperacion,
    seleccionarOpcion,
    isListening: voiceState === VoiceTurnState.LISTENING || voiceState === VoiceTurnState.SPEECH_DETECTED,
    isProcessing: voiceState === VoiceTurnState.PROCESSING,
    isSpeaking: voiceState === VoiceTurnState.SPEAKING,
    isConfirming: voiceState === VoiceTurnState.CONFIRMING,
    isActive: voiceState !== VoiceTurnState.IDLE,
  }
}
