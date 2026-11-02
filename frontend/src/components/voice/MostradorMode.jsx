import React, { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useNavigate } from 'react-router-dom'
import { X, Mic, MicOff, Check, AlertCircle, Sparkles, Volume2, RotateCcw, Terminal } from 'lucide-react'
import VoiceOrb from './VoiceOrb'
import { VoiceTurnState } from '../../services/voice/VoiceTurnManager'

/**
 * MostradorMode: Vista inmersiva a pantalla completa optimizada para celulares apoyados
 * en el mostrador a 1 metro de distancia. Tipografía gigante de alto contraste.
 */
export default function MostradorMode({
  isOpen,
  onClose,
  voiceAgent,
}) {
  // ⚠️ Rules of Hooks: TODOS los hooks deben correr en cada render, sin retornos
  // condicionales antes. Un early-return previo crasheaba el árbol al cerrar el
  // modal ("Rendered fewer hooks than expected" → pestaña zombi, orbe muerto).
  const {
    voiceState,
    transcript,
    lastResponse,
    errorMessage,
    activarModoVoz,
    desactivarModoVoz,
    iniciarEscucha,
    detenerYEnviar,
    omitirRespuesta,
    reiniciarSesion,
    confirmarOperacion,
    cancelarOperacion,
    seleccionarOpcion,
    isActive,
  } = voiceAgent || {}

  const navigate = useNavigate()

  const [mostrarLogs, setMostrarLogs] = useState(false)
  const [logsRecientes, setLogsRecientes] = useState([])

  // Interceptor de logs para visibilidad en celulares (sin DevTools)
  useEffect(() => {
    if (!isOpen) return
    const origLog = console.log
    const origWarn = console.warn
    const origError = console.error

    const interceptar = (tipo, args) => {
      const msg = args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ')
      if (msg.includes('[VOICE-') || msg.includes('VoiceTurnManager')) {
        const timestamp = new Date().toLocaleTimeString('es-CO', { hour12: false })
        setLogsRecientes(prev => [{ id: Date.now() + Math.random(), time: timestamp, tipo, msg }, ...prev.slice(0, 24)])
      }
    }

    console.log = (...args) => { origLog(...args); interceptar('info', args) }
    console.warn = (...args) => { origWarn(...args); interceptar('warn', args) }
    console.error = (...args) => { origError(...args); interceptar('error', args) }

    return () => {
      console.log = origLog
      console.warn = origWarn
      console.error = origError
    }
  }, [isOpen])

  // Auto-activación si el modal se abre y el servicio está en IDLE
  useEffect(() => {
    if (isOpen && voiceState === VoiceTurnState.IDLE) {
      console.log('[MostradorMode] Modal abierto en IDLE: auto-activando sesión de voz...')
      if (typeof activarModoVoz === 'function') {
        activarModoVoz(true)
      }
    }
  }, [isOpen, voiceState, activarModoVoz])


  // "Salir" cierra el modo voz y regresa al Dashboard (nunca cierra la sesión).
  const salirAlDashboard = () => {
    desactivarModoVoz()
    onClose()
    navigate('/dashboard', { replace: true })
  }

  const preview = lastResponse?.preview
  const clarification = lastResponse?.clarification
  const isConfirming = voiceState === VoiceTurnState.CONFIRMING || lastResponse?.estado === 'READY_TO_CONFIRM'
  const isError = voiceState === VoiceTurnState.ERROR
  const isListeningNow = voiceState === VoiceTurnState.LISTENING || voiceState === VoiceTurnState.SPEECH_DETECTED
  const isSpeakingNow = voiceState === VoiceTurnState.SPEAKING

  // Diagnóstico BFCache/zombia: loguea TODO click en fase de captura (antes que React).
  // Si el usuario hace click y NO aparece esta línea en consola, el DOM está muerto (pestaña zombi).
  useEffect(() => {
    if (!isOpen) return
    const listener = (e) => {
      const label = e.target?.textContent?.trim().slice(0, 30) || e.target?.tagName || '?'
      const enOverlay = !!e.target?.closest?.('[data-voice-overlay]')
      console.log(`[VOICE-UI] click "${label}" ${enOverlay ? 'EN overlay' : 'FUERA (atravesó)'} (voiceState=${voiceState})`)
    }
    document.addEventListener('click', listener, true)
    return () => document.removeEventListener('click', listener, true)
    // voiceState se re-evalúa en cada render por el closure del listener
  })

  // 🔴 CABLE DE EMERGENCIA (independiente de React): un botón creado con DOM puro,
  // colgado directo de document.body con listeners nativos (click/mousedown/touchend).
  // Funciona aunque el sistema de eventos sintéticos de React esté muerto (pestaña
  // zombi, hooks crasheados o una extensión de Chrome tragándose los clicks).
  useEffect(() => {
    if (!isOpen) return
    const salir = () => {
      try { window.__voiceSalirAlDashboard?.() } catch { /* React muerto: seguimos con el plan nuclear */ }
      // Si React no desmontó el overlay en ~300 ms (árbol muerto), recarga dura.
      // NUNCA quitar nodos de React a mano (removeChild posterior → NotFoundError).
      setTimeout(() => {
        if (document.querySelector('[data-voice-overlay="1"]')) location.replace('/dashboard')
      }, 300)
    }
    // Micro-hoja de estilos para el hover del botón nativo (los inline no soportan :hover)
    if (!document.getElementById('voice-exit-style')) {
      const s = document.createElement('style')
      s.id = 'voice-exit-style'
      s.textContent =
        '#voice-emergency-exit:hover{background-color:#334155;color:#fff}' +
        '#voice-emergency-exit:active{transform:scale(.96)}'
      document.head.appendChild(s)
    }
    const btn = document.createElement('button')
    btn.id = 'voice-emergency-exit'
    btn.setAttribute('aria-label', 'Cerrar modo voz')
    btn.title = 'Cerrar modo voz y volver al Dashboard'
    btn.innerHTML = '<span style="color:#f87171;font-weight:700">✕</span><span>Cerrar</span>'
    // Diseño integrado a la barra superior: mismo look que Reiniciar, avatar ✕ en rojo
    btn.style.cssText =
      'position:fixed;top:12px;right:16px;z-index:2147483647;' +
      'display:inline-flex;align-items:center;gap:6px;background:rgba(30,41,59,.85);' +
      'color:#cbd5e1;border:1px solid #334155;border-radius:8px;padding:6px 12px;' +
      'font:500 12px/1 system-ui,-apple-system,sans-serif;cursor:pointer;' +
      'transition:background-color .15s,color .15s,transform .1s'
    let disparado = false
    const disparar = (e) => {
      if (disparado) return
      disparado = true
      e.preventDefault()
      e.stopImmediatePropagation()
      setTimeout(salir, 0)
    }
    // Tres tipos de evento: si una extensión traga 'click', mousedown/touchend pasan igual
    btn.addEventListener('click', disparar)
    btn.addEventListener('mousedown', disparar)
    btn.addEventListener('touchend', disparar)
    document.body.appendChild(btn)
    return () => {
      btn.remove()
    }
  }, [isOpen])

  // Puente para el cable de emergencia: el handler de cierre sano de React
  useEffect(() => {
    window.__voiceSalirAlDashboard = () => salirAlDashboard()
    return () => delete window.__voiceSalirAlDashboard
  })

  // Activación por teclado: Escape = salir, Enter/Espacio = acción principal del estado
  useEffect(() => {
    if (!isOpen) return
    const onKey = (e) => {
      if (e.key === 'Escape') {
        salirAlDashboard()
        return
      }
      // No robar Enter/Espacio a los botones enfocados: ellos ya disparan su propio onClick
      const target = e.target
      if (target instanceof HTMLElement && (target.tagName === 'BUTTON' || target.tagName === 'INPUT' || target.tagName === 'TEXTAREA')) {
        return
      }
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        if (isConfirming) {
          confirmarOperacion()
        } else if (isListeningNow) {
          detenerYEnviar()
        } else if (isSpeakingNow) {
          omitirRespuesta()
        } else if (isError || !isActive) {
          activarModoVoz(true)
        }
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [isOpen, voiceState, isConfirming, isListeningNow, isSpeakingNow, isError, isActive, activarModoVoz, desactivarModoVoz, detenerYEnviar, omitirRespuesta, confirmarOperacion, onClose])

  const handleOrbClick = () => {
    if (voiceState === VoiceTurnState.LISTENING || voiceState === VoiceTurnState.SPEECH_DETECTED) {
      detenerYEnviar()
    } else if (voiceState === VoiceTurnState.READY) {
      if (typeof iniciarEscucha === 'function') {
        iniciarEscucha()
      } else {
        activarModoVoz(false)
      }
    } else if (voiceState === VoiceTurnState.IDLE) {
      activarModoVoz(true)
    } else if (voiceState === VoiceTurnState.PROCESSING) {
      console.log('[MostradorMode] Usuario tocó el orbe durante PROCESSING: reseteando sesión...')
      desactivarModoVoz()
      setTimeout(() => activarModoVoz(false), 200)
    } else if (voiceState === VoiceTurnState.SPEAKING || voiceState === VoiceTurnState.SETTLING) {
      console.log('[MostradorMode] Usuario tocó el orbe durante SPEAKING: omitiendo audio y reanudando escucha...')
      omitirRespuesta()
    } else if (isError) {
      console.log('[MostradorMode] Usuario tocó el orbe durante ERROR: reintentando...')
      activarModoVoz(true)
    }
  }

  // Todos los hooks ya corrieron arriba: este retorno es legal (Rules of Hooks).
  // Sin esta condición el overlay se pintaba SIEMPRE (por eso solo loguear ya
  // mostraba la orbe sin que nadie la abriera).
  if (!isOpen) return null

  return createPortal(
    <div
      tabIndex={-1}
      data-voice-overlay="1"
      className="pointer-events-auto fixed inset-0 z-[70] bg-slate-950 flex flex-col justify-between p-4 md:p-6 text-white select-none animate-in fade-in duration-200 outline-none"
    >
      {/* Barra superior de control */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${isActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
          <span className="text-xs md:text-sm font-semibold tracking-wider text-slate-300 uppercase truncate">
            Modo Mostrador • Manos Libres
          </span>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {/* Indicador inequívoco de servicio PRENDIDO / APAGADO */}
          <span
            className={`hidden sm:inline-flex px-2.5 py-1 rounded-full text-[10px] md:text-xs font-bold uppercase tracking-wider border ${
              isError ? 'bg-red-950 border-red-600 text-red-300' :
              isActive ? 'bg-emerald-950 border-emerald-600 text-emerald-300' : 'bg-slate-900 border-slate-700 text-slate-400'
            }`}
          >
            {isError
              ? '🔴 Servicio: Error'
              : isActive
                ? isSpeakingNow ? '🟢 Servicio: Hablando' : isListeningNow ? '🟢 Servicio: Escuchando' : '🟢 Servicio: Activo'
                : '⚪ Servicio: Apagado'}
          </span>

          {/* Botón de Diagnósticos / Logs para móvil */}
          <button
            onClick={() => setMostrarLogs(prev => !prev)}
            title="Ver bitácora de eventos del modo voz"
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-all ${
              mostrarLogs
                ? 'bg-cyan-950 border-cyan-500 text-cyan-300'
                : 'bg-slate-800/80 hover:bg-slate-700 text-slate-300 border-slate-700'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span className="text-[11px]">Logs</span>
          </button>

          {/* Reiniciar sesión de voz (siempre disponible, kit de emergencia) */}
          <button
            onClick={reiniciarSesion}
            title="Reiniciar sesión de voz (apaga y prende el servicio)"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 active:scale-95 transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="hidden sm:inline">Reiniciar</span>
          </button>

          {/* Espacio reservado para el botón nativo "Cerrar modo voz" (DOM puro, brazo derecho de la barra) */}
          <div className="w-[120px] shrink-0" aria-hidden="true" />
        </div>
      </div>

      {/* Zona Central: Orbe y transcripciones legibles a 1 metro */}
      <div className="flex-1 flex flex-col items-center justify-center max-w-lg mx-auto w-full my-auto text-center px-2">
        {/* Orbe Visual Interactivo (Tap-to-send) */}
        <VoiceOrb state={voiceState} size="large" onClick={handleOrbClick} />

        {(voiceState === VoiceTurnState.LISTENING || voiceState === VoiceTurnState.SPEECH_DETECTED) && (
          <span className="text-xs text-slate-500 -mt-2 mb-2 animate-in fade-in">
            Habla a tu ritmo natural • Toca el orbe para enviar ya
          </span>
        )}

        {/* Transcripción en vivo de lo que dice el tendero */}
        {transcript && (
          <div className="mt-2 text-slate-400 text-sm md:text-base font-medium italic min-h-[1.5rem]">
            "{transcript}"
          </div>
        )}

        {/* Respuesta del Asistente */}
        {lastResponse?.respuesta && (
          <div className="mt-4 px-4 py-3 rounded-xl bg-slate-900/80 border border-slate-800 text-slate-100 text-base md:text-xl font-medium leading-relaxed max-w-md shadow-lg">
            {lastResponse.respuesta}
          </div>
        )}

        {/* Opciones de aclaración si hay ambigüedad de productos */}
        {clarification?.options && clarification.options.length > 0 && (
          <div className="mt-4 flex flex-col gap-2 w-full max-w-sm">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Elige o di el producto:
            </span>
            {clarification.options.map((opt, idx) => {
              const nombreLimpio = (opt.label || '').split('(')[0].trim()
              return (
                <button
                  key={opt.id || idx}
                  onClick={() => seleccionarOpcion(nombreLimpio || String(idx + 1))}
                  className="px-4 py-2.5 rounded-xl bg-slate-900 border border-cyan-500/40 hover:border-cyan-400 text-left text-sm font-medium text-cyan-200 active:scale-98 transition-all flex items-center justify-between"
                >
                  <span>{opt.label}</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                    Opción {idx + 1}
                  </span>
                </button>
              )
            })}
          </div>
        )}

        {/* Tarjeta Gigante de Confirmación (Legible a distancia) */}
        {isConfirming && preview && (
          <div className="mt-5 w-full max-w-sm rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border-2 border-emerald-500/70 p-5 shadow-[0_0_40px_rgba(16,185,129,0.25)] animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between text-xs text-emerald-400 font-bold uppercase tracking-wider mb-2">
              <span>{preview.accion === 'reabastecer' ? 'Reabastecimiento' : 'Registro de Venta'}</span>
              <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300">
                Pendiente
              </span>
            </div>

            <div className="text-xl md:text-2xl font-bold text-white mb-1">
              {preview.cantidad} × {preview.producto_nombre}
            </div>

            {preview.total_estimado != null && (
              <div className="text-2xl md:text-3xl font-extrabold text-emerald-400 my-2">
                ${Number(preview.total_estimado).toLocaleString('es-CO')}
              </div>
            )}

            <p className="text-xs text-slate-400 mt-2">
              Di <strong className="text-white">"Sí, dale"</strong> o toca el botón:
            </p>

            {/* Botones táctiles de respaldo (Comparten el mismo camino transaccional) */}
            <div className="mt-4 grid grid-cols-2 gap-3">
              <button
                onClick={confirmarOperacion}
                disabled={voiceState === VoiceTurnState.PROCESSING}
                className={`py-3 px-4 rounded-xl font-bold text-base flex items-center justify-center gap-1.5 shadow-lg transition-all ${
                  voiceState === VoiceTurnState.PROCESSING
                    ? 'bg-emerald-800/60 text-emerald-200/70 cursor-not-allowed'
                    : 'bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white active:scale-95'
                }`}
              >
                <Check className="w-5 h-5" />
                <span>{voiceState === VoiceTurnState.PROCESSING ? 'Procesando...' : 'Confirmar'}</span>
              </button>

              <button
                onClick={cancelarOperacion}
                disabled={voiceState === VoiceTurnState.PROCESSING}
                className={`py-3 px-4 rounded-xl font-semibold text-base flex items-center justify-center gap-1.5 border border-slate-700 transition-all ${
                  voiceState === VoiceTurnState.PROCESSING
                    ? 'bg-slate-900/60 text-slate-500 cursor-not-allowed'
                    : 'bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-300 active:scale-95'
                }`}
              >
                <X className="w-5 h-5" />
                <span>Cancelar</span>
              </button>
            </div>
          </div>
        )}

        {/* Mensaje de Error Amigable */}
        {errorMessage && (
          <div className="mt-4 px-4 py-2 rounded-xl bg-rose-950/80 border border-rose-800/80 text-rose-200 text-xs md:text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>


      {/* Panel flotante de diagnóstico para móvil */}
      {mostrarLogs && (
        <div className="absolute inset-x-2 top-16 bottom-20 z-50 bg-slate-900/95 border border-slate-700 rounded-2xl p-3 flex flex-col backdrop-blur-md shadow-2xl animate-in fade-in zoom-in-95 duration-150">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs text-slate-300">
            <span className="font-bold flex items-center gap-1.5 text-cyan-400">
              <Terminal className="w-3.5 h-3.5" /> Diagnóstico de Voz en Vivo (Móvil)
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setLogsRecientes([])}
                className="text-[10px] text-slate-400 hover:text-white px-2 py-0.5 rounded bg-slate-800 border border-slate-700"
              >
                Limpiar
              </button>
              <button
                onClick={() => setMostrarLogs(false)}
                className="text-slate-400 hover:text-white p-1"
              >
                ✕
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto mt-2 space-y-1 font-mono text-[11px] text-left">
            {logsRecientes.length === 0 ? (
              <p className="text-slate-500 italic p-4 text-center">No hay eventos recientes aún. Habla o interactúa con el orbe.</p>
            ) : (
              logsRecientes.map(l => (
                <div
                  key={l.id}
                  className={`p-1.5 rounded border text-[10.5px] leading-relaxed break-all ${
                    l.tipo === 'error'
                      ? 'bg-rose-950/60 border-rose-800 text-rose-300'
                      : l.tipo === 'warn'
                        ? 'bg-amber-950/60 border-amber-800 text-amber-300'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300'
                  }`}
                >
                  <span className="text-slate-500 mr-1.5">[{l.time}]</span>
                  <span>{l.msg}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Barra Inferior: Activación / Estado */}
      <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Volume2 className="w-4 h-4 text-slate-400" />
          <span>Voz: Español (Colombia / Latinoamérica)</span>
        </div>

        {!isActive || isError ? (
          <button
            onClick={() => activarModoVoz(true)}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/30 active:scale-95 transition-all"
          >
            <Mic className="w-4 h-4" />
            <span>{isError ? 'Reintentar Escucha' : 'Toca para Iniciar Escucha'}</span>
          </button>
        ) : voiceState === VoiceTurnState.SPEAKING ? (
          <button
            onClick={omitirRespuesta}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold text-sm flex items-center justify-center gap-2 active:scale-95 transition-all"
          >
            <Volume2 className="w-4 h-4" />
            <span>Hablando... toca para omitir</span>
          </button>
        ) : (
          <div className="flex items-center gap-2 text-slate-400">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>Escuchando por turnos discretos</span>
          </div>
        )}
      </div>
    </div>,
    document.body
  )
}
