import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'
import { TrendingUp, Package, ShoppingBag, AlertTriangle, CheckCircle } from 'lucide-react'

const BASE = import.meta.env.VITE_API_URL || '/api'
const fmt = (n) => Number(n).toLocaleString('es-CO', { maximumFractionDigits: 0 })

const ICONO_CAT = {
  'Utiles escolares': '✏️',
  'Papel y resmas':   '📄',
  'Tecnologia':       '💻',
  'Servicios':        '🖨️',
  'Miscelanea':       '🗂️',
}

function KpiCard({ label, value, sub, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
            {label}
          </p>
          <p className={`text-3xl font-bold ${color}`}>
            {value}
          </p>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <div className={`p-2.5 rounded-xl bg-slate-50`}>
          <Icon size={20} className="text-slate-400" />
        </div>
      </div>
    </div>
  )
}

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

  const stockBajo = datos?.stock_bajo ?? []
  const hayStockBajo = stockBajo.length > 0

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-6">

        <div>
          <h1 className="text-xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Resumen del día — {new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard
            label="Ventas hoy"
            value={cargando ? '…' : fmt(datos?.ventas_hoy ?? 0)}
            sub="transacciones"
            icon={ShoppingBag}
            color="text-slate-800"
          />
          <KpiCard
            label="Ingresos hoy"
            value={cargando ? '…' : `$${fmt(datos?.ingresos_hoy ?? 0)}`}
            sub="pesos colombianos"
            icon={TrendingUp}
            color="text-indigo-600"
          />
          <KpiCard
            label="Productos activos"
            value={cargando ? '…' : fmt(datos?.total_productos_activos ?? 0)}
            sub="en inventario"
            icon={Package}
            color="text-slate-800"
          />
        </div>

        {/* Stock bajo — widget central */}
        <div
          className={`rounded-xl border p-5 ${
            hayStockBajo
              ? 'bg-amber-50 border-amber-200'
              : 'bg-emerald-50 border-emerald-200'
          }`}
        >
          <div className="flex items-center gap-2 mb-4">
            {hayStockBajo ? (
              <AlertTriangle size={18} className="text-amber-600 shrink-0" />
            ) : (
              <CheckCircle size={18} className="text-emerald-600 shrink-0" />
            )}
            <h2 className={`font-semibold text-sm ${hayStockBajo ? 'text-amber-800' : 'text-emerald-800'}`}>
              {hayStockBajo
                ? `${stockBajo.length} producto${stockBajo.length === 1 ? '' : 's'} con stock bajo`
                : 'Stock en buen estado'}
            </h2>
          </div>

          {cargando ? (
            <div className="space-y-2">
              {[1, 2, 3].map(n => (
                <div key={n} className="h-10 bg-amber-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : hayStockBajo ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {stockBajo.map(p => (
                <div
                  key={p.id}
                  className="bg-white rounded-xl px-4 py-3 flex items-center justify-between gap-3 shadow-sm"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-lg shrink-0">
                      {ICONO_CAT[p.categoria] || '🗂️'}
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-800 truncate">{p.nombre}</p>
                      <p className="text-xs text-slate-400">{p.categoria}</p>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-sm font-bold text-amber-700">{p.cantidad_actual}</p>
                    <p className="text-[10px] text-slate-400">mín {p.stock_minimo}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-emerald-700">
              Ningún producto ha alcanzado su umbral de stock mínimo.
            </p>
          )}
        </div>

      </div>
    </div>
  )
}
