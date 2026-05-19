import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

const TABS = [
  { id: 'hoy',       label: 'Hoy',      labelCorto: 'Hoy' },
  { id: 'semana',    label: 'Esta Semana', labelCorto: 'Semana' },
  { id: 'historico', label: 'Histórico y Reportes', labelCorto: 'Histórico' },
]

function getFechas(tab) {
  const ahora = new Date()
  const fin = ahora.toISOString()
  const inicio = new Date(ahora)

  if (tab === 'hoy') {
    inicio.setHours(0, 0, 0, 0)
  } else if (tab === 'semana') {
    const dayOfWeek = inicio.getDay() || 7 // Convertir Domingo (0) a 7
    inicio.setDate(inicio.getDate() - (dayOfWeek - 1)) // Retroceder hasta el Lunes
    inicio.setHours(0, 0, 0, 0)
  } else {
    inicio.setDate(inicio.getDate() - 30)
    inicio.setHours(0, 0, 0, 0)
  }

  return { fecha_inicio: inicio.toISOString(), fecha_fin: fin }
}

const fmt = (n) => Number(n).toLocaleString('es-CO', { maximumFractionDigits: 0 })

const formatFecha = (fecha) =>
  new Date(fecha).toLocaleDateString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })

function TotalBanner({ tab, ventas, cargando }) {
  const total = ventas.reduce((s, v) => s + v.total, 0)
  const labels = {
    hoy:       'Total ingresos hoy',
    semana:    'Total esta semana',
    historico: 'Total últimos 30 días',
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 mb-5 flex items-center justify-between">
      <div>
        <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">{labels[tab]}</p>
        <p className="text-4xl font-bold text-violet-600">
          {cargando ? '…' : `$${fmt(total)}`}
        </p>
      </div>
      <div className="text-right">
        <p className="text-2xl font-bold text-slate-800">
          {cargando ? '…' : ventas.length}
        </p>
        <p className="text-xs text-slate-400">venta{ventas.length !== 1 ? 's' : ''}</p>
      </div>
    </div>
  )
}

function ListaVentas({ ventas }) {
  if (ventas.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400">
        <div className="text-5xl mb-3">📋</div>
        <p className="text-sm">Sin ventas en este período</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {ventas.map(venta => (
        <div key={venta.id} className="bg-white rounded-xl border border-slate-200 p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="font-semibold text-gray-800 text-sm">{formatFecha(venta.fecha_venta)}</p>
              <p className="text-xs text-gray-400 font-mono mt-0.5">#{venta.id.split('-')[0]}</p>
            </div>
            <span className="font-bold text-lg text-violet-600">
              ${fmt(venta.total)}
            </span>
          </div>
          <div className="border-t pt-3 space-y-1">
            {venta.detalles.map(d => (
              <div key={d.id} className="flex justify-between text-sm text-gray-600">
                <span className="truncate mr-2">
                  {d.producto_nombre} × {Number(d.cantidad).toLocaleString('es-CO', { maximumFractionDigits: 3 })}
                </span>
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
  const [estado, setEstado]   = useState(null) // 'ok' | 'error' | null

  const descargar = async () => {
    setDescargando(true)
    setEstado(null)
    try {
      const token = authService.getToken()
      const res = await fetch(`${BASE}/reportes/ventas/excel/${empresaId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Error generando el reporte')
      const blob = await res.blob()
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
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
    <div className="bg-white rounded-xl border border-slate-200 p-5 mt-5">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <p className="font-semibold text-slate-800">Exportar a Excel</p>
          <p className="text-sm text-slate-500 mt-0.5">
            Descarga el historial completo de ventas (.xlsx)
          </p>
        </div>
        <div className="flex items-center gap-3">
          {estado === 'ok' && (
            <span className="text-sm text-green-600 font-medium">✅ Descargado</span>
          )}
          {estado === 'error' && (
            <span className="text-sm text-red-600 font-medium">❌ Error al generar</span>
          )}
          <button
            onClick={descargar}
            disabled={descargando}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-200 disabled:cursor-not-allowed text-white font-semibold px-5 py-2.5 rounded-lg transition-colors text-sm"
          >
            {descargando ? '⏳ Generando…' : '⬇ Exportar Excel'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Ventas() {
  const { usuario } = useAuth()
  const [tab,      setTab]      = useState('hoy')
  const [ventas,   setVentas]   = useState([])
  const [cargando, setCargando] = useState(true)
  const [error,    setError]    = useState(null)

  const cargar = useCallback(async (tabActual) => {
    if (!usuario?.empresa_id) return
    setCargando(true)
    setError(null)
    try {
      const { fecha_inicio, fecha_fin } = getFechas(tabActual)
      const url = new URL(`${BASE}/ventas/${usuario.empresa_id}`)
      url.searchParams.set('fecha_inicio', fecha_inicio)
      url.searchParams.set('fecha_fin',    fecha_fin)
      const res = await authService.fetchAuth(url.toString())
      if (!res.ok) throw new Error('Error cargando ventas')
      setVentas(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [usuario])

  useEffect(() => {
    cargar(tab)
  }, [tab, cargar])

  const cambiarTab = (id) => {
    setVentas([])
    setTab(id)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-5">Ventas</h1>

      {/* Tabs — segmented control */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl mb-5">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => cambiarTab(t.id)}
            className={`flex-1 py-2 px-2 sm:px-3 rounded-lg text-sm font-medium transition-all ${
              tab === t.id
                ? 'bg-white text-violet-700 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <span className="sm:hidden">{t.labelCorto}</span>
            <span className="hidden sm:inline">{t.label}</span>
          </button>
        ))}
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4 text-sm">{error}</div>
      )}

      <TotalBanner tab={tab} ventas={ventas} cargando={cargando} />

      {cargando ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-500" />
        </div>
      ) : (
        <ListaVentas ventas={ventas} />
      )}

      {tab === 'historico' && (
        <ExcelExport empresaId={usuario?.empresa_id} />
      )}
    </div>
  )
}
