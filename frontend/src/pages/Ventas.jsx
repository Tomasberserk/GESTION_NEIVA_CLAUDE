import { useState, useEffect, useCallback, useMemo } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'
import usuarioService from '../services/usuarioService'
import { isAdmin, canExportReports } from '../utils/permissions'
import {
  Clock,
  Calendar,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  User,
  Users,
  Filter,
  FileSpreadsheet,
  RefreshCw,
  ShoppingBag,
  Loader2,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react'

const BASE = import.meta.env.VITE_API_URL || '/api'

const TABS_HISTORICO = [
  { id: 'hoy',       label: 'Hoy',      labelCorto: 'Hoy' },
  { id: 'semana',    label: 'Esta Semana', labelCorto: 'Semana' },
  { id: 'historico', label: 'Histórico y Reportes', labelCorto: 'Histórico' },
]

// Obtiene la fecha de hoy en formato YYYY-MM-DD según la zona horaria comercial America/Bogota
function getHoyColombia() {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Bogota',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date())
  return parts
}

function sumarDias(fechaStr, dias) {
  const [y, m, d] = fechaStr.split('-').map(Number)
  const dt = new Date(Date.UTC(y, m - 1, d + dias))
  return dt.toISOString().split('T')[0]
}

function formatearFechaCabecera(fechaStr) {
  const [y, m, d] = fechaStr.split('-').map(Number)
  const fecha = new Date(Date.UTC(y, m - 1, d, 12, 0, 0))
  const esHoy = fechaStr === getHoyColombia()
  const texto = new Intl.DateTimeFormat('es-CO', {
    timeZone: 'America/Bogota',
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(fecha)
  return esHoy ? `Hoy · ${texto}` : texto
}

function formatearHoraBogota(isoString) {
  try {
    return new Intl.DateTimeFormat('es-CO', {
      timeZone: 'America/Bogota',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    }).format(new Date(isoString))
  } catch {
    return ''
  }
}

const fmt = (n) => Number(n).toLocaleString('es-CO', { maximumFractionDigits: 0 })

function ExcelExport({ empresaId }) {
  const [descargando, setDescargando] = useState(false)
  const [estado, setEstado] = useState(null) // 'ok' | 'error' | null

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
    <div className="bg-white rounded-xl border border-slate-200 p-5 mt-5">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <FileSpreadsheet size={22} />
          </div>
          <div>
            <p className="font-semibold text-slate-800">Exportar a Excel</p>
            <p className="text-sm text-slate-500 mt-0.5">
              Descarga el historial completo de ventas (.xlsx)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {estado === 'ok' && (
            <span className="text-sm text-green-600 font-medium flex items-center gap-1">
              <CheckCircle2 size={16} /> Descargado
            </span>
          )}
          {estado === 'error' && (
            <span className="text-sm text-red-600 font-medium flex items-center gap-1">
              <AlertCircle size={16} /> Error al generar
            </span>
          )}
          <button
            onClick={descargar}
            disabled={descargando}
            className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-200 disabled:cursor-not-allowed text-white font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm flex items-center gap-2"
          >
            {descargando ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Generando...
              </>
            ) : (
              '⬇ Exportar Excel'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * Item individual del Timeline de Actividad del Día con Acordeón desplegable
 */
function VentaTimelineItem({ venta }) {
  const [expandido, setExpandido] = useState(false)
  const hora = formatearHoraBogota(venta.fecha_venta)
  const vendedor = venta.vendedor_nombre_snapshot || 'Vendedor'
  const codigo = venta.id ? `#${venta.id.split('-')[0]}` : ''

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm transition-all hover:border-slate-300 overflow-hidden">
      {/* Fila principal compacta */}
      <div
        onClick={() => setExpandido(!expandido)}
        className="p-4 flex items-center justify-between cursor-pointer select-none hover:bg-slate-50/70 transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-violet-50 text-violet-700 flex items-center justify-center shrink-0">
            <Clock size={18} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-slate-800 text-sm">{hora}</span>
              <span className="text-xs font-mono text-slate-400">{codigo}</span>
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-slate-100 text-slate-700 truncate max-w-[140px]">
                👤 {vendedor}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {venta.detalles?.length || 0} {venta.detalles?.length === 1 ? 'producto' : 'productos'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <span className="font-bold text-base sm:text-lg text-violet-700">
            ${fmt(venta.total)}
          </span>
          <button
            type="button"
            className="text-slate-400 hover:text-slate-600 p-1 transition-transform"
            aria-label={expandido ? 'Colapsar detalles' : 'Ver productos'}
          >
            {expandido ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
      </div>

      {/* Detalle expandible (Acordeón) */}
      {expandido && (
        <div className="border-t border-slate-100 bg-slate-50/50 p-4 animate-in fade-in-50 duration-150">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">
            Detalle de la Venta
          </h4>
          <div className="space-y-2">
            {venta.detalles?.map((d) => (
              <div
                key={d.id}
                className="flex items-center justify-between text-xs sm:text-sm text-slate-700 bg-white p-2.5 rounded-lg border border-slate-100"
              >
                <div className="truncate mr-3">
                  <span className="font-medium text-slate-800">{d.producto_nombre || 'Producto'}</span>
                  <span className="text-slate-400 ml-2">
                    × {Number(d.cantidad).toLocaleString('es-CO', { maximumFractionDigits: 3 })}
                  </span>
                </div>
                <div className="shrink-0 text-right">
                  <span className="font-semibold text-slate-800">${fmt(d.subtotal)}</span>
                  {d.cantidad > 1 && (
                    <span className="block text-[10px] text-slate-400">
                      (${fmt(d.precio_unitario)} c/u)
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function Ventas() {
  const { usuario } = useAuth()
  const esAdmin = isAdmin(usuario)

  // Modo de vista para Admin: 'actividad' (timeline del día) | 'historico' (períodos)
  const [modoVista, setModoVista] = useState(esAdmin ? 'actividad' : 'historico')

  // Estado para "Actividad del Día"
  const [fechaActividad, setFechaActividad] = useState(getHoyColombia)
  const [cajeroFiltro, setCajeroFiltro] = useState('') // '' = todos
  const [cajerosDisponibles, setCajerosDisponibles] = useState([])
  const [ventasActividad, setVentasActividad] = useState([])
  const [cargandoActividad, setCargandoActividad] = useState(false)
  const [errorActividad, setErrorActividad] = useState(null)

  // Estado para "Histórico" (o cajeros)
  const [tabHistorico, setTabHistorico] = useState('hoy')
  const [ventasHistorico, setVentasHistorico] = useState([])
  const [cargandoHistorico, setCargandoHistorico] = useState(false)
  const [errorHistorico, setErrorHistorico] = useState(null)

  // 1. Cargar cajeros disponibles para el selector de filtro (solo Admin)
  useEffect(() => {
    if (esAdmin) {
      usuarioService
        .listarEmpleados()
        .then((data) => setCajerosDisponibles(data))
        .catch(() => {})
    }
  }, [esAdmin])

  // 2. Cargar Actividad del Día (Server-side)
  const cargarActividad = useCallback(async () => {
    if (!esAdmin) return
    setCargandoActividad(true)
    setErrorActividad(null)

    try {
      const url = new URL(`${BASE}/ventas/actividad`, window.location.origin)
      if (fechaActividad) url.searchParams.set('fecha', fechaActividad)
      if (cajeroFiltro) url.searchParams.set('usuario_id', cajeroFiltro)

      const res = await authService.fetchAuth(url.toString())
      if (!res.ok) throw new Error('Error al cargar la actividad del día')
      const data = await res.json()
      setVentasActividad(data || [])
    } catch (err) {
      setErrorActividad(err.message || 'Error al conectar con el servidor')
    } finally {
      setCargandoActividad(false)
    }
  }, [esAdmin, fechaActividad, cajeroFiltro])

  useEffect(() => {
    if (modoVista === 'actividad') {
      cargarActividad()
    }
  }, [modoVista, cargarActividad])

  // 3. Cargar Histórico (o vista simple para cajeros)
  const cargarHistorico = useCallback(async (tabActual) => {
    if (!usuario?.empresa_id) return
    setCargandoHistorico(true)
    setErrorHistorico(null)

    try {
      const ahora = new Date()
      const fin = ahora.toISOString()
      const inicio = new Date(ahora)

      if (tabActual === 'hoy') {
        inicio.setHours(0, 0, 0, 0)
      } else if (tabActual === 'semana') {
        const dayOfWeek = inicio.getDay() || 7
        inicio.setDate(inicio.getDate() - (dayOfWeek - 1))
        inicio.setHours(0, 0, 0, 0)
      } else {
        inicio.setDate(inicio.getDate() - 30)
        inicio.setHours(0, 0, 0, 0)
      }

      const url = new URL(`${BASE}/ventas/${usuario.empresa_id}`, window.location.origin)
      url.searchParams.set('fecha_inicio', inicio.toISOString())
      url.searchParams.set('fecha_fin', fin)

      const res = await authService.fetchAuth(url.toString())
      if (!res.ok) throw new Error('Error cargando ventas')
      const data = await res.json()
      setVentasHistorico(data || [])
    } catch (e) {
      setErrorHistorico(e.message)
    } finally {
      setCargandoHistorico(false)
    }
  }, [usuario])

  useEffect(() => {
    if (modoVista === 'historico') {
      cargarHistorico(tabHistorico)
    }
  }, [modoVista, tabHistorico, cargarHistorico])

  // Navegación de fechas para Actividad del Día
  const esHoy = fechaActividad === getHoyColombia()
  const irDiaAnterior = () => setFechaActividad((prev) => sumarDias(prev, -1))
  const irDiaSiguiente = () => setFechaActividad((prev) => sumarDias(prev, 1))
  const irAHoy = () => setFechaActividad(getHoyColombia())

  // Métricas calculadas para la actividad del día
  const totalActividad = useMemo(
    () => ventasActividad.reduce((acc, v) => acc + (v.total || 0), 0),
    [ventasActividad]
  )

  // Desglose de ventas por cajero
  const desgloseVendedores = useMemo(() => {
    const mapa = {}
    ventasActividad.forEach((v) => {
      const nombre = v.vendedor_nombre_snapshot || 'Admin'
      if (!mapa[nombre]) {
        mapa[nombre] = { conteo: 0, total: 0 }
      }
      mapa[nombre].conteo += 1
      mapa[nombre].total += v.total || 0
    })
    return Object.entries(mapa).map(([nombre, stats]) => ({
      nombre,
      ...stats,
    }))
  }, [ventasActividad])

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Encabezado y Selector de Modo (solo Admin) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">
            {esAdmin ? 'Ventas & Actividad' : 'Ventas del Mostrador'}
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {esAdmin
              ? 'Monitoreo de ingresos en vivo y trazabilidad de cajeros'
              : 'Historial de ventas registradas'}
          </p>
        </div>

        {esAdmin && (
          <div className="flex bg-slate-100 p-1 rounded-xl shrink-0">
            <button
              type="button"
              onClick={() => setModoVista('actividad')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                modoVista === 'actividad'
                  ? 'bg-white text-violet-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <Clock size={16} />
              Actividad del Día
            </button>
            <button
              type="button"
              onClick={() => setModoVista('historico')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                modoVista === 'historico'
                  ? 'bg-white text-violet-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <Calendar size={16} />
              Histórico
            </button>
          </div>
        )}
      </div>

      {/* ======================================================== */}
      {/* MODO 1: ACTIVIDAD DEL DÍA (Exclusivo Admin) */}
      {/* ======================================================== */}
      {esAdmin && modoVista === 'actividad' && (
        <div className="space-y-5">
          {/* Barra de Control: Selector de Fecha + Filtro Cajero */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            {/* Controles de Fecha Mobile-First */}
            <div className="flex items-center justify-between sm:justify-start gap-2">
              <button
                type="button"
                onClick={irDiaAnterior}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors"
                title="Día anterior"
              >
                <ChevronLeft size={18} />
              </button>

              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-100 text-slate-800 font-semibold text-xs sm:text-sm">
                <Calendar size={16} className="text-violet-600" />
                <span>{formatearFechaCabecera(fechaActividad)}</span>
              </div>

              <button
                type="button"
                onClick={irDiaSiguiente}
                disabled={esHoy}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed text-slate-600 transition-colors"
                title="Día siguiente"
              >
                <ChevronRight size={18} />
              </button>

              {!esHoy && (
                <button
                  type="button"
                  onClick={irAHoy}
                  className="text-xs text-violet-600 hover:text-violet-700 font-semibold px-2 py-1 underline ml-1"
                >
                  Ir a Hoy
                </button>
              )}
            </div>

            {/* Filtro por Vendedor (Server-Side) */}
            <div className="flex items-center gap-2">
              <Filter size={16} className="text-slate-400 shrink-0 hidden sm:block" />
              <select
                value={cajeroFiltro}
                onChange={(e) => setCajeroFiltro(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2 text-xs sm:text-sm bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-violet-500 w-full sm:w-auto"
              >
                <option value="">Todos los cajeros</option>
                {cajerosDisponibles.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nombre || c.email}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={cargarActividad}
                className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-500 transition-colors"
                title="Refrescar actividad"
              >
                <RefreshCw size={16} className={cargandoActividad ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>

          {/* Tarjeta de Resumen Superior */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Total Ingresos Registrados ({formatearFechaCabecera(fechaActividad)})
                </span>
                <p className="text-3xl sm:text-4xl font-extrabold text-violet-700">
                  {cargandoActividad ? '…' : `$${fmt(totalActividad)}`}
                </p>
              </div>

              <div className="text-left sm:text-right">
                <p className="text-2xl font-bold text-slate-800">
                  {cargandoActividad ? '…' : ventasActividad.length}
                </p>
                <p className="text-xs text-slate-400">
                  {ventasActividad.length === 1 ? 'venta realizada' : 'ventas realizadas'}
                </p>
              </div>
            </div>

            {/* Desglose por Vendedor */}
            {desgloseVendedores.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  Ventas por Vendedor:
                </span>
                <div className="flex flex-wrap gap-2">
                  {desgloseVendedores.map((v) => (
                    <div
                      key={v.nombre}
                      className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-100 text-xs flex items-center gap-2"
                    >
                      <span className="font-semibold text-slate-700">👤 {v.nombre}:</span>
                      <span className="text-violet-600 font-bold">${fmt(v.total)}</span>
                      <span className="text-slate-400 text-[11px]">({v.conteo})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Timeline de Ventas con Acordeón */}
          {errorActividad && (
            <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded-xl text-sm flex items-center justify-between">
              <span>{errorActividad}</span>
              <button
                type="button"
                onClick={cargarActividad}
                className="text-xs bg-red-600 text-white font-semibold px-3 py-1.5 rounded-lg"
              >
                Reintentar
              </button>
            </div>
          )}

          {cargandoActividad ? (
            <div className="flex items-center justify-center h-48 bg-white rounded-xl border border-slate-200">
              <div className="flex items-center gap-3 text-slate-500 text-sm">
                <Loader2 size={22} className="animate-spin text-violet-600" />
                Cargando ventas del día...
              </div>
            </div>
          ) : ventasActividad.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
              <div className="w-14 h-14 bg-slate-100 text-slate-400 rounded-2xl flex items-center justify-center mx-auto mb-3 text-2xl">
                📋
              </div>
              <h3 className="font-semibold text-slate-800 text-base">
                Sin ventas registradas en esta fecha
              </h3>
              <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1">
                {cajeroFiltro
                  ? 'Este cajero no registró ventas en la fecha seleccionada.'
                  : 'Aún no se han completado transacciones para este día comercial.'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {ventasActividad.map((venta) => (
                <VentaTimelineItem key={venta.id} venta={venta} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* MODO 2: HISTÓRICO GENERAL (O vista cajero) */}
      {/* ======================================================== */}
      {(modoVista === 'historico' || !esAdmin) && (
        <div className="space-y-5">
          {/* Segmented control para pestañas históricas */}
          <div className="flex gap-1 bg-slate-100 p-1 rounded-xl">
            {TABS_HISTORICO.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTabHistorico(t.id)}
                className={`flex-1 py-2 px-2 sm:px-3 rounded-lg text-sm font-medium transition-all ${
                  tabHistorico === t.id
                    ? 'bg-white text-violet-700 shadow-sm'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <span className="sm:hidden">{t.labelCorto}</span>
                <span className="hidden sm:inline">{t.label}</span>
              </button>
            ))}
          </div>

          {errorHistorico && (
            <div className="bg-red-50 text-red-600 p-4 rounded-xl text-sm">{errorHistorico}</div>
          )}

          {/* Banner de Total del período */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wide font-bold mb-1">
                {tabHistorico === 'hoy'
                  ? 'Total ingresos hoy'
                  : tabHistorico === 'semana'
                  ? 'Total esta semana'
                  : 'Total últimos 30 días'}
              </p>
              <p className="text-3xl sm:text-4xl font-extrabold text-violet-600">
                {cargandoHistorico
                  ? '…'
                  : `$${fmt(ventasHistorico.reduce((s, v) => s + (v.total || 0), 0))}`}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-slate-800">
                {cargandoHistorico ? '…' : ventasHistorico.length}
              </p>
              <p className="text-xs text-slate-400">
                {ventasHistorico.length === 1 ? 'venta' : 'ventas'}
              </p>
            </div>
          </div>

          {/* Lista de ventas histórica */}
          {cargandoHistorico ? (
            <div className="flex items-center justify-center h-48 bg-white rounded-xl border border-slate-200">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-500" />
            </div>
          ) : ventasHistorico.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-400">
              <div className="text-5xl mb-3">📋</div>
              <p className="text-sm">Sin ventas en este período</p>
            </div>
          ) : (
            <div className="space-y-3">
              {ventasHistorico.map((venta) => (
                <VentaTimelineItem key={venta.id} venta={venta} />
              ))}
            </div>
          )}

          {/* Botón de exportación a Excel solo visible para administradores */}
          {canExportReports(usuario) && tabHistorico === 'historico' && (
            <ExcelExport empresaId={usuario?.empresa_id} />
          )}
        </div>
      )}
    </div>
  )
}
