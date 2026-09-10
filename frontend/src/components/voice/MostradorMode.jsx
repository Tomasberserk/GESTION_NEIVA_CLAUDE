import React from 'react'
import { X, Mic, MicOff, Check, AlertCircle, Sparkles, Volume2 } from 'lucide-react'
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
  if (!isOpen) return null

  const {
    voiceState,
    transcript,
    lastResponse,
    errorMessage,
    activarModoVoz,
    desactivarModoVoz,
    detenerYEnviar,
    confirmarOperacion,
    cancelarOperacion,
    seleccionarOpcion,
    isActive,
  } = voiceAgent

  const preview = lastResponse?.preview
  const clarification = lastResponse?.clarification
  const isConfirming = voiceState === VoiceTurnState.CONFIRMING || lastResponse?.estado === 'READY_TO_CONFIRM'

  const handleOrbClick = () => {
    if (voiceState === VoiceTurnState.LISTENING || voiceState === VoiceTurnState.SPEECH_DETECTED) {
      detenerYEnviar()
    } else if (voiceState === VoiceTurnState.READY) {
      activarModoVoz(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-slate-950 flex flex-col justify-between p-4 md:p-6 text-white select-none animate-in fade-in duration-200">
      {/* Barra superior de control */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs md:text-sm font-semibold tracking-wider text-slate-300 uppercase">
            Modo Mostrador • Manos Libres
          </span>
        </div>

        <button
          onClick={() => {
            desactivarModoVoz()
            onClose()
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 active:scale-95 transition-all"
        >
          <X className="w-4 h-4" />
          <span>Salir</span>
        </button>
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
                className="py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-bold text-base flex items-center justify-center gap-1.5 shadow-lg active:scale-95 transition-all"
              >
                <Check className="w-5 h-5" />
                <span>Confirmar</span>
              </button>

              <button
                onClick={cancelarOperacion}
                className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-300 font-semibold text-base flex items-center justify-center gap-1.5 border border-slate-700 active:scale-95 transition-all"
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

      {/* Barra Inferior: Activación / Estado */}
      <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Volume2 className="w-4 h-4 text-slate-400" />
          <span>Voz: Español (Colombia / Latinoamérica)</span>
        </div>

        {!isActive ? (
          <button
            onClick={activarModoVoz}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/30 active:scale-95 transition-all"
          >
            <Mic className="w-4 h-4" />
            <span>Toca para Iniciar Escucha</span>
          </button>
        ) : (
          <div className="flex items-center gap-2 text-slate-400">
            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>Escuchando por turnos discretos</span>
          </div>
        )}
      </div>
    </div>
  )
}
