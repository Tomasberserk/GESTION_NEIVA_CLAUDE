import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'

const BASE = '/api'

export function useProductos() {
  const { usuario } = useAuth()
  const [productos, setProductos] = useState([])
  const [tienda, setTienda] = useState('')
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    if (!usuario) return
    setCargando(true)
    setError(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/productos/${usuario.empresa_id}`)
      if (!res.ok) throw new Error('Error cargando productos')
      const data = await res.json()
      setProductos(data.inventario)
      setTienda(data.tienda)
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [usuario])

  useEffect(() => {
    cargar()
  }, [cargar])

  const crear = async (payload) => {
    const res = await authService.fetchAuth(`${BASE}/productos/`, {
      method: 'POST',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error creando producto')
    }
    await cargar()
    return res.json()
  }

  const actualizar = async (id, payload) => {
    const res = await authService.fetchAuth(`${BASE}/productos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error actualizando producto')
    }
    await cargar()
  }

  const eliminar = async (id) => {
    const res = await authService.fetchAuth(`${BASE}/productos/${id}`, {
      method: 'DELETE',
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || 'Error eliminando producto')
    }
    await cargar()
  }

  return { productos, tienda, cargando, error, cargar, crear, actualizar, eliminar }
}
