import { useState, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

export function useVentas() {
  const { usuario } = useAuth()
  const [ventas, setVentas] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async (desde, hasta) => {
    if (!usuario) return
    setCargando(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (desde) params.set('desde', desde)
      if (hasta) params.set('hasta', hasta)
      const qs = params.toString()
      const url = `${BASE}/ventas/${usuario.empresa_id}${qs ? `?${qs}` : ''}`
      const res = await authService.fetchAuth(url)
      if (!res.ok) throw new Error('Error cargando ventas')
      setVentas(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [usuario])

  const registrar = async (items) => {
    const res = await authService.fetchAuth(`${BASE}/ventas/${usuario.empresa_id}`, {
      method: 'POST',
      body: JSON.stringify({ items }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error registrando venta')
    }
    return res.json()
  }

  return { ventas, cargando, error, cargar, registrar }
}
