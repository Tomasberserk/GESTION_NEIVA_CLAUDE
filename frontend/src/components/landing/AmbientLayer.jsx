/**
 * AmbientLayer — textura ambiental de marca (motas + niebla + mesh)
 * Sin dependencias: posiciones deterministas (nada de Math.random en render).
 * Cero interacción con pointer-events para no comerse clicks del contenido.
 */
export default function AmbientLayer({ motes = 18 }) {
  const items = Array.from({ length: motes }, (_, i) => ({
    left: (37 * i) % 100,
    top: 20 + ((53 * i) % 75),
    size: 2 + (i % 3),
    delay: (0.9 * i) % 12,
    duration: 10 + ((i % 5) * 2),
  }))

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      {/* Gradient mesh: 3 focos de luz cálida sobre bosque */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(60% 45% at 18% 12%, rgba(216,154,61,.13) 0%, transparent 60%),' +
            'radial-gradient(50% 40% at 85% 8%,  rgba(216,154,61,.07) 0%, transparent 55%),' +
            'radial-gradient(70% 60% at 50% 105%, rgba(27,61,46,.55) 0%, transparent 70%)',
        }}
      />

      {/* Niebla cálido-cinematográfica */}
      <div
        className="lnd-mist absolute -inset-x-10 -bottom-1/4 h-1/2"
        style={{
          background:
            'radial-gradient(55% 100% at 30% 60%, rgba(216,154,61,.10) 0%, transparent 60%),' +
            'radial-gradient(45% 90% at 75% 55%, rgba(245,239,230,.06) 0%, transparent 60%)',
          filter: 'blur(12px)',
        }}
      />

      {/* Motas flotantes (como polvo en el haz de luz del persiano) */}
      {items.map((m, i) => (
        <span
          key={i}
          className="lnd-mote absolute rounded-full"
          style={{
            left: `${m.left}%`,
            top: `${m.top}%`,
            width: m.size,
            height: m.size,
            background: 'rgba(245,239,230,.55)',
            animationDelay: `${m.delay}s`,
            animationDuration: `${m.duration}s`,
          }}
        />
      ))}
    </div>
  )
}
