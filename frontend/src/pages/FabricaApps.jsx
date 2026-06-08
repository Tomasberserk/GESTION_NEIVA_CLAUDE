import { useState, useEffect } from 'react'
import { Rocket, CheckCircle, Clock, Loader2, AlertTriangle } from 'lucide-react'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

export default function FabricaApps() {
  const [empresa, setEmpresa] = useState(null)
  const [solicitado, setSolicitado] = useState(false)
  const [cargando, setCargando] = useState(true)
  const [solicitando, setSolicitando] = useState(false)
  const [mensaje, setMensaje] = useState(null) // { tipo: 'ok'|'error', texto: '' }

  async function cargarDatos() {
    try {
      const [resEmpresa, resTickets] = await Promise.all([
        authService.fetchAuth(`${BASE}/empresas/mi-empresa`),
        authService.fetchAuth(`${BASE}/soporte/tickets`),
      ])
      if (resEmpresa.ok) {
        const emp = await resEmpresa.json()
        setEmpresa(emp)
      }
      if (resTickets.ok) {
        const tickets = await resTickets.json()
        const tieneSolicitud = tickets.some(
          (t) => t.asunto === 'Solicitud de upgrade a Plan Medium (ERP Distribuidora)' && t.estado !== 'cerrado'
        )
        setSolicitado(tieneSolicitud)
      }
    } catch {
      // silencioso
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargarDatos()
  }, [])

  async function solicitarUpgrade() {
    setSolicitando(true)
    setMensaje(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/soporte/solicitar-upgrade`, { method: 'POST' })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        setMensaje({ tipo: 'ok', texto: data.mensaje || 'Solicitud enviada correctamente.' })
        await cargarDatos()
      } else {
        setMensaje({ tipo: 'error', texto: data.detail || 'Error al enviar la solicitud.' })
      }
    } catch {
      setMensaje({ tipo: 'error', texto: 'Error de conexión.' })
    } finally {
      setSolicitando(false)
    }
  }

  if (cargando) {
    return (
      <div className="flex items-center justify-center h-full py-24 text-slate-400">
        <Loader2 size={28} className="animate-spin mr-3" />
        Cargando...
      </div>
    )
  }

  const esPlanMediumOPremium = empresa?.plan === 'medium' || empresa?.plan === 'premium'

  return (
    <div className="max-w-2xl mx-auto py-10 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Rocket size={24} className="text-indigo-500" />
          Fábrica de Apps
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Amplía tu negocio con módulos adicionales integrados en el POS.
        </p>
      </div>

      {/* Plan actual */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Tu plan actual</span>
          <span className="text-xs bg-indigo-100 text-indigo-700 font-semibold px-2.5 py-0.5 rounded-full capitalize">
            {empresa?.plan || 'Basic'}
          </span>
        </div>
        <p className="text-slate-600 text-sm font-medium">
          {esPlanMediumOPremium 
            ? 'Plan Medium — Disfruta de la integración del ERP Distribuidora con compras, proveedores y cuentas por pagar.'
            : 'Plan Basic — POS para tiendas de barrio con inventario, ventas y reportes.'
          }
        </p>
      </div>

      {/* Módulo ERP Distribuidora */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="font-semibold text-slate-800 text-base">ERP Distribuidora — Plan Medium</h2>
            <p className="text-slate-500 text-sm mt-0.5">
              Administración de proveedores, compras a crédito y deudas (cuentas por pagar).
            </p>
          </div>
          {esPlanMediumOPremium ? (
            <span className="text-xs bg-emerald-100 text-emerald-700 font-semibold px-2.5 py-1 rounded-full shrink-0 ml-3">
              Activo
            </span>
          ) : solicitado ? (
            <span className="text-xs bg-amber-100 text-amber-700 font-semibold px-2.5 py-1 rounded-full shrink-0 ml-3">
              Pendiente
            </span>
          ) : (
            <span className="text-xs bg-slate-100 text-slate-500 font-semibold px-2.5 py-1 rounded-full shrink-0 ml-3">
              No activo
            </span>
          )}
        </div>

        {/* Estado activo */}
        {esPlanMediumOPremium && (
          <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-4 space-y-2">
            <div className="flex items-center gap-2 text-emerald-700 text-sm font-semibold">
              <CheckCircle size={16} />
              Módulo ERP Integrado
            </div>
            <p className="text-xs text-emerald-600">
              Los menús de <strong>Proveedores</strong>, <strong>Compras</strong> y <strong>Cuentas por Pagar</strong> ya están habilitados directamente en tu menú lateral izquierdo.
            </p>
          </div>
        )}

        {/* Estado pendiente — esperando activación */}
        {!esPlanMediumOPremium && solicitado && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
            <Clock size={18} className="text-amber-500 shrink-0 mt-0.5" />
            <p className="text-amber-700 text-sm">
              Tu solicitud fue recibida. El equipo de soporte activará el módulo en breve y te notificará por el ticket.
            </p>
          </div>
        )}

        {/* Estado no solicitado — mostrar botón de solicitud */}
        {!esPlanMediumOPremium && !solicitado && (
          <div className="space-y-2">
            <div className="text-sm text-slate-500">
              <strong>Prueba gratis por 8 días.</strong> Solicita la activación y el equipo de soporte lo habilitará directamente en tu POS.
            </div>
            <button
              onClick={solicitarUpgrade}
              disabled={solicitando}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-xl transition-colors text-sm"
            >
              {solicitando ? <Loader2 size={16} className="animate-spin" /> : <Rocket size={16} />}
              Solicitar activación de prueba (8 días)
            </button>
          </div>
        )}
      </div>

      {/* Mensaje de feedback */}
      {mensaje && (
        <div
          className={`rounded-xl px-4 py-3 text-sm flex items-start gap-2 ${
            mensaje.tipo === 'ok'
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}
        >
          {mensaje.tipo === 'error' && <AlertTriangle size={16} className="shrink-0 mt-0.5" />}
          {mensaje.texto}
        </div>
      )}
    </div>
  )
}
