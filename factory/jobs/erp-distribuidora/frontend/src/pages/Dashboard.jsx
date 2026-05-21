import { useState, useEffect } from 'react'
import { TrendingDown, AlertTriangle, CheckCircle, Package, Users, CreditCard } from 'lucide-react'
import authService from '../services/authService'

const fmt = (n) => Number(n ?? 0).toLocaleString('es-CO', { maximumFractionDigits: 0 })

function KpiCard({ label, value, sub, icon: Icon, color, bgColor }) {
  return (
    <div className={`rounded-xl border p-5 ${bgColor || 'bg-white border-slate-200'}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">{label}</p>
          <p className={`text-2xl font-bold ${color || 'text-slate-800'}`}>{value}</p>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <div className="p-2.5 rounded-xl bg-white/60">
          <Icon size={20} className="text-slate-400" />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [kpis, setKpis] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    authService.fetchAuth('/api/dashboard/kpis')
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) setKpis(data) })
      .finally(() => setCargando(false))
  }, [])

  const fin = kpis?.resumen_financiero
  const inv = kpis?.inventario
  const prov = kpis?.proveedores
  const hayVencidas = (fin?.deudas_vencidas ?? 0) > 0

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto p-4 sm:p-6 space-y-6">

        <div>
          <h1 className="text-xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Resumen financiero — {new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
        </div>

        {/* Alerta de deudas vencidas */}
        {!cargando && hayVencidas && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 flex items-start gap-3">
            <AlertTriangle size={18} className="text-red-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-800">Deudas vencidas pendientes</p>
              <p className="text-sm text-red-700 mt-0.5">
                Tienes <strong>${fmt(fin?.deudas_vencidas)}</strong> en obligaciones vencidas con proveedores. Revisa Cuentas por Pagar.
              </p>
            </div>
          </div>
        )}

        {/* KPIs financieros */}
        <div>
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">Finanzas</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <KpiCard
              label="Compras totales"
              value={cargando ? '…' : `$${fmt(fin?.compras_totales)}`}
              sub="en el período"
              icon={TrendingDown}
              color="text-slate-800"
            />
            <KpiCard
              label="Deudas activas"
              value={cargando ? '…' : `$${fmt(fin?.deudas_activas)}`}
              sub="saldo pendiente"
              icon={CreditCard}
              color="text-amber-700"
              bgColor="bg-amber-50 border-amber-200"
            />
            <KpiCard
              label="Deudas vencidas"
              value={cargando ? '…' : `$${fmt(fin?.deudas_vencidas)}`}
              sub="requieren atención"
              icon={AlertTriangle}
              color={hayVencidas ? 'text-red-700' : 'text-slate-400'}
              bgColor={hayVencidas ? 'bg-red-50 border-red-200' : 'bg-white border-slate-200'}
            />
          </div>
        </div>

        {/* KPIs inventario y proveedores */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <Package size={16} className="text-slate-400" />
              <h3 className="text-sm font-semibold text-slate-700">Inventario</h3>
            </div>
            {cargando ? (
              <div className="space-y-2">
                {[1,2].map(n => <div key={n} className="h-6 bg-slate-100 rounded animate-pulse" />)}
              </div>
            ) : (
              <dl className="space-y-2">
                <div className="flex justify-between text-sm">
                  <dt className="text-slate-500">Total productos</dt>
                  <dd className="font-semibold text-slate-800">{fmt(inv?.total_items)}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-slate-500">Valor stock</dt>
                  <dd className="font-semibold text-slate-800">${fmt(inv?.valor_total_stock)}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-slate-500">Rotación promedio</dt>
                  <dd className="font-semibold text-slate-800">{inv?.rotacion_promedio_dias ?? '—'} días</dd>
                </div>
              </dl>
            )}
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center gap-2 mb-4">
              <Users size={16} className="text-slate-400" />
              <h3 className="text-sm font-semibold text-slate-700">Proveedores</h3>
            </div>
            {cargando ? (
              <div className="space-y-2">
                {[1,2,3].map(n => <div key={n} className="h-6 bg-slate-100 rounded animate-pulse" />)}
              </div>
            ) : (
              <dl className="space-y-2">
                <div className="flex justify-between text-sm">
                  <dt className="text-slate-500">Total activos</dt>
                  <dd className="font-semibold text-slate-800">{prov?.total_activos ?? 0}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-slate-500">Con deuda activa</dt>
                  <dd className="font-semibold text-amber-700">{prov?.con_deuda_activa ?? 0}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-slate-500">Con deuda vencida</dt>
                  <dd className={`font-semibold ${(prov?.con_deuda_vencida ?? 0) > 0 ? 'text-red-700' : 'text-slate-400'}`}>
                    {prov?.con_deuda_vencida ?? 0}
                  </dd>
                </div>
              </dl>
            )}
          </div>
        </div>

        {!cargando && !hayVencidas && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 flex items-center gap-3">
            <CheckCircle size={18} className="text-emerald-600 shrink-0" />
            <p className="text-sm text-emerald-800 font-medium">Sin deudas vencidas — obligaciones al día</p>
          </div>
        )}
      </div>
    </div>
  )
}
