import React from 'react'
import { VoiceTurnState } from '../../services/voice/VoiceTurnManager'

/**
 * VoiceOrb: Componente visual de presentación pura para el Modo Voz.
 * Construido 100% en CSS3 acelerado por GPU (transform, opacity, radial-gradient).
 * Garantiza >=50 FPS sin long tasks ni recalentamiento en teléfonos Android de 2019.
 */
export default function VoiceOrb({ state = VoiceTurnState.IDLE, size = 'large' }) {
  const isLarge = size === 'large'
  const orbSize = isLarge ? 'w-44 h-44 md:w-56 md:h-56' : 'w-24 h-24'

  // Configuración de colores y animaciones según la máquina de estados
  const getOrbConfig = () => {
    switch (state) {
      case VoiceTurnState.LISTENING:
        return {
          glow: 'from-cyan-400 via-blue-500 to-indigo-600',
          shadow: 'shadow-[0_0_50px_rgba(6,182,212,0.6)]',
          animation: 'animate-pulse',
          pulseScale: 'scale-105',
          label: 'Escuchando...',
          textColor: 'text-cyan-400',
          ringColor: 'border-cyan-400/40',
        }

      case VoiceTurnState.SPEECH_DETECTED:
        return {
          glow: 'from-sky-300 via-cyan-500 to-blue-600',
          shadow: 'shadow-[0_0_70px_rgba(14,165,233,0.8)]',
          animation: 'animate-ping',
          pulseScale: 'scale-110',
          label: 'Te escucho...',
          textColor: 'text-sky-300',
          ringColor: 'border-sky-400/60',
        }

      case VoiceTurnState.PROCESSING:
        return {
          glow: 'from-indigo-400 via-purple-500 to-violet-700',
          shadow: 'shadow-[0_0_50px_rgba(139,92,246,0.5)]',
          animation: 'animate-spin',
          pulseScale: 'scale-95',
          label: 'Pensando...',
          textColor: 'text-indigo-400',
          ringColor: 'border-indigo-400/30',
        }

      case VoiceTurnState.SPEAKING:
        return {
          glow: 'from-emerald-400 via-teal-500 to-cyan-600',
          shadow: 'shadow-[0_0_60px_rgba(16,185,129,0.6)]',
          animation: 'animate-pulse',
          pulseScale: 'scale-105',
          label: 'Hablando...',
          textColor: 'text-emerald-400',
          ringColor: 'border-emerald-400/40',
        }

      case VoiceTurnState.CONFIRMING:
        return {
          glow: 'from-emerald-400 via-green-500 to-teal-600',
          shadow: 'shadow-[0_0_80px_rgba(34,197,94,0.7)]',
          animation: 'animate-bounce',
          pulseScale: 'scale-110',
          label: '¿Confirmamos?',
          textColor: 'text-green-400',
          ringColor: 'border-green-400/60',
        }

      case VoiceTurnState.ERROR:
        return {
          glow: 'from-amber-400 via-rose-500 to-red-600',
          shadow: 'shadow-[0_0_50px_rgba(239,68,68,0.6)]',
          animation: 'animate-pulse',
          pulseScale: 'scale-90',
          label: 'Atención',
          textColor: 'text-rose-400',
          ringColor: 'border-rose-400/40',
        }

      case VoiceTurnState.READY:
      case VoiceTurnState.IDLE:
      default:
        return {
          glow: 'from-slate-600 via-slate-700 to-slate-800',
          shadow: 'shadow-[0_0_30px_rgba(100,116,139,0.3)]',
          animation: '',
          pulseScale: 'scale-100',
          label: 'Listo',
          textColor: 'text-slate-400',
          ringColor: 'border-slate-600/30',
        }
    }
  }

  const config = getOrbConfig()

  return (
    <div className="flex flex-col items-center justify-center select-none py-4">
      {/* Contenedor relativo para capas concéntricas aceleradas por GPU */}
      <div className={`relative flex items-center justify-center ${orbSize}`}>
        {/* Anillo exterior reactivo */}
        <div
          className={`absolute inset-0 rounded-full border-2 ${config.ringColor} transition-all duration-500 will-change-transform ${
            state === VoiceTurnState.SPEAKING || state === VoiceTurnState.CONFIRMING ? 'scale-125 opacity-70 animate-ping' : 'scale-100 opacity-30'
          }`}
          style={{ transform: 'translateZ(0)' }}
        />

        {/* Anillo intermedio difuso */}
        <div
          className={`absolute inset-2 rounded-full bg-gradient-to-tr ${config.glow} opacity-30 blur-xl transition-all duration-700 will-change-transform`}
          style={{ transform: 'translateZ(0)' }}
        />

        {/* Núcleo del Orbe con gradiente y sombras suaves */}
        <div
          className={`relative w-full h-full rounded-full bg-gradient-to-br ${config.glow} ${config.shadow} ${config.pulseScale} transition-transform duration-300 ease-out flex items-center justify-center will-change-transform`}
          style={{ transform: 'translateZ(0)' }}
        >
          {/* Brillo interno especular */}
          <div className="absolute top-2 left-4 w-1/3 h-1/3 rounded-full bg-white/25 blur-sm" />

          {/* Icono de estado central sutil */}
          <div className="text-white/80 font-medium text-xs tracking-widest uppercase">
            {state === VoiceTurnState.PROCESSING && (
              <div className="w-8 h-8 rounded-full border-2 border-white/30 border-t-white animate-spin" />
            )}
            {state === VoiceTurnState.CONFIRMING && (
              <span className="text-2xl font-bold">✓</span>
            )}
          </div>
        </div>
      </div>

      {/* Etiqueta de estado en español legible a distancia */}
      <span className={`mt-4 text-sm md:text-base font-semibold tracking-wide transition-colors duration-300 ${config.textColor}`}>
        {config.label}
      </span>
    </div>
  )
}
