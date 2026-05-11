import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'

const BASE = 'http://localhost:8000'

export default function Dashboard() {
  const { usuario } = useAuth()
  const [datos, setDatos] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    if (!usuario?.empresa_id) return
    const cargar = async () => {
      try {
        const res = await authService.fetchAuth(`${BASE}/dashboard/${usuario.empresa_id}`)
        if (res.ok) setDatos(await res.json())
      } finally {
        setCargando(false)
      }
    }
    cargar()
  }, [usuario])

  const fmt = (n) => Number(n).toLocaleString('es-CO')

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-1">Dashboard</h1>
      <p className="text-gray-400 text-sm mb-6">
        Bienvenido{usuario?.email ? `, ${usuario.email}` : ''} — resumen de hoy
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Ventas hoy</p>
          <p className="text-3xl font-bold text-slate-800">
            {cargando ? '…' : fmt(datos?.ventas_hoy ?? 0)}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Ingresos hoy</p>
          <p className="text-3xl font-bold text-violet-600">
            {cargando ? '…' : `$${fmt(datos?.ingresos_hoy ?? 0)}`}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Productos activos</p>
          <p className="text-3xl font-bold text-slate-800">
            {cargando ? '…' : fmt(datos?.total_productos ?? 0)}
          </p>
        </div>
      </div>

      {!cargando && datos?.stock_bajo?.length > 0 && (
        <div className="bg-white rounded-xl border border-amber-200 p-5">
          <h2 className="text-sm font-semibold text-amber-700 mb-3">
            Stock bajo ({datos.stock_bajo.length} productos con 5 unidades o menos)
          </h2>
          <div className="space-y-2">
            {datos.stock_bajo.map(p => (
              <div key={p.id} className="flex justify-between text-sm text-gray-700">
                <span>{p.nombre}</span>
                <span className="font-semibold text-amber-600">{p.cantidad} uds</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
