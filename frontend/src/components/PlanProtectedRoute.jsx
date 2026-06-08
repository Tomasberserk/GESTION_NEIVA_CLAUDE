import { useState, useEffect } from 'react'
import { Navigate, Outlet } from 'react-router-dom'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

export default function PlanProtectedRoute({ planesPermitidos }) {
  const [plan, setPlan] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    authService
      .fetchAuth(`${BASE}/empresas/mi-empresa`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) {
          setPlan(data.plan)
        }
      })
      .catch(() => {})
      .finally(() => setCargando(false))
  }, [])

  if (cargando) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    )
  }

  if (!plan || !planesPermitidos.includes(plan)) {
    return <Navigate to="/inventario" replace />
  }

  return <Outlet />
}
