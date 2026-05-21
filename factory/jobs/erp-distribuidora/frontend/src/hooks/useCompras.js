import { useState, useCallback } from 'react'
import authService from '../services/authService'

export function useCompras() {
  const [compras, setCompras] = useState([])
  const [total, setTotal] = useState(0)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async (filtros = {}) => {
    setCargando(true)
    setError(null)
    try {
      const params = new URLSearchParams({ limit: 100 })
      if (filtros.desde) params.set('desde', filtros.desde)
      if (filtros.hasta) params.set('hasta', filtros.hasta)
      if (filtros.proveedor_id) params.set('proveedor_id', filtros.proveedor_id)
      if (filtros.estado) params.set('estado', filtros.estado)
      const res = await authService.fetchAuth(`/api/compras?${params}`)
      if (!res.ok) throw new Error('Error cargando compras')
      const data = await res.json()
      setCompras(data.items ?? [])
      setTotal(data.total ?? 0)
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [])

  const registrar = useCallback(async (payload) => {
    const res = await authService.fetchAuth('/api/compras', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error registrando compra')
    }
    return res.json()
  }, [])

  const anular = useCallback(async (id) => {
    const res = await authService.fetchAuth(`/api/compras/${id}`, { method: 'DELETE' })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error anulando compra')
    }
    return res.json()
  }, [])

  return { compras, total, cargando, error, cargar, registrar, anular }
}
