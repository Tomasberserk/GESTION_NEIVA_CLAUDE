import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { useVentas } from '../hooks/useVentas'
import authService from '../services/authService'
import { Download, TrendingUp } from 'lucide-react'

const BASE = import.meta.env.VITE_API_URL || '/api'

const TABS = [
  { id: 'hoy',       label: 'Hoy',             labelCorto: 'Hoy' },
  { id: 'semana',    label: 'Esta semana',      labelCorto: 'Semana' },
  { id: 'historico', label: 'Últimos 30 días',  labelCorto: '30 días' },
]

function getFechas(tab) {
  const ahora = new Date()
  const fin = ahora.toISOString()
  const inicio = new Date(ahora)

  if (tab === 'hoy') {
    inicio.setHours(0, 0, 0, 0)
  } else if (tab === 'semana') {
    const dow = inicio.getDay() || 7
    inicio.setDate(inicio.getDate() - (dow - 1))
    inicio.setHours(0, 0, 0, 0)
  } else {
    inicio.setDate(inicio.getDate() - 30)
    inicio.setHours(0, 0, 0, 0)
  }

  return { desde: inicio.toISOString(), hasta: fin }
}

const fmt = (n) => Number(n).toLocaleString('es-CO', { maximumFractionDigits: 0 })

const formatFecha = (fecha) =>
  new Date(fecha).toLocaleDateString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

function ResumenBanner({ ventas, cargando }) {
  const total = ventas.reduce((s, v) => s + v.total, 0)

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center justify-between">
      <div>
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
          Total ingresos
        </p>
        <p className="text-3xl font-bold text-indigo-600">
          {cargando ? '…' : `$${fmt(total)}`}
        </p>
      </div>
      <div className="text-right">
        <p className="text-2xl font-bold text-slate-800">
          {cargando ? '…' : ventas.length}
        </p>
        <p className="text-xs text-slate-400">
          venta{ventas.length !== 1 ? 's' : ''}
        </p>
      </div>
    </div>
  )
}

function ListaVentas({ ventas }) {
  if (ventas.length === 0) {
    return (
      <div className="text-center py-16 text-slate-400">
        <TrendingUp size={40} className="mx-auto mb-3 text-slate-300" />
        <p className="text-sm">Sin ventas en este período</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {ventas.map(venta => (
        <div key={venta.id} className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="flex items-start justify-between mb-3">
            <div>
              <p className="font-semibold text-slate-800 text-sm">{formatFecha(venta.fecha_venta)}</p>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                #{venta.id.split('-')[0]} · {venta.usuario_email}
              </p>
            </div>
            <span className="font-bold text-lg text-indigo-600">${fmt(venta.total)}</span>
          </div>
          <div className="border-t border-slate-100 pt-3 space-y-1">
            {venta.detalles.map(d => (
              <div key={d.id} className="flex justify-between text-sm text-slate-600">
                <span className="truncate mr-2">{d.producto_nombre} × {d.cantidad}</span>
                <span className="shrink-0 font-medium">${fmt(d.subtotal)}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function ExcelExport({ empresaId }) {
  const [descargando, setDescargando] = useState(false)
  const [estado, setEstado] = useState(null)

  const descargar = async () => {
    setDescargando(true)
    setEstado(null)
    try {
      const token = authService.getToken()
      const res = await fetch(`${BASE}/reportes/ventas/excel/${empresaId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error()
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ventas_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      setEstado('ok')
      setTimeout(() => setEstado(null), 4000)
    } catch {
      setEstado('error')
    } finally {
      setDescargando(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <p className="font-semibold text-slate-800 text-sm">Exportar historial completo</p>
          <p className="text-xs text-slate-500 mt-0.5">Descarga todas las ventas en formato Excel</p>
        </div>
        <div className="flex items-center gap-3">
          {estado === 'ok' && (
            <span className="text-xs text-emerald-600 font-medium">Descargado</span>
          )}
          {estado === 'error' && (
            <span className="text-xs text-red-600 font-medium">Error al generar</span>
          )}
          <button
            onClick={descargar}
            disabled={descargando}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white font-semibold px-4 py-2.5 rounded-xl transition-colors text-sm"
          >
            <Download size={14} />
            {descargando ? 'Generando…' : 'Exportar .xlsx'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Reportes() {
  const { usuario } = useAuth()
  const { cargar } = useVentas()
  const [tab, setTab] = useState('hoy')
  const [ventas, setVentas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const cargarVentas = useCallback(async (tabActual) => {
    if (!usuario?.empresa_id) return
    setCargando(true)
    setError(null)
    try {
      const { desde, hasta } = getFechas(tabActual)
      const params = new URLSearchParams({ desde, hasta })
      const res = await authService.fetchAuth(
        `${BASE}/ventas/${usuario.empresa_id}?${params.toString()}`
      )
      if (!res.ok) throw new Error('Error cargando ventas')
      setVentas(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [usuario])

  useEffect(() => {
    cargarVentas(tab)
  }, [tab, cargarVentas])

  const cambiarTab = (id) => {
    setVentas([])
    setTab(id)
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto p-4 sm:p-6 space-y-5">

        <h1 className="text-xl font-bold text-slate-900">Reportes</h1>

        {/* Tabs */}
        <div className="flex gap-1 bg-slate-100 p-1 rounded-xl">
          {TABS.map(t => (
            <button
              key={t.id}
              onClick={() => cambiarTab(t.id)}
              className={`flex-1 py-2 px-2 sm:px-3 rounded-lg text-sm font-medium transition-all ${
                tab === t.id
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <span className="sm:hidden">{t.labelCorto}</span>
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          ))}
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm border border-red-100">
            {error}
          </div>
        )}

        <ResumenBanner ventas={ventas} cargando={cargando} />

        {cargando ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
          </div>
        ) : (
          <ListaVentas ventas={ventas} />
        )}

        {tab === 'historico' && (
          <ExcelExport empresaId={usuario?.empresa_id} />
        )}

      </div>
    </div>
  )
}
