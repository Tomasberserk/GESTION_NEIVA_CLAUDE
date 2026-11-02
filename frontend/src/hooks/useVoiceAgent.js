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
      // Solo detener/nullear si este effect sigue siendo el dueño del ref
      // (protege contra ciclos de remontaje de StrictMode/HMR dejando refs huérfanas)
      if (managerRef.current === manager) {
        manager.detenerSesion()
        managerRef.current = null
      }
    }
  }, [])

  // [VOICE-HEARTBEAT] Anti-sueño: Render free duerme el servicio tras ~15 min sin
  // tráfico → cold start de decenas de segundos (causa #1 de las respuestas >10s).
  // Mientras el hook del modo voz esté vivo, latimos /health cada 4 min y el
  // primer latido al montar también precalienta el cold start.
  useEffect(() => {
    const BASE = import.meta.env.VITE_API_URL || '/api'
    const raiz = BASE.replace(/\/api\/?$/, '')
    let cancelado = false
    const latir = () => {
      const t = Date.now()
      fetch(`${raiz}/health`, { method: 'GET' })
        .then((r) => {
          if (!cancelado) console.log(`[VOICE-HEARTBEAT] /health → ${r.status} (${Date.now() - t}ms)`)
        })
        .catch(() => {})
    }
    latir()
    const id = setInterval(latir, 4 * 60 * 1000)
    return () => {
      cancelado = true
      clearInterval(id)
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

  const omitirRespuesta = useCallback(() => {
    console.log('[VOICE-DEBUG][useVoiceAgent] omitirRespuesta disparado (skip TTS)')
    if (managerRef.current) {
      managerRef.current.omitirRespuesta()
    }
  }, [])

  const reiniciarSesion = useCallback(async () => {
    console.log('[VOICE-DEBUG][useVoiceAgent] reiniciarSesion disparado (stop + start)')
    if (managerRef.current) {
      managerRef.current.detenerSesion()
    }
    setTranscript('')
    setErrorMessage(null)
    if (managerRef.current) {
      await managerRef.current.activarSesion(true)
    }
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

  const iniciarEscucha = useCallback(() => {
    console.log('[VOICE-DEBUG][useVoiceAgent] iniciarEscucha disparado')
    if (managerRef.current) {
      managerRef.current.iniciarEscucha()
    }
  }, [])

  return {
    voiceState,
    transcript,
    lastResponse,
    errorMessage,
    activarModoVoz,
    desactivarModoVoz,
    iniciarEscucha,
    detenerYEnviar,
    omitirRespuesta,
    reiniciarSesion,
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
