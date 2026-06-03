import { useState, useEffect } from 'react'
import { Rocket, CheckCircle, Clock, ExternalLink, Loader2, AlertTriangle } from 'lucide-react'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

export default function FabricaApps() {
  const [empresa, setEmpresa] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [solicitando, setSolicitando] = useState(false)
  const [lanzando, setLanzando] = useState(false)
  const [mensaje, setMensaje] = useState(null) // { tipo: 'ok'|'error', texto: '' }

  async function cargarEmpresa() {
    try {
      const res = await authService.fetchAuth(`${BASE}/empresas/mi-empresa`)
      if (res.ok) setEmpresa(await res.json())
    } catch {
      // silencioso — empresa quedará null
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => { cargarEmpresa() }, [])

  async function solicitarUpgrade() {
    setSolicitando(true)
    setMensaje(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/soporte/solicitar-upgrade`, { method: 'POST' })
      const data = await res.json().catch(() => ({}))
      if (res.ok) {
        setMensaje({ tipo: 'ok', texto: data.mensaje || 'Solicitud enviada correctamente.' })
        await cargarEmpresa()
      } else {
        setMensaje({ tipo: 'error', texto: data.detail || 'Error al enviar la solicitud.' })
      }
    } catch {
      setMensaje({ tipo: 'error', texto: 'Error de conexión.' })
    } finally {
      setSolicitando(false)
    }
  }

  async function lanzarERP() {
    if (lanzando || !empresa?.factory_url) return
    setLanzando(true)
    setMensaje(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/sso/token`, { method: 'POST' })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setMensaje({ tipo: 'error', texto: data.detail || 'Error al generar acceso SSO.' })
        return
      }
      const url = `${empresa.factory_url}?sso_token=${data.token}`
      window.open(url, '_blank', 'noopener,noreferrer')
    } catch {
      setMensaje({ tipo: 'error', texto: 'Error de conexión.' })
    } finally {
      setLanzando(false)
    }
  }

  function formatFecha(iso) {
    if (!iso) return '—'
    try {
      return new Date(iso).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })
    } catch { return iso }
  }

  function diasRestantes(iso) {
    if (!iso) return null
    const diff = new Date(iso) - new Date()
    return Math.max(0, Math.ceil(diff / 86400000))
  }

  if (cargando) {
    return (
      <div className="flex items-center justify-center h-full py-24 text-slate-400">
        <Loader2 size={28} className="animate-spin mr-3" />
        Cargando...
      </div>
    )
  }

  const trialDias = diasRestantes(empresa?.factory_trial_expires_at)

  return (
    <div className="max-w-2xl mx-auto py-10 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Rocket size={24} className="text-indigo-500" />
          Fábrica de Apps
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Amplía tu negocio con módulos adicionales generados por IA.
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
        <p className="text-slate-600 text-sm">
          Plan Basic — POS para tiendas de barrio con inventario, ventas y reportes.
        </p>
      </div>

      {/* Módulo ERP Distribuidora */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="font-semibold text-slate-800">ERP Distribuidora — Plan Medium</h2>
            <p className="text-slate-500 text-sm mt-0.5">
              Proveedores, compras a crédito, cuentas por pagar y más.
            </p>
          </div>
          {empresa?.factory_activa ? (
            <span className="text-xs bg-emerald-100 text-emerald-700 font-semibold px-2.5 py-1 rounded-full shrink-0 ml-3">
              Activo
            </span>
          ) : empresa?.factory_upgrade_solicitado ? (
            <span className="text-xs bg-amber-100 text-amber-700 font-semibold px-2.5 py-1 rounded-full shrink-0 ml-3">
              Pendiente
            </span>
          ) : (
            <span className="text-xs bg-slate-100 text-slate-500 font-semibold px-2.5 py-1 rounded-full shrink-0 ml-3">
              No activo
            </span>
          )}
        </div>

        {/* Estado activo — mostrar launcher */}
        {empresa?.factory_activa && (
          <div className="bg-emerald-50 rounded-xl p-4 space-y-3">
            <div className="flex items-center gap-2 text-emerald-700 text-sm font-medium">
              <CheckCircle size={16} />
              Trial activo
              {trialDias !== null && (
                <span className="ml-auto text-xs text-emerald-600">
                  {trialDias} día{trialDias !== 1 ? 's' : ''} restante{trialDias !== 1 ? 's' : ''}
                </span>
              )}
            </div>
            <p className="text-xs text-emerald-600">Vence: {formatFecha(empresa.factory_trial_expires_at)}</p>
            <button
              onClick={lanzarERP}
              disabled={lanzando}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-xl transition-colors text-sm"
            >
              {lanzando ? <Loader2 size={16} className="animate-spin" /> : <ExternalLink size={16} />}
              Abrir ERP Distribuidora
            </button>
          </div>
        )}

        {/* Estado pendiente — esperando activación */}
        {!empresa?.factory_activa && empresa?.factory_upgrade_solicitado && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
            <Clock size={18} className="text-amber-500 shrink-0 mt-0.5" />
            <p className="text-amber-700 text-sm">
              Tu solicitud fue recibida. El equipo de soporte activará el trial en breve.
            </p>
          </div>
        )}

        {/* Estado no solicitado — mostrar botón de solicitud */}
        {!empresa?.factory_upgrade_solicitado && (
          <div className="space-y-2">
            <div className="text-sm text-slate-500">
              <strong>8 días gratis.</strong> Sin tarjeta de crédito. El equipo activa el acceso en 24 horas.
            </div>
            <button
              onClick={solicitarUpgrade}
              disabled={solicitando}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-xl transition-colors text-sm"
            >
              {solicitando ? <Loader2 size={16} className="animate-spin" /> : <Rocket size={16} />}
              Solicitar trial de 8 días
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
