const BASE = '/api'

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
      const err = await res.json()
      throw new Error(err.detail || 'Credenciales inválidas')
    }
    const data = await res.json()
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
      const err = await res.json()
      throw new Error(err.detail || 'Error en el registro')
    }
    const data = await res.json()
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
      const err = await res.json()
      throw new Error(err.detail || 'Error creando empresa')
    }
    return res.json()
  },

  async getMe() {
    const res = await this.fetchAuth(`${BASE}/me`)
    if (!res.ok) throw new Error('No autenticado')
    return res.json()
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
