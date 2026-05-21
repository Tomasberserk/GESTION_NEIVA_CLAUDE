import { useState, useCallback } from 'react'
import authService from '../services/authService'

export function useProductos() {
  const [productos, setProductos] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async (q = '') => {
    setCargando(true)
    setError(null)
    try {
      const url = q ? `/api/productos?q=${encodeURIComponent(q)}&limit=50` : '/api/productos?limit=100'
      const res = await authService.fetchAuth(url)
      if (!res.ok) throw new Error('Error cargando productos')
      const data = await res.json()
      setProductos(Array.isArray(data) ? data : data.items ?? [])
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [])

  const crear = useCallback(async (payload) => {
    const res = await authService.fetchAuth('/api/productos', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error creando producto')
    }
    return res.json()
  }, [])

  const actualizar = useCallback(async (id, payload) => {
    const res = await authService.fetchAuth(`/api/productos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error actualizando producto')
    }
    return res.json()
  }, [])

  const eliminar = useCallback(async (id) => {
    const res = await authService.fetchAuth(`/api/productos/${id}`, { method: 'DELETE' })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error eliminando producto')
    }
    return res.json()
  }, [])

  return { productos, cargando, error, cargar, crear, actualizar, eliminar }
}
