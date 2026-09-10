const BASE = import.meta.env.VITE_API_URL || '/api'

let currentConversationId = localStorage.getItem('agente_conversation_id') || null

export const agentService = {
  getConversationId() {
    return currentConversationId
  },

  setConversationId(id) {
    currentConversationId = id
    if (id) {
      localStorage.setItem('agente_conversation_id', id)
    } else {
      localStorage.removeItem('agente_conversation_id')
    }
  },

  resetConversation() {
    this.setConversationId(null)
  },

  async enviarMensaje(mensaje) {
    const token = localStorage.getItem('access_token')
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

    const res = await fetch(`${BASE}/agente/mensaje`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      let errorMsg = 'Error al comunicarse con el asistente'
      try {
        const errJson = await res.json()
        errorMsg = errJson.detail || errorMsg
      } catch {
        // Ignorar error al parsear json
      }
      throw new Error(errorMsg)
    }

    const data = await res.json()
    if (data.conversation_id) {
      this.setConversationId(data.conversation_id)
    }

    return data
  },
}

export default agentService
