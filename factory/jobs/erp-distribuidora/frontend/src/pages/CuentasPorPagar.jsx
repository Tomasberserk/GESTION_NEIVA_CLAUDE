import { useState, useEffect, useCallback } from 'react'
import { CreditCard, AlertTriangle, Clock, CheckCircle, X, ChevronDown, DollarSign } from 'lucide-react'
import { useCuentasPorPagar } from '../hooks/useCuentasPorPagar'

const fmt = (n) => Number(n ?? 0).toLocaleString('es-CO', { maximumFractionDigits: 0 })

const METODOS_ABONO = ['EFECTIVO', 'TRANSFERENCIA', 'CHEQUE']

function badgeEstado(estado, diasVence) {
  if (estado === 'PAGADA') return { cls: 'bg-emerald-100 text-emerald-700', label: 'PAGADA', icon: CheckCircle }
  if (estado === 'VENCIDA' || (diasVence !== null && diasVence < 0))
    return { cls: 'bg-red-100 text-red-700', label: 'VENCIDA', icon: AlertTriangle }
  if (diasVence !== null && diasVence < 7)
    return { cls: 'bg-amber-100 text-amber-700', label: `Vence en ${diasVence}d`, icon: Clock }
  return { cls: 'bg-slate-100 text-slate-600', label: 'PENDIENTE', icon: Clock }
}

function fmtFecha(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function calcDias(fechaIso) {
  if (!fechaIso) return null
  const diff = new Date(fechaIso) - new Date()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

function ModalAbono({ cxp, onRegistrar, onCerrar }) {
  const [form, setForm] = useState({ monto: '', metodo_pago: 'EFECTIVO', nota: '' })
  const [error, setError] = useState('')
  const [guardando, setGuardando] = useState(false)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    const monto = parseFloat(form.monto)
    if (!monto || monto <= 0) { setError('Monto inválido'); return }
    if (monto > cxp.saldo_pendiente) {
      setError(`El monto no puede superar el saldo pendiente ($${fmt(cxp.saldo_pendiente)})`)
      return
    }
    setGuardando(true)
    try {
      await onRegistrar(cxp.id, { monto, metodo_pago: form.metodo_pago, nota: form.nota || null })
      onCerrar()
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div>
            <h2 className="font-semibold text-slate-900">Registrar abono</h2>
            <p className="text-xs text-slate-500 mt-0.5">{cxp.proveedor?.razon_social}</p>
          </div>
          <button onClick={onCerrar} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
        </div>

        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
          <div className="flex justify-between text-sm">
            <span className="text-slate-500">Deuda total</span>
            <span className="font-medium text-slate-800">${fmt(cxp.monto_total)}</span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-slate-500">Saldo pendiente</span>
            <span className="font-bold text-amber-700">${fmt(cxp.saldo_pendiente)}</span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-slate-500">Vencimiento</span>
            <span className="text-slate-700">{fmtFecha(cxp.fecha_vencimiento)}</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <p className="text-sm text-red-600 bg-red-50 rounded-lg p-3">{error}</p>}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Monto del abono *</label>
            <div className="relative">
              <DollarSign size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="number"
                min="0.01"
                max={cxp.saldo_pendiente}
                step="any"
                required
                value={form.monto}
                onChange={set('monto')}
                placeholder={`Máx: $${fmt(cxp.saldo_pendiente)}`}
                className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </div>
            <button
              type="button"
              onClick={() => setForm(f => ({ ...f, monto: cxp.saldo_pendiente }))}
              className="text-xs text-indigo-600 hover:underline mt-1"
            >
              Pagar saldo completo (${fmt(cxp.saldo_pendiente)})
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Método de pago</label>
            <div className="relative">
              <select
                value={form.metodo_pago}
                onChange={set('metodo_pago')}
                className="w-full appearance-none px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
              >
                {METODOS_ABONO.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
              <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Nota / referencia</label>
            <input
              type="text"
              value={form.nota}
              onChange={set('nota')}
              placeholder="Ej: Transferencia Bancolombia Ref: #48109"
              className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onCerrar} className="flex-1 py-2.5 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50">
              Cancelar
            </button>
            <button type="submit" disabled={guardando} className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-medium">
              {guardando ? 'Registrando...' : 'Registrar abono'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function CuentasPorPagar() {
  const { cuentas, total, cargando, cargar, registrarAbono } = useCuentasPorPagar()
  const [estadoFiltro, setEstadoFiltro] = useState('')
  const [cxpAbono, setCxpAbono] = useState(null)

  const recargar = useCallback(() => {
    cargar({ estado: estadoFiltro || undefined })
  }, [cargar, estadoFiltro])

  useEffect(() => { recargar() }, [recargar])

  const handleAbono = async (cxpId, payload) => {
    await registrarAbono(cxpId, payload)
    recargar()
  }

  // KPIs calculados localmente
  const totalDeudas = cuentas.reduce((s, c) => s + (c.saldo_pendiente ?? 0), 0)
  const totalVencidas = cuentas.filter(c => {
    const dias = calcDias(c.fecha_vencimiento)
    return c.estado === 'VENCIDA' || (dias !== null && dias < 0)
  }).reduce((s, c) => s + (c.saldo_pendiente ?? 0), 0)
  const totalAbonado = cuentas.reduce((s, c) => s + ((c.monto_total ?? 0) - (c.saldo_pendiente ?? 0)), 0)

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Toolbar */}
      <div className="bg-white border-b border-slate-200 px-4 sm:px-6 py-4 shrink-0">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-bold text-slate-900">Cuentas por Pagar</h1>
            <p className="text-xs text-slate-500 mt-0.5">{total} obligaciones</p>
          </div>
          <div className="relative">
            <select
              value={estadoFiltro}
              onChange={e => setEstadoFiltro(e.target.value)}
              className="appearance-none pl-3 pr-8 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
            >
              <option value="">Todos</option>
              <option value="PENDIENTE">PENDIENTE</option>
              <option value="VENCIDA">VENCIDA</option>
              <option value="PAGADA">PAGADA</option>
            </select>
            <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
        {/* KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Total deudas</p>
            <p className="text-2xl font-bold text-slate-900">${fmt(totalDeudas)}</p>
            <p className="text-xs text-slate-400 mt-1">saldo pendiente acumulado</p>
          </div>
          <div className={`rounded-xl border p-4 ${totalVencidas > 0 ? 'bg-red-50 border-red-200' : 'bg-white border-slate-200'}`}>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Deudas vencidas</p>
            <p className={`text-2xl font-bold ${totalVencidas > 0 ? 'text-red-700' : 'text-slate-400'}`}>${fmt(totalVencidas)}</p>
            <p className="text-xs text-slate-400 mt-1">requieren pago urgente</p>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Abonado total</p>
            <p className="text-2xl font-bold text-emerald-700">${fmt(totalAbonado)}</p>
            <p className="text-xs text-slate-400 mt-1">pagado a proveedores</p>
          </div>
        </div>

        {/* Lista */}
        {cargando ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
          </div>
        ) : cuentas.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400">
            <CreditCard size={32} className="mb-3" />
            <p className="text-sm">Sin cuentas por pagar</p>
          </div>
        ) : (
          <div className="space-y-3">
            {cuentas.map(cxp => {
              const dias = calcDias(cxp.fecha_vencimiento)
              const badge = badgeEstado(cxp.estado, dias)
              const BadgeIcon = badge.icon
              const pct = cxp.monto_total > 0
                ? Math.round(((cxp.monto_total - cxp.saldo_pendiente) / cxp.monto_total) * 100)
                : 0

              return (
                <div
                  key={cxp.id}
                  className={`bg-white rounded-xl border p-4 ${
                    cxp.estado === 'VENCIDA' || (dias !== null && dias < 0)
                      ? 'border-red-200'
                      : dias !== null && dias < 7 && cxp.estado !== 'PAGADA'
                      ? 'border-amber-200'
                      : 'border-slate-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <p className="font-semibold text-slate-900 text-sm">{cxp.proveedor?.razon_social || '—'}</p>
                        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium ${badge.cls}`}>
                          <BadgeIcon size={10} />
                          {badge.label}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mb-2">Vence: {fmtFecha(cxp.fecha_vencimiento)}</p>

                      {/* Barra de progreso */}
                      <div className="w-full bg-slate-100 rounded-full h-1.5 mb-1">
                        <div
                          className="bg-emerald-500 h-1.5 rounded-full transition-all"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <p className="text-xs text-slate-400">{pct}% pagado</p>
                    </div>

                    <div className="text-right shrink-0 space-y-1">
                      <div>
                        <p className="text-xs text-slate-400">Total deuda</p>
                        <p className="text-sm font-medium text-slate-700">${fmt(cxp.monto_total)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Saldo pendiente</p>
                        <p className="text-base font-bold text-amber-700">${fmt(cxp.saldo_pendiente)}</p>
                      </div>
                      {cxp.estado !== 'PAGADA' && (
                        <button
                          onClick={() => setCxpAbono(cxp)}
                          className="mt-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-medium transition-colors"
                        >
                          Registrar abono
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {cxpAbono && (
        <ModalAbono
          cxp={cxpAbono}
          onRegistrar={handleAbono}
          onCerrar={() => setCxpAbono(null)}
        />
      )}
    </div>
  )
}
