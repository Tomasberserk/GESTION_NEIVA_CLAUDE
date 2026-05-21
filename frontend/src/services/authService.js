const BASE = import.meta.env.VITE_API_URL || '/api'

async function parseJsonSafe(res) {
  const text = await res.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return null
  }
}

const authService = {
  setToken(token) {
    localStorage.setItem('access_token', token)
  },

  getToken() {
    return localStorage.getItem('access_token')
  },

  clearToken() {
    localStorage.removeItem('access_token')
  },

  async login(email, password) {
    const res = await fetch(`${BASE}/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await parseJsonSafe(res)
      throw new Error(err?.detail || res.statusText || 'Credenciales inválidas')
    }
    const data = await parseJsonSafe(res)
    if (!data) throw new Error('Respuesta inválida del servidor')
    this.setToken(data.access_token)
    return data
  },

  async registro(payload) {
    const res = await fetch(`${BASE}/auth/registro-completo`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await parseJsonSafe(res)
      throw new Error(err?.detail || res.statusText || 'Error en el registro')
    }
    const data = await parseJsonSafe(res)
    if (!data) throw new Error('Respuesta inválida del servidor')
    this.setToken(data.access_token)
    return data
  },

  async crearEmpresa(payload) {
    const res = await fetch(`${BASE}/empresas/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await parseJsonSafe(res)
      throw new Error(err?.detail || res.statusText || 'Error creando empresa')
    }
    return parseJsonSafe(res)
  },

  async getMe() {
    const res = await this.fetchAuth(`${BASE}/me`)
    if (!res.ok) throw new Error('No autenticado')
    const data = await parseJsonSafe(res)
    if (!data) throw new Error('Respuesta inválida del servidor')
    return data
  },

  logout() {
    this.clearToken()
  },

  async fetchAuth(url, options = {}) {
    const token = this.getToken()
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    }
    const res = await fetch(url, { ...options, headers })
    if (res.status === 401) {
      this.clearToken()
      window.location.href = '/login'
    }
    return res
  },
}

export default authService
