import { useState, useEffect, useRef, useCallback } from 'react'
import { VoiceTurnManager, VoiceTurnState } from '../services/voice/VoiceTurnManager'
import { agentService } from '../services/agentService'

/**
 * Hook para integrar el VoiceTurnManager en cualquier componente React.
 * Instrumentado con logs de diagnóstico.
 */
export function useVoiceAgent() {
  const [voiceState, setVoiceState] = useState(VoiceTurnState.IDLE)
  const [transcript, setTranscript] = useState('')
  const [lastResponse, setLastResponse] = useState(null)
  const [errorMessage, setErrorMessage] = useState(null)

  const managerRef = useRef(null)

  useEffect(() => {
    console.log('[VOICE-DEBUG][useVoiceAgent] useEffect inicializando VoiceTurnManager...')
    const manager = new VoiceTurnManager({
      onStateChange: (newState, data) => {
        console.log(`[VOICE-DEBUG][useVoiceAgent] onStateChange recibido: ${newState}`, data)
        setVoiceState(newState)
        if (newState === VoiceTurnState.ERROR && data.message) {
          setErrorMessage(data.message)
        } else if (newState !== VoiceTurnState.ERROR) {
          setErrorMessage(null)
        }
      },
      onTranscriptUpdate: (text, isFinal) => {
        console.log(`[VOICE-DEBUG][useVoiceAgent] onTranscriptUpdate: "${text}", isFinal: ${isFinal}`)
        setTranscript(text)
      },
      onAgentResponse: (res) => {
        console.log('[VOICE-DEBUG][useVoiceAgent] onAgentResponse recibido:', res)
        setLastResponse(res)
      },
      onSendMessage: async (text) => {
        console.log(`[VOICE-DEBUG][useVoiceAgent] onSendMessage invocando agentService.enviarMensaje("${text}")...`)
        return await agentService.enviarMensaje(text)
      },
    })

    managerRef.current = manager

    return () => {
      console.log('[VOICE-DEBUG][useVoiceAgent] Limpiando sesión en desmontaje...')
      manager.detenerSesion()
    }
  }, [])

  const activarModoVoz = useCallback(async (saludar = true) => {
    console.log('[VOICE-DEBUG][useVoiceAgent] activarModoVoz disparado por usuario, saludar:', saludar)
    setTranscript('')
    setErrorMessage(null)
    if (managerRef.current) {
      await managerRef.current.activarSesion(saludar)
    } else {
      console.error('[VOICE-DEBUG][useVoiceAgent] managerRef.current es null al activar')
    }
  }, [])

  const desactivarModoVoz = useCallback(() => {
    console.log('[VOICE-DEBUG][useVoiceAgent] desactivarModoVoz disparado')
    if (managerRef.current) {
      managerRef.current.detenerSesion()
    }
    setTranscript('')
  }, [])

  const detenerYEnviar = useCallback(() => {
    console.log('[VOICE-DEBUG][useVoiceAgent] detenerYEnviar disparado')
    if (managerRef.current) {
      managerRef.current.detenerYEnviar()
    }
  }, [])

  const isActionBusyRef = useRef(false)

  const confirmarOperacion = useCallback(async () => {
    if (isActionBusyRef.current) return
    isActionBusyRef.current = true
    console.log('[VOICE-DEBUG][useVoiceAgent] confirmarOperacion táctil disparado ("sí, dale")')
    try {
      if (managerRef.current) {
        await managerRef.current.enviarMensajeManual('sí, dale')
      }
    } finally {
      setTimeout(() => { isActionBusyRef.current = false }, 1000)
    }
  }, [])

  const cancelarOperacion = useCallback(async () => {
    if (isActionBusyRef.current) return
    isActionBusyRef.current = true
    console.log('[VOICE-DEBUG][useVoiceAgent] cancelarOperacion táctil disparado ("cancelar")')
    try {
      if (managerRef.current) {
        await managerRef.current.enviarMensajeManual('cancelar')
      }
    } finally {
      setTimeout(() => { isActionBusyRef.current = false }, 1000)
    }
  }, [])

  const seleccionarOpcion = useCallback(async (opcionTexto) => {
    if (isActionBusyRef.current) return
    isActionBusyRef.current = true
    console.log(`[VOICE-DEBUG][useVoiceAgent] seleccionarOpcion táctil disparado ("${opcionTexto}")`)
    try {
      if (managerRef.current) {
        await managerRef.current.enviarMensajeManual(opcionTexto)
      }
    } finally {
      setTimeout(() => { isActionBusyRef.current = false }, 1000)
    }
  }, [])

  return {
    voiceState,
    transcript,
    lastResponse,
    errorMessage,
    activarModoVoz,
    desactivarModoVoz,
    detenerYEnviar,
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
