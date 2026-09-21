const BASE = import.meta.env.VITE_API_URL || '/api'

let currentConversationId = localStorage.getItem('agente_conversation_id') || null

export const agentService = {
  getConversationId() {
    return currentConversationId
  },

  setConversationId(id) {
    console.log('[VOICE-DEBUG][agentService] setConversationId:', id)
    currentConversationId = id
    if (id) {
      localStorage.setItem('agente_conversation_id', id)
    } else {
      localStorage.removeItem('agente_conversation_id')
    }
  },

  resetConversation() {
    console.log('[VOICE-DEBUG][agentService] resetConversation()')
    this.setConversationId(null)
  },

  async enviarMensaje(mensaje) {
    const token = localStorage.getItem('access_token')
    console.log('[VOICE-DEBUG][agentService] enviarMensaje llamado con:', mensaje, 'tieneToken:', !!token, 'convId:', currentConversationId)

    const headers = {
      'Content-Type': 'application/json',
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const payload = {
      mensaje,
      conversation_id: currentConversationId,
    }

    console.log('[VOICE-DEBUG][agentService] Enviando POST a:', `${BASE}/agente/mensaje`, 'payload:', payload)

    const res = await fetch(`${BASE}/agente/mensaje`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    })

    console.log('[VOICE-DEBUG][agentService] HTTP status respuesta:', res.status)

    if (!res.ok) {
      let errorMsg = 'Error al comunicarse con el asistente'
      try {
        const errJson = await res.json()
        if (typeof errJson.detail === 'string') {
          errorMsg = errJson.detail
        } else if (errJson.detail && typeof errJson.detail === 'object') {
          errorMsg = errJson.detail.message || JSON.stringify(errJson.detail)
        } else if (errJson.message) {
          errorMsg = errJson.message
        }
      } catch {
        // Ignorar error al parsear json
      }
      console.error('[VOICE-DEBUG][agentService] Error HTTP:', res.status, errorMsg)
      throw new Error(errorMsg)
    }

    const data = await res.json()
    console.log('[VOICE-DEBUG][agentService] Datos recibidos del backend:', data)

    if (data.conversation_id) {
      this.setConversationId(data.conversation_id)
    }

    return data
  },
}

export default agentService
