import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

export function useVentas() {
  const { usuario } = useAuth()
  const [ventas, setVentas] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    if (!usuario) return
    setCargando(true)
    setError(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/ventas/${usuario.empresa_id}`)
      if (!res.ok) throw new Error('Error cargando ventas')
      setVentas(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [usuario])

  useEffect(() => {
    cargar()
  }, [cargar])

  const registrar = async (detalles) => {
    const res = await authService.fetchAuth(`${BASE}/ventas/${usuario.empresa_id}`, {
      method: 'POST',
      body: JSON.stringify({ detalles }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error registrando venta')
    }
    const resultado = await res.json()
    await cargar()
    return resultado
  }

  return { ventas, cargando, error, cargar, registrar }
}
