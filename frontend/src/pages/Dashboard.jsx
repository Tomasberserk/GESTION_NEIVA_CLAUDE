import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'

const BASE = import.meta.env.VITE_API_URL || '/api'

const PALETA = ['#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe']

function TooltipVentas({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg px-3 py-2 text-sm">
      <p className="font-semibold text-slate-800 mb-0.5">{payload[0].payload.nombre}</p>
      <p className="text-violet-600">
        {Number(payload[0].value).toLocaleString('es-CO')} vendidos
      </p>
    </div>
  )
}

function BadgeDias({ dias }) {
  if (dias < 0)  return <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700">Vencido</span>
  if (dias === 0) return <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700">Vence hoy</span>
  if (dias <= 7)  return <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-orange-100 text-orange-700">{dias}d</span>
  return               <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-700">{dias}d</span>
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

  const fmt = (n) => Number(n).toLocaleString('es-CO')
  const topProductos     = datos?.top_productos      ?? []
  const alertasVenc      = datos?.alertas_vencimiento ?? []

  return (
    <div className="space-y-6">

      {/* Encabezado */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-1">Dashboard</h1>
        <p className="text-gray-400 text-sm">
          Bienvenido{usuario?.email ? `, ${usuario.email}` : ''} — resumen de hoy
        </p>
      </div>

      {/* Banner trial */}
      {!cargando && datos?.dias_trial_restantes != null && (
        <div className={`px-4 py-3 rounded-xl text-sm font-medium border ${
          datos.dias_trial_restantes <= 5
            ? 'bg-red-50 text-red-700 border-red-200'
            : datos.dias_trial_restantes <= 10
            ? 'bg-amber-50 text-amber-700 border-amber-200'
            : 'bg-blue-50 text-blue-700 border-blue-200'
        }`}>
          {datos.dias_trial_restantes === 0
            ? 'Tu período de prueba vence hoy. Contacta al administrador para continuar.'
            : `Periodo de prueba activo — te quedan ${datos.dias_trial_restantes} día${datos.dias_trial_restantes === 1 ? '' : 's'}. Plan: ${datos.plan?.toUpperCase() ?? 'BASIC'}`
          }
        </div>
      )}

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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

      {/* Gráfica top 5 + panel vencimientos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Gráfica horizontal de barras */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">
            Top 5 productos más vendidos
          </h2>
          {cargando ? (
            <div className="flex items-center justify-center h-52">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-500" />
            </div>
          ) : topProductos.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-52 text-slate-400 text-sm gap-2">
              <span className="text-3xl">📊</span>
              Aún no hay ventas registradas
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={topProductos}
                layout="vertical"
                margin={{ top: 0, right: 16, left: 4, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11, fill: '#94a3b8' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="nombre"
                  width={100}
                  tick={{ fontSize: 11, fill: '#475569' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => v.length > 12 ? `${v.slice(0, 12)}…` : v}
                />
                <Tooltip content={<TooltipVentas />} cursor={{ fill: '#f8fafc' }} />
                <Bar dataKey="total_vendido" radius={[0, 6, 6, 0]} maxBarSize={30}>
                  {topProductos.map((_, i) => (
                    <Cell key={i} fill={PALETA[i % PALETA.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Panel de alertas de vencimiento */}
        <div className={`rounded-xl border p-5 ${
          alertasVenc.length > 0
            ? 'bg-red-50 border-red-200'
            : 'bg-green-50 border-green-200'
        }`}>
          <h2 className={`text-sm font-semibold mb-3 ${
            alertasVenc.length > 0 ? 'text-red-700' : 'text-green-700'
          }`}>
            Próximos a vencer
          </h2>

          {cargando ? (
            <div className="animate-pulse space-y-2">
              {[1, 2, 3].map(n => (
                <div key={n} className="h-10 bg-red-100 rounded-lg" />
              ))}
            </div>
          ) : alertasVenc.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <span className="text-3xl mb-2">✅</span>
              <p className="text-green-700 text-sm font-semibold">Todo en orden</p>
              <p className="text-green-600 text-xs mt-1">
                Ningún producto vence en los próximos 15 días
              </p>
            </div>
          ) : (
            <div className="space-y-2 overflow-y-auto max-h-52">
              {alertasVenc.map(p => (
                <div
                  key={p.id}
                  className="bg-white rounded-lg px-3 py-2 flex items-center justify-between gap-2 shadow-sm"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate">{p.nombre}</p>
                    <p className="text-xs text-slate-400">{p.fecha_vencimiento}</p>
                  </div>
                  <BadgeDias dias={p.dias_restantes} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Stock bajo */}
      {!cargando && datos?.stock_bajo?.length > 0 && (
        <div className="bg-white rounded-xl border border-amber-200 p-5">
          <h2 className="text-sm font-semibold text-amber-700 mb-3">
            Stock bajo — {datos.stock_bajo.length} producto{datos.stock_bajo.length === 1 ? '' : 's'} con 5 unidades o menos
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
