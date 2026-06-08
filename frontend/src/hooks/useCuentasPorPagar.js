import { useState, useCallback } from 'react'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

export function useCuentasPorPagar() {
  const [cuentas, setCuentas] = useState([])
  const [total, setTotal] = useState(0)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async (filtros = {}) => {
    setCargando(true)
    setError(null)
    try {
      const params = new URLSearchParams({ limit: 100 })
      if (filtros.estado) params.set('estado', filtros.estado)
      if (filtros.proveedor_id) params.set('proveedor_id', filtros.proveedor_id)
      const res = await authService.fetchAuth(`${BASE}/cuentas-por-pagar?${params}`)
      if (!res.ok) throw new Error('Error cargando cuentas por pagar')
      const data = await res.json()
      setCuentas(data.items ?? [])
      setTotal(data.total ?? 0)
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [])

  const registrarAbono = useCallback(async (cxpId, payload) => {
    const res = await authService.fetchAuth(`${BASE}/cuentas-por-pagar/${cxpId}/abonos`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error registrando abono')
    }
    return res.json()
  }, [])

  const obtenerAbonos = useCallback(async (cxpId) => {
    const res = await authService.fetchAuth(`${BASE}/cuentas-por-pagar/${cxpId}/abonos`)
    if (!res.ok) throw new Error('Error cargando abonos')
    return res.json()
  }, [])

  const reversarAbono = useCallback(async (abonoId) => {
    const res = await authService.fetchAuth(`${BASE}/cuentas-por-pagar/abonos/${abonoId}`, {
      method: 'DELETE',
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error reversando abono')
    }
    return res.json()
  }, [])

  return { cuentas, total, cargando, error, cargar, registrarAbono, obtenerAbonos, reversarAbono }
}