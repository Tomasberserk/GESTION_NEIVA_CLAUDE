import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, ShoppingCart, ChevronDown } from 'lucide-react'
import { useCompras } from '../hooks/useCompras'

const fmt = (n) => Number(n ?? 0).toLocaleString('es-CO', { maximumFractionDigits: 0 })

const ESTADO_BADGE = {
  PAGADA:   'bg-emerald-100 text-emerald-700',
  PENDIENTE:'bg-amber-100 text-amber-700',
  ANULADA:  'bg-slate-100 text-slate-500',
}

const ESTADOS = ['', 'PAGADA', 'PENDIENTE', 'ANULADA']

function fmtFecha(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

export default function Compras() {
  const navigate = useNavigate()
  const { compras, total, cargando, cargar, anular } = useCompras()
  const [estadoFiltro, setEstadoFiltro] = useState('')

  useEffect(() => { cargar({ estado: estadoFiltro || undefined }) }, [cargar, estadoFiltro])

  const handleAnular = async (c) => {
    if (!confirm(`¿Anular compra ${c.numero_factura || c.id.slice(0, 8)}?\nEsto reversará el stock automáticamente.`)) return
    try {
      await anular(c.id)
      cargar({ estado: estadoFiltro || undefined })
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Toolbar */}
      <div className="bg-white border-b border-slate-200 px-4 sm:px-6 py-4 shrink-0">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-bold text-slate-900">Historial de Compras</h1>
            <p className="text-xs text-slate-500 mt-0.5">{total} compras registradas</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <select
                value={estadoFiltro}
                onChange={e => setEstadoFiltro(e.target.value)}
                className="appearance-none pl-3 pr-8 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
              >
                {ESTADOS.map(e => <option key={e} value={e}>{e || 'Todos los estados'}</option>)}
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            </div>
            <button
              onClick={() => navigate('/compras/nueva')}
              className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-medium whitespace-nowrap"
            >
              <Plus size={15} />
              <span className="hidden sm:inline">Nueva compra</span>
            </button>
          </div>
        </div>
      </div>

      {/* Lista */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        {cargando ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
          </div>
        ) : compras.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400">
            <ShoppingCart size={32} className="mb-3" />
            <p className="text-sm">Sin compras registradas</p>
            <button
              onClick={() => navigate('/compras/nueva')}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-xl text-sm font-medium hover:bg-indigo-700"
            >
              Registrar primera compra
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {compras.map(c => (
              <div key={c.id} className="bg-white rounded-xl border border-slate-200 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <p className="font-semibold text-slate-900 text-sm">
                        {c.numero_factura || `#${c.id.slice(0, 8)}`}
                      </p>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ESTADO_BADGE[c.estado] || 'bg-slate-100 text-slate-500'}`}>
                        {c.estado}
                      </span>
                      <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                        {c.metodo_pago}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600 mb-1">{c.proveedor?.razon_social || '—'}</p>
                    <div className="flex gap-4 text-xs text-slate-400">
                      <span>Fecha: {fmtFecha(c.fecha_compra)}</span>
                      {c.fecha_vencimiento && <span>Vence: {fmtFecha(c.fecha_vencimiento)}</span>}
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-lg font-bold text-slate-900">${fmt(c.total)}</p>
                    {c.estado !== 'ANULADA' && (
                      <button
                        onClick={() => handleAnular(c)}
                        className="text-xs text-red-500 hover:text-red-700 mt-1 transition-colors"
                      >
                        Anular
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
