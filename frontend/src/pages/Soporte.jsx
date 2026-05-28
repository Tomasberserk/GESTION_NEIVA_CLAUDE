import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'
import {
  MessageSquare,
  Plus,
  X,
  Send,
  RefreshCw,
  AlertTriangle,
  InboxIcon,
  ChevronRight
} from 'lucide-react'

const BASE = import.meta.env.VITE_API_URL || '/api'

function estadoBadge(estado) {
  const map = {
    abierto: 'bg-amber-100 text-amber-800 border border-amber-200',
    respondido: 'bg-green-100 text-green-800 border border-green-200',
    cerrado: 'bg-slate-100 text-slate-600 border border-slate-200',
  }
  return map[estado] ?? 'bg-slate-100 text-slate-600 border border-slate-200'
}

function formatearFecha(iso) {
  if (!iso) return ''
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(iso))
}

export default function Soporte() {
  const { usuario } = useAuth()

  // Lista de tickets
  const [tickets, setTickets] = useState([])
  const [cargandoLista, setCargandoLista] = useState(true)
  const [errorLista, setErrorLista] = useState(null)

  // Ticket seleccionado (con mensajes)
  const [ticketSeleccionado, setTicketSeleccionado] = useState(null)
  const [cargandoDetalle, setCargandoDetalle] = useState(false)
  const [errorDetalle, setErrorDetalle] = useState(null)

  // Modal nuevo ticket
  const [mostrarModal, setMostrarModal] = useState(false)
  const [nuevoTicket, setNuevoTicket] = useState({ asunto: '', mensaje: '' })
  const [enviandoTicket, setEnviandoTicket] = useState(false)
  const [errorModal, setErrorModal] = useState(null)

  // Respuesta en el hilo
  const [respuesta, setRespuesta] = useState('')
  const [enviandoRespuesta, setEnviandoRespuesta] = useState(false)
  const [errorRespuesta, setErrorRespuesta] = useState(null)

  const hiloRef = useRef(null)

  // ── Carga de tickets ─────────────────────────────────────────────────────────

  const cargarTickets = async () => {
    setCargandoLista(true)
    setErrorLista(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/soporte/tickets`)
      if (!res.ok) throw new Error('No se pudo cargar la lista de tickets')
      const data = await res.json()
      setTickets(data)
    } catch (e) {
      setErrorLista(e.message)
    } finally {
      setCargandoLista(false)
    }
  }

  useEffect(() => {
    cargarTickets()
  }, [])

  // ── Seleccionar ticket (carga detalle con mensajes) ──────────────────────────

  const seleccionarTicket = async (id) => {
    setCargandoDetalle(true)
    setErrorDetalle(null)
    setTicketSeleccionado(null)
    setRespuesta('')
    setErrorRespuesta(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/soporte/tickets/${id}`)
      if (!res.ok) throw new Error('No se pudo cargar el ticket')
      const data = await res.json()
      setTicketSeleccionado(data)
    } catch (e) {
      setErrorDetalle(e.message)
    } finally {
      setCargandoDetalle(false)
    }
  }

  // Scroll al fondo del hilo cuando carga o llegan mensajes nuevos
  useEffect(() => {
    if (hiloRef.current) {
      hiloRef.current.scrollTop = hiloRef.current.scrollHeight
    }
  }, [ticketSeleccionado])

  // ── Crear nuevo ticket ───────────────────────────────────────────────────────

  const crearTicket = async (e) => {
    e.preventDefault()
    if (!nuevoTicket.asunto.trim() || !nuevoTicket.mensaje.trim()) {
      setErrorModal('El asunto y el mensaje son obligatorios.')
      return
    }
    setEnviandoTicket(true)
    setErrorModal(null)
    try {
      const res = await authService.fetchAuth(`${BASE}/soporte/tickets`, {
        method: 'POST',
        body: JSON.stringify(nuevoTicket),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err?.detail || 'No se pudo crear el ticket')
      }
      setMostrarModal(false)
      setNuevoTicket({ asunto: '', mensaje: '' })
      await cargarTickets()
    } catch (e) {
      setErrorModal(e.message)
    } finally {
      setEnviandoTicket(false)
    }
  }

  // ── Enviar respuesta ─────────────────────────────────────────────────────────

  const enviarRespuesta = async (e) => {
    e.preventDefault()
    if (!respuesta.trim()) return
    setEnviandoRespuesta(true)
    setErrorRespuesta(null)
    try {
      const res = await authService.fetchAuth(
        `${BASE}/soporte/tickets/${ticketSeleccionado.id}/responder`,
        {
          method: 'POST',
          body: JSON.stringify({ mensaje: respuesta }),
        }
      )
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err?.detail || 'No se pudo enviar la respuesta')
      }
      setRespuesta('')
      // Recarga el detalle para mostrar el nuevo mensaje
      await seleccionarTicket(ticketSeleccionado.id)
      // También actualiza la lista (el estado puede haber cambiado)
      await cargarTickets()
    } catch (e) {
      setErrorRespuesta(e.message)
    } finally {
      setEnviandoRespuesta(false)
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full">
      {/* Cabecera */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <MessageSquare className="text-indigo-600 w-7 h-7" />
            Soporte Tecnico
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Crea y gestiona tus solicitudes de soporte.
          </p>
        </div>
        <button
          onClick={cargarTickets}
          className="flex items-center gap-2 border bg-white hover:bg-gray-50 text-gray-700 font-semibold px-4 py-2.5 rounded-lg transition-colors"
          title="Actualizar lista"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="hidden sm:inline">Actualizar</span>
        </button>
      </div>

      {/* Layout de dos paneles */}
      <div className="flex flex-1 gap-4 min-h-0" style={{ height: 'calc(100vh - 200px)' }}>

        {/* Panel izquierdo — lista de tickets */}
        <div className="w-full sm:w-72 lg:w-80 flex-shrink-0 flex flex-col bg-white border border-slate-200 rounded-xl overflow-hidden">
          {/* Botón nuevo ticket */}
          <div className="p-3 border-b border-slate-100">
            <button
              onClick={() => {
                setMostrarModal(true)
                setErrorModal(null)
                setNuevoTicket({ asunto: '', mensaje: '' })
              }}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-4 py-2.5 rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              Nuevo Ticket
            </button>
          </div>

          {/* Lista */}
          <div className="flex-1 overflow-y-auto">
            {cargandoLista ? (
              <div className="flex flex-col items-center justify-center py-16 gap-3">
                <RefreshCw className="w-7 h-7 animate-spin text-indigo-400" />
                <span className="text-sm text-slate-400">Cargando tickets...</span>
              </div>
            ) : errorLista ? (
              <div className="p-4">
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  {errorLista}
                </div>
              </div>
            ) : tickets.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-400">
                <InboxIcon className="w-10 h-10" />
                <span className="text-sm">Sin tickets aun</span>
              </div>
            ) : (
              <ul className="divide-y divide-slate-100">
                {tickets.map((t) => {
                  const esSeleccionado = ticketSeleccionado?.id === t.id
                  return (
                    <li key={t.id}>
                      <button
                        onClick={() => seleccionarTicket(t.id)}
                        className={`w-full text-left px-4 py-3 transition-colors flex items-start gap-2 group ${
                          esSeleccionado
                            ? 'bg-indigo-50 border-l-2 border-l-indigo-500'
                            : 'hover:bg-slate-50 border-l-2 border-l-transparent'
                        }`}
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-slate-800 truncate">
                            {t.asunto}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <span
                              className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full ${estadoBadge(t.estado)}`}
                            >
                              {t.estado}
                            </span>
                            <span className="text-xs text-slate-400 truncate">
                              {formatearFecha(t.created_at)}
                            </span>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-500 flex-shrink-0 mt-1" />
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        </div>

        {/* Panel derecho — detalle del ticket */}
        <div className="flex-1 flex flex-col bg-white border border-slate-200 rounded-xl overflow-hidden min-w-0">
          {cargandoDetalle ? (
            <div className="flex flex-col items-center justify-center flex-1 gap-3">
              <RefreshCw className="w-7 h-7 animate-spin text-indigo-400" />
              <span className="text-sm text-slate-400">Cargando conversacion...</span>
            </div>
          ) : errorDetalle ? (
            <div className="flex-1 flex items-center justify-center p-6">
              <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg text-sm flex items-start gap-2 max-w-md">
                <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                {errorDetalle}
              </div>
            </div>
          ) : !ticketSeleccionado ? (
            <div className="flex flex-col items-center justify-center flex-1 gap-3 text-slate-400">
              <MessageSquare className="w-12 h-12" />
              <p className="text-base font-medium">Selecciona un ticket</p>
              <p className="text-sm">Elige un ticket de la lista para ver la conversacion.</p>
            </div>
          ) : (
            <>
              {/* Cabecera del ticket */}
              <div className="px-6 py-4 border-b border-slate-100">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h2 className="text-lg font-bold text-slate-800 truncate">
                      {ticketSeleccionado.asunto}
                    </h2>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Abierto el {formatearFecha(ticketSeleccionado.created_at)}
                    </p>
                  </div>
                  <span
                    className={`inline-block text-xs font-semibold px-3 py-1 rounded-full flex-shrink-0 ${estadoBadge(
                      ticketSeleccionado.estado
                    )}`}
                  >
                    {ticketSeleccionado.estado}
                  </span>
                </div>
              </div>

              {/* Hilo de mensajes */}
              <div
                ref={hiloRef}
                className="flex-1 overflow-y-auto px-6 py-4 space-y-4"
              >
                {ticketSeleccionado.mensajes && ticketSeleccionado.mensajes.length > 0 ? (
                  ticketSeleccionado.mensajes.map((msg) => {
                    const esUsuario = msg.remitente_rol === 'usuario'
                    return (
                      <div
                        key={msg.id}
                        className={`flex flex-col ${esUsuario ? 'items-end' : 'items-start'}`}
                      >
                        <div
                          className={`max-w-lg px-4 py-3 rounded-2xl text-sm shadow-sm ${
                            esUsuario
                              ? 'bg-indigo-600 text-white rounded-br-sm'
                              : 'bg-slate-100 text-slate-800 rounded-bl-sm'
                          }`}
                        >
                          <p className="whitespace-pre-wrap break-words">{msg.mensaje}</p>
                        </div>
                        <div className="flex items-center gap-1.5 mt-1 px-1">
                          <span
                            className={`text-xs font-medium ${
                              esUsuario ? 'text-indigo-400' : 'text-slate-400'
                            }`}
                          >
                            {esUsuario ? 'Tu' : 'Soporte'}
                          </span>
                          <span className="text-xs text-slate-300">
                            {formatearFecha(msg.created_at)}
                          </span>
                        </div>
                      </div>
                    )
                  })
                ) : (
                  <div className="flex items-center justify-center py-8 text-slate-400 text-sm">
                    Sin mensajes en este ticket.
                  </div>
                )}
              </div>

              {/* Caja de respuesta */}
              <div className="px-6 py-4 border-t border-slate-100">
                {ticketSeleccionado.estado === 'cerrado' ? (
                  <div className="text-center text-sm text-slate-400 py-2 bg-slate-50 rounded-lg border border-slate-200">
                    Este ticket esta cerrado. No se pueden agregar mas respuestas.
                  </div>
                ) : (
                  <form onSubmit={enviarRespuesta} className="flex flex-col gap-2">
                    {errorRespuesta && (
                      <div className="bg-red-50 border border-red-200 text-red-700 p-2 rounded-lg text-xs flex items-start gap-2">
                        <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                        {errorRespuesta}
                      </div>
                    )}
                    <div className="flex gap-2 items-end">
                      <textarea
                        value={respuesta}
                        onChange={(e) => setRespuesta(e.target.value)}
                        placeholder="Escribe tu respuesta..."
                        rows={3}
                        className="flex-1 resize-none border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition"
                      />
                      <button
                        type="submit"
                        disabled={enviandoRespuesta || !respuesta.trim()}
                        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed text-white font-semibold px-5 py-3 rounded-xl transition-colors flex-shrink-0"
                      >
                        {enviandoRespuesta ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                        <span className="hidden sm:inline">Enviar Respuesta</span>
                      </button>
                    </div>
                  </form>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Modal — Nuevo Ticket */}
      {mostrarModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 relative">
            {/* Cerrar */}
            <button
              onClick={() => setMostrarModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="text-xl font-bold text-slate-800 mb-1 flex items-center gap-2">
              <Plus className="w-5 h-5 text-indigo-600" />
              Nuevo Ticket de Soporte
            </h2>
            <p className="text-sm text-slate-500 mb-5">
              Describe tu problema y nuestro equipo te respondera a la brevedad.
            </p>

            <form onSubmit={crearTicket} className="space-y-4">
              {errorModal && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg text-sm flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  {errorModal}
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                  Asunto
                </label>
                <input
                  type="text"
                  value={nuevoTicket.asunto}
                  onChange={(e) =>
                    setNuevoTicket((prev) => ({ ...prev, asunto: e.target.value }))
                  }
                  placeholder="Ej: No puedo registrar una venta"
                  className="w-full border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                  Mensaje
                </label>
                <textarea
                  value={nuevoTicket.mensaje}
                  onChange={(e) =>
                    setNuevoTicket((prev) => ({ ...prev, mensaje: e.target.value }))
                  }
                  placeholder="Describe el problema con el mayor detalle posible..."
                  rows={5}
                  className="w-full resize-none border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition"
                />
              </div>

              <div className="flex gap-3 pt-1">
                <button
                  type="button"
                  onClick={() => setMostrarModal(false)}
                  className="flex-1 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-semibold py-2.5 rounded-xl transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={enviandoTicket}
                  className="flex-1 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-xl transition-colors"
                >
                  {enviandoTicket ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Enviar Ticket
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
