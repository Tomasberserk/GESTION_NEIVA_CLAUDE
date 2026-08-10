import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'
import {
  MessageSquare,
  Smartphone,
  Copy,
  Check,
  RefreshCw,
  Unlink,
  Mic,
  Type,
  Package,
  Search,
  Bot,
  Zap,
  Shield,
  ChevronRight,
} from 'lucide-react'

const BASE = import.meta.env.VITE_API_URL || '/api'

function formatearTiempo(segundos) {
  const min = Math.floor(segundos / 60)
  const seg = segundos % 60
  return `${min}:${seg.toString().padStart(2, '0')}`
}

export default function ConfigWhatsApp() {
  const { usuario } = useAuth()

  // Estado de vinculación
  const [estado, setEstado] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  // Código de vinculación
  const [codigo, setCodigo] = useState(null)
  const [tiempoRestante, setTiempoRestante] = useState(0)
  const [generandoCodigo, setGenerandoCodigo] = useState(false)
  const [copiado, setCopiado] = useState(false)

  // Desvincular
  const [desvinculando, setDesvinculando] = useState(false)
  const [confirmarDesvincular, setConfirmarDesvincular] = useState(false)

  // ── Cargar estado ─────────────────────────────────────────────────────────────

  const cargarEstado = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/api/whatsapp/estado`)
      if (!res.ok) throw new Error('No se pudo cargar el estado de WhatsApp')
      const data = await res.json()
      setEstado(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    cargarEstado()
  }, [cargarEstado])

  // ── Temporizador del código ───────────────────────────────────────────────────

  useEffect(() => {
    if (tiempoRestante <= 0) return
    const interval = setInterval(() => {
      setTiempoRestante((prev) => {
        if (prev <= 1) {
          setCodigo(null)
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [tiempoRestante])

  // ── Generar código ────────────────────────────────────────────────────────────

  const generarCodigo = async () => {
    setGenerandoCodigo(true)
    setError(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/api/whatsapp/vinculacion/codigo`)
      if (!res.ok) throw new Error('No se pudo generar el código')
      const data = await res.json()
      if (data.telefono_vinculado) {
        setEstado({ vinculado: true, telefono: data.telefono_vinculado })
        setCodigo(null)
      } else {
        setCodigo(data.codigo)
        setTiempoRestante(data.expira_en || 600)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setGenerandoCodigo(false)
    }
  }

  // ── Copiar código ─────────────────────────────────────────────────────────────

  const copiarCodigo = async () => {
    if (!codigo) return
    try {
      await navigator.clipboard.writeText(`VINCULAR ${codigo}`)
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    } catch {
      // Fallback
      const el = document.createElement('textarea')
      el.value = `VINCULAR ${codigo}`
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    }
  }

  // ── Desvincular ───────────────────────────────────────────────────────────────

  const desvincular = async () => {
    setDesvinculando(true)
    setError(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/api/whatsapp/vinculacion`, {
        method: 'DELETE',
      })
      if (!res.ok) throw new Error('No se pudo desvincular')
      setEstado({ vinculado: false, telefono: null })
      setConfirmarDesvincular(false)
    } catch (e) {
      setError(e.message)
    } finally {
      setDesvinculando(false)
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────────

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw size={24} className="animate-spin text-emerald-500" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/20">
          <Bot size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Asistente WhatsApp IA</h1>
          <p className="text-sm text-slate-400">
            Gestiona tu inventario con mensajes de voz o texto
          </p>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Estado de conexión */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Smartphone size={18} className="text-slate-400" />
            <span className="text-sm font-semibold text-slate-200">Estado de Conexión</span>
          </div>
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
              estado?.vinculado
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${
              estado?.vinculado ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
            }`} />
            {estado?.vinculado ? 'Vinculado' : 'No vinculado'}
          </span>
        </div>

        <div className="p-5">
          {estado?.vinculado ? (
            /* ─── Ya vinculado ─── */
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                <Check size={18} className="text-emerald-400 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-emerald-300">
                    WhatsApp conectado
                  </p>
                  <p className="text-xs text-emerald-400/70 mt-0.5">
                    Número: {estado.telefono}
                  </p>
                </div>
              </div>

              <p className="text-sm text-slate-400">
                Tu inventario se actualiza automáticamente cuando envías mensajes de voz o texto al bot.
              </p>

              {/* Botón desvincular */}
              {confirmarDesvincular ? (
                <div className="flex items-center gap-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                  <span className="text-sm text-red-300">¿Seguro que quieres desvincular?</span>
                  <button
                    onClick={desvincular}
                    disabled={desvinculando}
                    className="px-3 py-1.5 text-xs font-semibold rounded-md bg-red-600 text-white hover:bg-red-700 transition-colors disabled:opacity-50"
                  >
                    {desvinculando ? 'Desvinculando...' : 'Sí, desvincular'}
                  </button>
                  <button
                    onClick={() => setConfirmarDesvincular(false)}
                    className="px-3 py-1.5 text-xs font-semibold rounded-md bg-slate-700 text-slate-300 hover:bg-slate-600 transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmarDesvincular(true)}
                  className="flex items-center gap-2 text-sm text-red-400 hover:text-red-300 transition-colors"
                >
                  <Unlink size={14} />
                  Desvincular WhatsApp
                </button>
              )}
            </div>
          ) : (
            /* ─── No vinculado — mostrar código ─── */
            <div className="space-y-5">
              {codigo ? (
                <>
                  <div className="text-center space-y-3">
                    <p className="text-sm text-slate-400">
                      Envía este mensaje al bot por WhatsApp:
                    </p>
                    <div className="relative inline-flex items-center gap-2 px-6 py-4 bg-slate-900 border border-slate-600 rounded-xl">
                      <span className="text-2xl font-mono font-bold tracking-[0.3em] text-emerald-400">
                        VINCULAR {codigo}
                      </span>
                      <button
                        onClick={copiarCodigo}
                        className="absolute -top-2 -right-2 p-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors"
                        title="Copiar mensaje"
                      >
                        {copiado ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                      </button>
                    </div>
                    <p className="text-xs text-slate-500">
                      Expira en{' '}
                      <span className={tiempoRestante < 60 ? 'text-amber-400' : 'text-slate-400'}>
                        {formatearTiempo(tiempoRestante)}
                      </span>
                    </p>
                  </div>
                </>
              ) : (
                <div className="text-center space-y-4">
                  <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-green-500/20 flex items-center justify-center">
                    <MessageSquare size={28} className="text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-300 font-medium">
                      Conecta tu WhatsApp para gestionar inventario por voz
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      Genera un código y envíalo al bot desde tu WhatsApp
                    </p>
                  </div>
                  <button
                    onClick={generarCodigo}
                    disabled={generandoCodigo}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-emerald-600 to-green-600 text-white text-sm font-semibold hover:from-emerald-500 hover:to-green-500 transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                  >
                    {generandoCodigo ? (
                      <RefreshCw size={16} className="animate-spin" />
                    ) : (
                      <Zap size={16} />
                    )}
                    {generandoCodigo ? 'Generando...' : 'Generar Código de Vinculación'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Guía de uso */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-700">
          <span className="text-sm font-semibold text-slate-200">
            ¿Qué puedes hacer con el asistente?
          </span>
        </div>
        <div className="p-5 grid gap-4 sm:grid-cols-2">
          {/* Reabastecer */}
          <div className="p-4 bg-slate-900/50 border border-slate-700/50 rounded-lg space-y-2">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-blue-500/15">
                <Package size={16} className="text-blue-400" />
              </div>
              <span className="text-sm font-semibold text-slate-200">Reabastecer Stock</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Envía un audio o texto diciendo qué productos llegaron y en qué cantidad.
            </p>
            <div className="space-y-1.5 pt-1">
              <div className="flex items-start gap-2">
                <Mic size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                <p className="text-xs text-slate-500 italic">
                  "Me llegaron 20 papeles higiénicos Familia y 30 jabones Protex"
                </p>
              </div>
              <div className="flex items-start gap-2">
                <Type size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                <p className="text-xs text-slate-500 italic">
                  "Llegaron 50 gaseosas Coca-Cola litro"
                </p>
              </div>
            </div>
          </div>

          {/* Consultar */}
          <div className="p-4 bg-slate-900/50 border border-slate-700/50 rounded-lg space-y-2">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-purple-500/15">
                <Search size={16} className="text-purple-400" />
              </div>
              <span className="text-sm font-semibold text-slate-200">Consultar Stock</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Pregunta cuántas unidades tienes de cualquier producto.
            </p>
            <div className="space-y-1.5 pt-1">
              <div className="flex items-start gap-2">
                <Mic size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                <p className="text-xs text-slate-500 italic">
                  "¿Cuántos arroz Diana tengo?"
                </p>
              </div>
              <div className="flex items-start gap-2">
                <Type size={12} className="text-emerald-400 mt-0.5 shrink-0" />
                <p className="text-xs text-slate-500 italic">
                  "Stock de jabón"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Instrucciones paso a paso */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-700">
          <span className="text-sm font-semibold text-slate-200">
            Cómo empezar
          </span>
        </div>
        <div className="p-5 space-y-3">
          {[
            {
              step: '1',
              title: 'Genera tu código',
              desc: 'Haz clic en "Generar Código de Vinculación" arriba',
            },
            {
              step: '2',
              title: 'Abre WhatsApp',
              desc: 'Guarda el número del bot y envíale el mensaje con tu código',
            },
            {
              step: '3',
              title: '¡Listo! Empieza a hablarle',
              desc: 'Envía notas de voz o mensajes de texto para gestionar tu inventario',
            },
          ].map((item) => (
            <div
              key={item.step}
              className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-700/30 transition-colors"
            >
              <span className="flex items-center justify-center w-7 h-7 rounded-full bg-emerald-500/15 text-emerald-400 text-xs font-bold shrink-0">
                {item.step}
              </span>
              <div>
                <p className="text-sm font-medium text-slate-200">{item.title}</p>
                <p className="text-xs text-slate-400 mt-0.5">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Seguridad */}
      <div className="flex items-start gap-3 p-4 bg-slate-800/30 border border-slate-700/50 rounded-lg">
        <Shield size={16} className="text-slate-500 mt-0.5 shrink-0" />
        <p className="text-xs text-slate-500 leading-relaxed">
          Tu inventario solo es accesible desde el WhatsApp vinculado a tu cuenta. 
          Nadie más puede modificar tus productos. Si cambias de número, 
          desvincula el anterior y vincula el nuevo.
        </p>
      </div>
    </div>
  )
}
