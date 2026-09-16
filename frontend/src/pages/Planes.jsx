import { useState, useEffect } from 'react'
import {
  Sparkles,
  Check,
  Mic,
  MessageSquare,
  Bot,
  ShieldCheck,
  Clock,
  Loader2,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Volume2,
  Zap,
} from 'lucide-react'
import authService from '../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

export default function Planes() {
  const [empresa, setEmpresa] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [solicitando, setSolicitando] = useState(false)
  const [solicitudEnviada, setSolicitudEnviada] = useState(false)
  const [modalAbierto, setModalAbierto] = useState(false)
  const [periodoFacturacion, setPeriodoFacturacion] = useState('mensual') // 'mensual' | 'anual'
  const [mensaje, setMensaje] = useState(null) // { tipo: 'ok' | 'error', texto: '' }

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
          (t) =>
            t.asunto &&
            t.asunto.toLowerCase().includes('solicitud de upgrade') &&
            t.estado !== 'cerrado'
        )
        setSolicitudEnviada(tieneSolicitud)
      }
    } catch {
      // manejo silencioso
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargarDatos()
  }, [])

  async function handleSolicitarUpgrade() {
    setSolicitando(true)
    setMensaje(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/soporte/solicitar-upgrade`, {
        method: 'POST',
      })
      const data = await res.json().catch(() => ({}))

      if (res.ok) {
        setSolicitudEnviada(true)
        setMensaje({
          tipo: 'ok',
          texto:
            '¡Solicitud enviada exitosamente! Nuestro equipo activará tu Plan Pro y te contactará en breve.',
        })
        setModalAbierto(false)
        await cargarDatos()
      } else if (res.status === 409) {
        setSolicitudEnviada(true)
        setMensaje({
          tipo: 'info',
          texto: 'Ya tienes una solicitud de activación en revisión por el equipo.',
        })
        setModalAbierto(false)
      } else {
        setMensaje({
          tipo: 'error',
          texto: data.detail || 'Hubo un inconveniente al enviar la solicitud.',
        })
      }
    } catch {
      setMensaje({
        tipo: 'error',
        texto: 'Error de conexión con el servidor. Intenta de nuevo.',
      })
    } finally {
      setSolicitando(false)
    }
  }

  const esPlanPro = empresa?.plan === 'pro' || empresa?.plan === 'premium'

  const caracteristicasBasico = [
    'Punto de Venta (POS) rápido y recibos de venta',
    'Catálogo de productos e inventario en tiempo real',
    'Lector y escáner de código de barras integrado',
    'Métricas clave: ventas hoy, ingresos y alertas de stock',
    'Historial de transacciones y cierres de turno',
    'Soporte técnico estándar vía tickets en plataforma',
  ]

  const caracteristicasPro = [
    {
      titulo: 'Asistente de Voz Bidireccional (Modo Mostrador)',
      descripcion:
        'Opera tu tienda con manos libres: la IA te escucha y te responde por voz en vivo para registrar ventas y consultar stock.',
      icono: Mic,
    },
    {
      titulo: 'Chatbot Inteligente Especializado',
      descripcion:
        'Pregúntale en lenguaje natural por arqueos, productos más vendidos y auditoría de tu inventario al instante.',
      icono: MessageSquare,
    },
    {
      titulo: 'Modo Mostrador Inmersivo a Pantalla Completa',
      descripcion:
        'Interfaz visual optimizada para móviles y tablets apoyados en mostrador con activación táctil y por voz continua.',
      icono: Zap,
    },
    {
      titulo: 'Auditoría y Comandos de Voz Avanzados',
      descripcion:
        'Reconocimiento nativo de modismos colombianos con validación de seguridad antes de cualquier mutación.',
      icono: Volume2,
    },
    {
      titulo: 'Alertas y Análisis Predictivo de Stock',
      descripcion:
        'Sugerencias inteligentes de reabastecimiento antes de que se agoten tus productos de alta rotación.',
      icono: TrendingUp,
    },
    {
      titulo: 'Soporte Prioritario y Asesoría Personalizada',
      descripcion:
        'Acompañamiento VIP en la configuración de la IA y canal preferente de atención.',
      icono: ShieldCheck,
    },
  ]

  if (cargando) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center text-slate-400 bg-[#0c1017] rounded-3xl">
        <Loader2 size={36} className="animate-spin text-blue-500 mb-3" />
        <p className="text-sm font-medium text-slate-300">Cargando planes disponibles...</p>
      </div>
    )
  }

  return (
    <div className="min-h-full bg-[#0c1017] text-slate-100 rounded-3xl p-6 sm:p-10 border border-slate-800/80 shadow-2xl">
      {/* Encabezado Principal */}
      <div className="max-w-4xl mx-auto text-center space-y-4 mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles size={14} className="animate-pulse" />
          Planes y Suscripción
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white font-sans">
          Cambia a un plan superior
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto font-normal">
          Optimiza tu negocio con herramientas de Punto de Venta ágiles y desbloquea el poder de la
          Inteligencia Artificial con asistente de voz y chatbot en vivo.
        </p>

        {/* Toggle de facturación mensual / anual */}
        <div className="pt-2 flex justify-center">
          <div className="bg-[#161c28] p-1 rounded-full border border-slate-800 inline-flex items-center">
            <button
              onClick={() => setPeriodoFacturacion('mensual')}
              className={`px-5 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all ${
                periodoFacturacion === 'mensual'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Mensual
            </button>
            <button
              onClick={() => setPeriodoFacturacion('anual')}
              className={`px-5 py-2 rounded-full text-xs sm:text-sm font-semibold transition-all flex items-center gap-1.5 ${
                periodoFacturacion === 'anual'
                  ? 'bg-slate-800 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Anual
              <span className="text-[11px] bg-blue-500/20 text-blue-400 font-bold px-2 py-0.5 rounded-full border border-blue-500/30">
                Ahorra 15%
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Notificación de feedback si aplica */}
      {mensaje && (
        <div className="max-w-4xl mx-auto mb-8">
          <div
            className={`rounded-2xl p-4 text-sm flex items-center justify-between border ${
              mensaje.tipo === 'ok'
                ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
                : mensaje.tipo === 'info'
                ? 'bg-amber-950/40 border-amber-500/30 text-amber-300'
                : 'bg-red-950/40 border-red-500/30 text-red-300'
            }`}
          >
            <div className="flex items-center gap-3">
              {mensaje.tipo === 'ok' ? (
                <Check size={18} className="text-emerald-400 shrink-0" />
              ) : (
                <Clock size={18} className="text-amber-400 shrink-0" />
              )}
              <span>{mensaje.texto}</span>
            </div>
            <button
              onClick={() => setMensaje(null)}
              className="text-xs opacity-70 hover:opacity-100 underline ml-4"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Tarjetas de Planes */}
      <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch">
        {/* Tarjeta: Plan Básico */}
        <div className="bg-[#121722] border border-slate-800/90 rounded-3xl p-7 sm:p-8 flex flex-col justify-between transition-all hover:border-slate-700/80">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Plan Básico
              </span>
              {!esPlanPro && (
                <span className="text-xs font-medium px-3 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  Tu plan actual
                </span>
              )}
            </div>

            <h3 className="text-2xl font-bold text-white mb-2">POS Esencial</h3>
            <p className="text-sm text-slate-400 mb-6 leading-relaxed">
              Descubre cómo la plataforma te ayuda a ordenar tu tienda, registrar ventas en segundos
              y controlar tu stock.
            </p>

            {/* Precio */}
            <div className="mb-6">
              <div className="flex items-baseline gap-1">
                <span className="text-3xl sm:text-4xl font-extrabold text-white">$0</span>
                <span className="text-sm text-slate-400 font-medium">/ mes</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">Incluido para siempre con tu cuenta</p>
            </div>

            {/* Botón CTA Básico */}
            <div className="mb-8">
              {!esPlanPro ? (
                <button
                  disabled
                  className="w-full py-3 px-4 rounded-xl bg-slate-800/80 text-slate-400 text-sm font-semibold cursor-default border border-slate-700/50"
                >
                  Tu plan actual
                </button>
              ) : (
                <button
                  disabled
                  className="w-full py-3 px-4 rounded-xl bg-slate-800/40 text-slate-400 text-sm font-semibold cursor-default border border-slate-800"
                >
                  Plan base incluido
                </button>
              )}
            </div>

            {/* Desglose de características */}
            <div className="space-y-3 pt-4 border-t border-slate-800/80">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Empieza por lo básico:
              </p>
              <ul className="space-y-3">
                {caracteristicasBasico.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-sm text-slate-300">
                    <Check size={16} className="text-slate-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Tarjeta: Plan Pro (Gestión Inteligente) */}
        <div className="relative bg-gradient-to-b from-[#141d2f] to-[#101624] border-2 border-blue-500/50 rounded-3xl p-7 sm:p-8 flex flex-col justify-between shadow-2xl shadow-blue-500/10 transition-all hover:border-blue-400/80">
          {/* Badge superior destacado */}
          <div className="absolute -top-3.5 right-8">
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-[11px] font-extrabold uppercase tracking-widest px-3.5 py-1 rounded-full shadow-md shadow-blue-600/30">
              RECOMENDADO
            </span>
          </div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                <Zap size={14} />
                Gestión Inteligente Pro
              </span>
              {esPlanPro && (
                <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Plan Activo
                </span>
              )}
            </div>

            <h3 className="text-2xl sm:text-3xl font-bold text-white mb-2 flex items-center gap-2">
              Tu Asistente de IA
            </h3>
            <p className="text-sm text-slate-300 mb-6 leading-relaxed">
              Desbloquea el asistente de voz en vivo (Modo Mostrador), chatbot inteligente integrado y
              auditoría continua para operar tu tienda con manos libres.
            </p>

            {/* Precio */}
            <div className="mb-6">
              <div className="flex items-baseline gap-1">
                <span className="text-3xl sm:text-4xl font-extrabold text-white">
                  {periodoFacturacion === 'mensual' ? '$99.900' : '$84.900'}
                </span>
                <span className="text-sm text-slate-400 font-medium">COP / mes</span>
              </div>
              <p className="text-xs text-blue-400/90 mt-1 font-medium">
                {periodoFacturacion === 'mensual'
                  ? 'Facturación mensual recurrente'
                  : 'Facturado anualmente ($1.018.800 COP/año — 15% de descuento)'}
              </p>
            </div>

            {/* Botón CTA Pro */}
            <div className="mb-8">
              {esPlanPro ? (
                <div className="w-full py-3.5 px-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-sm font-bold text-center flex items-center justify-center gap-2">
                  <Check size={18} />
                  Tu plan Pro ya está activo
                </div>
              ) : solicitudEnviada ? (
                <div className="w-full py-3.5 px-4 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-300 text-sm font-semibold text-center flex items-center justify-center gap-2">
                  <Clock size={18} className="animate-spin" />
                  Solicitud en revisión por soporte
                </div>
              ) : (
                <button
                  onClick={() => setModalAbierto(true)}
                  className="w-full py-3.5 px-6 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-sm font-bold transition-all shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 group cursor-pointer"
                >
                  <Sparkles size={16} className="group-hover:rotate-12 transition-transform" />
                  Cambiar a Pro
                  <ChevronRight size={16} className="group-hover:translate-x-0.5 transition-transform" />
                </button>
              )}
            </div>

            {/* Desglose de características Pro */}
            <div className="space-y-4 pt-4 border-t border-slate-800">
              <p className="text-xs font-bold uppercase tracking-wider text-blue-300">
                Todo lo del plan Básico y además:
              </p>
              <div className="space-y-3.5">
                {caracteristicasPro.map((item, idx) => {
                  const Icon = item.icono
                  return (
                    <div key={idx} className="flex items-start gap-3">
                      <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 shrink-0 mt-0.5">
                        <Icon size={16} />
                      </div>
                      <div>
                        <h4 className="text-sm font-semibold text-white">{item.titulo}</h4>
                        <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">
                          {item.descripcion}
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pie de página explicativo */}
      <div className="max-w-4xl mx-auto mt-12 text-center text-xs text-slate-400 border-t border-slate-800/80 pt-6">
        <p>
          ¿Dudas sobre el plan adecuado para tu negocio? Escríbenos a soporte o solicita una demo
          guiada de la versión Pro con voz en vivo.
        </p>
      </div>

      {/* Modal interactivo de confirmación / solicitud de activación */}
      {modalAbierto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-[#141b27] border border-slate-700/80 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl text-left space-y-6 relative">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
                <Sparkles size={24} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">Activar Gestión Inteligente Pro</h3>
                <p className="text-xs text-slate-400 mt-0.5">Plan {periodoFacturacion}</p>
              </div>
            </div>

            <div className="bg-[#0e141f] border border-slate-800 rounded-2xl p-4 space-y-2 text-sm text-slate-300">
              <div className="flex justify-between items-center pb-2 border-b border-slate-800 text-xs">
                <span className="text-slate-400">Valor de la suscripción:</span>
                <span className="font-bold text-white">
                  {periodoFacturacion === 'mensual' ? '$99.900 COP / mes' : '$84.900 COP / mes'}
                </span>
              </div>
              <p className="text-xs text-slate-400 pt-1 leading-relaxed">
                Al confirmar, se generará una solicitud prioritaria en tu panel de soporte.
                Habilitaremos el asistente de voz bidireccional y el chatbot inteligente en tu cuenta.
              </p>
            </div>

            <div className="space-y-3 pt-2">
              <button
                onClick={handleSolicitarUpgrade}
                disabled={solicitando}
                className="w-full py-3.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:opacity-50 text-white font-bold text-sm transition-all shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2 cursor-pointer"
              >
                {solicitando ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Enviando solicitud...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    Confirmar y Solicitar Activación
                  </>
                )}
              </button>

              <button
                onClick={() => setModalAbierto(false)}
                className="w-full py-2.5 text-center text-xs text-slate-400 hover:text-white transition-colors"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
