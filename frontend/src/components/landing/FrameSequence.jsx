import { useEffect, useRef, useState } from 'react'
import {
  motion,
  useScroll,
  useSpring,
  useTransform,
  useReducedMotion,
} from 'motion/react'

/**
 * FrameSequence — scroll-telling estilo Apple (portado del análisis ORIVIA).
 * Una secuencia de N fotogramas webp se dibuja en un <canvas> sticky;
 * el progreso del scroll con spring físico la recorre como un video.
 *
 * Fallback sin-JS / reduced-motion: se muestra el frame final como <img>.
 */
export default function FrameSequence({
  pattern = '/media/viaje/v{n}.webp',
  frames = 120,
  pad = 3,
  steps = [],
  heightClass = 'h-[420svh]',
  id,
}) {
  const sectionRef = useRef(null)
  const canvasRef = useRef(null)
  const cacheRef = useRef({})
  const [activeStep, setActiveStep] = useState(0)
  const reduce = useReducedMotion()

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start start', 'end end'],
  })
  const smooth = useSpring(scrollYProgress, { stiffness: 90, damping: 22, mass: 0.5 })

  const src = (n) => pattern.replace('{n}', String(n).padStart(pad, '0'))

  useEffect(() => {
    if (reduce) return
    const draw = (n) => {
      const c = canvasRef.current
      if (!c) return
      const img = cacheRef.current[n]
      if (!img || !img.complete || !img.naturalWidth) {
        // Si el frame aún no llega, dibuja el más cercano ya cargado
        for (let w = 1; w < 15; w++) {
          const a = cacheRef.current[n - w]
          const b = cacheRef.current[n + w]
          if (a?.complete && a.naturalWidth) { return drawImageTo(c, a) }
          if (b?.complete && b.naturalWidth) { return drawImageTo(c, b) }
        }
        return
      }
      drawImageTo(c, img)
    }

    const load = (n) => {
      if (cacheRef.current[n]) return
      const img = new Image()
      img.src = src(n)
      img.onload = () => draw(n)
      cacheRef.current[n] = img
    }

    // Precarga amino inicial: los primeros 12 frames (el tramo que ve al entrar)
    const first = []
    for (let n = 0; n < 12; n++) first.push(n)
    first.forEach(load)

    // Precarga progresiva por ventana según el frame objetivo
    let lastLoaded = -1
    const unsub = smooth.on('change', (v) => {
      const target = Math.max(0, Math.min(frames - 1, Math.round(v * (frames - 1))))
      // ventana ±14 alrededor del target
      for (let n = Math.max(0, target - 14); n <= Math.min(frames - 1, target + 14); n++) {
        load(n)
      }
      if (target !== lastLoaded) {
        lastLoaded = target
        draw(target)
        // paso narrativo activo
        const stepCount = steps.length
        if (stepCount) setActiveStep(Math.min(stepCount - 1, Math.floor(v * stepCount)))
      }
    })
    return () => unsub()
  }, [reduce]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <section
      ref={sectionRef}
      id={id}
      aria-label={steps[0]?.label || 'Recorrido en imágenes'}
      className={`relative ${heightClass} lnd`}
      style={{ background: 'var(--noche)' }}
    >
      <div className="sticky top-0 h-screen overflow-hidden">
        {reduce ? (
          <img
            src={src(frames - 1)}
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-90"
          />
        ) : (
          <canvas
            ref={canvasRef}
            width={960}
            height={540}
            className="absolute inset-0 h-full w-full object-cover"
          />
        )}

        {/* Vignette para legibilidad del texto */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'linear-gradient(to top, rgba(16,22,19,.92) 0%, rgba(16,22,19,.35) 38%, rgba(16,22,19,.25) 70%, rgba(16,22,19,.55) 100%)',
          }}
        />

        {/* Overlays narrativos por paso */}
        <div className="absolute inset-x-0 bottom-14 sm:bottom-20 px-5 sm:px-8">
          <div className="mx-auto max-w-3xl space-y-6">
            <div className="flex items-center gap-3 font-mono text-[11px] tracking-widest uppercase" style={{ color: 'var(--tinta-suave)' }}>
              <span>Del mostrador a la claridad</span>
              <span className="h-px flex-1" style={{ background: 'var(--linea)' }} />
              <span style={{ color: 'var(--ambar)' }}>
                {String(activeStep + 1).padStart(2, '0')}/{String(steps.length).padStart(2, '0')}
              </span>
            </div>

            {steps.map((s, i) => (
              <motion.div
                key={s.title}
                initial={false}
                animate={{
                  opacity: i === activeStep ? 1 : 0,
                  y: i === activeStep ? 0 : 12,
                }}
                transition={{ duration: 0.45, ease: 'easeOut' }}
                className={i === activeStep ? 'block' : 'hidden'}
              >
                <h3
                  className="text-2xl sm:text-4xl font-black tracking-tight"
                  style={{ color: 'var(--crema)' }}
                >
                  {s.title}
                </h3>
                <p className="mt-2 max-w-xl text-sm sm:text-base leading-relaxed" style={{ color: 'var(--tinta-suave)' }}>
                  {s.text}
                </p>
              </motion.div>
            ))}

            {/* Progreso */}
            <div className="flex gap-1.5">
              {steps.map((_, i) => (
                <div
                  key={i}
                  className="h-1 flex-1 rounded-full transition-opacity"
                  style={{
                    background: 'var(--crema)',
                    opacity: i <= activeStep ? 0.9 : 0.25,
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function drawImageTo(c, img) {
  const ctx = c.getContext('2d')
  if (!ctx) return
  // cover-fit: recorta centrado para llenar el canvas sin deformar
  const scale = Math.max(c.width / img.naturalWidth, c.height / img.naturalHeight)
  const w = img.naturalWidth * scale
  const h = img.naturalHeight * scale
  ctx.drawImage(img, (c.width - w) / 2, (c.height - h) / 2, w, h)
}
