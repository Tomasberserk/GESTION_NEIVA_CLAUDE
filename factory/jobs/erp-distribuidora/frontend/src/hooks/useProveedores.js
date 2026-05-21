import { useState, useCallback } from 'react'
import authService from '../services/authService'

export function useProveedores() {
  const [proveedores, setProveedores] = useState([])
  const [total, setTotal] = useState(0)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async (q = '') => {
    setCargando(true)
    setError(null)
    try {
      const params = new URLSearchParams({ limit: 100 })
      if (q) params.set('q', q)
      const res = await authService.fetchAuth(`/api/proveedores?${params}`)
      if (!res.ok) throw new Error('Error cargando proveedores')
      const data = await res.json()
      setProveedores(data.items ?? [])
      setTotal(data.total ?? 0)
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [])

  const crear = useCallback(async (payload) => {
    const res = await authService.fetchAuth('/api/proveedores', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error creando proveedor')
    }
    return res.json()
  }, [])

  const actualizar = useCallback(async (id, payload) => {
    const res = await authService.fetchAuth(`/api/proveedores/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error actualizando proveedor')
    }
    return res.json()
  }, [])

  const eliminar = useCallback(async (id) => {
    const res = await authService.fetchAuth(`/api/proveedores/${id}`, { method: 'DELETE' })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error eliminando proveedor')
    }
    return res.json()
  }, [])

  return { proveedores, total, cargando, error, cargar, crear, actualizar, eliminar }
}
