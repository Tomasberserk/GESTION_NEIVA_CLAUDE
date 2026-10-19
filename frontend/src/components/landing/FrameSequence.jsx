import { useEffect, useRef, useState } from 'react'
import { motion, useScroll, useReducedMotion } from 'motion/react'

/**
 * FrameSequence — scroll-telling ligado directo al scroll (sin spring:
 * el usuario no debe sentir la imagen persiguiéndolo en un terminal lento).
 *
 * - Dibujo coalescido con requestAnimationFrame: se descartan frames obsoletos.
 * - Ventana de caché acotada (WINDOW = 8): solo se precargan frames cercanos y
 *   los lejanos se sueltan (120 frames decodificados a la vez ≈ 237 MB teóricos).
 * - Pausa total cuando la sección sale del viewport o la pestaña se oculta.
 * - Sin JS / reduced-motion: <img> estático del frame final (contenido visible).
 */
const WINDOW = 8

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
  const stateRef = useRef({ target: 0, drawn: -1, pending: false })
  const pausedRef = useRef(true)
  const [activeStep, setActiveStep] = useState(0)
  const [alive, setAlive] = useState(true) // inView && pestaña visible
  const reduce = useReducedMotion()

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ['start start', 'end end'],
  })

  // Pausa cuando no se ve o la pestaña está en segundo plano (auditoría §5D)
  useEffect(() => {
    const node = sectionRef.current
    if (!node) return
    let inView = false
    let visible = document.visibilityState === 'visible'
    const sync = () => {
      pausedRef.current = !(inView && visible)
      setAlive(inView && visible)
    }
    const obs = new IntersectionObserver(
      ([entry]) => { inView = entry.isIntersecting; sync() },
      { rootMargin: '120px 0px' },
    )
    obs.observe(node)
    const onVis = () => { visible = document.visibilityState === 'visible'; sync() }
    document.addEventListener('visibilitychange', onVis)
    return () => {
      obs.disconnect()
      document.removeEventListener('visibilitychange', onVis)
    }
  }, [])

  const src = (n) => pattern.replace('{n}', String(n).padStart(pad, '0'))

  // Dibujo con cover-fit (sin deformar)
  const drawImageTo = (c, img) => {
    const ctx = c.getContext('2d')
    if (!ctx) return
    const scale = Math.max(c.width / img.naturalWidth, c.height / img.naturalHeight)
    const w = img.naturalWidth * scale
    const h = img.naturalHeight * scale
    ctx.drawImage(img, (c.width - w) / 2, (c.height - h) / 2, w, h)
  }

  const drawNearest = (target) => {
    const c = canvasRef.current
    if (!c) return
    for (let d = 0; d < WINDOW * 2; d++) {
      for (const n of d === 0 ? [target] : [target - d, target + d]) {
        if (n < 0 || n > frames - 1) continue
        const img = cacheRef.current[n]
        if (img?.complete && img.naturalWidth) {
          drawImageTo(c, img)
          return true
        }
      }
    }
    return false
  }

  useEffect(() => {
    if (reduce) return

    const targetFrom = (v) =>
      Math.max(0, Math.min(frames - 1, Math.round(v * (frames - 1))))

    // Poster inmediato: primer frame con prioridad
    const load = (n) => {
      if (cacheRef.current[n]) return
      const img = new Image()
      img.onload = () => {
        if (stateRef.current.drawn < 0 && n < 4 && !pausedRef.current) {
          // pintar el primer frame en cuanto llegue (el canvas nunca queda negro)
          const c = canvasRef.current
          if (c) { drawImageTo(c, img); stateRef.current.drawn = 0 }
        }
      }
      img.src = src(n)
      img.decoding = 'async'
      cacheRef.current[n] = img
    }
    for (let n = 0; n < 4; n++) load(n)

    let lastTarget = -1
    let rafId = null

    const paintTarget = () => {
      const { target, drawn } = stateRef.current
      if (target === drawn) return
      const ok = drawNearest(target)
      stateRef.current.drawn = ok ? target : drawn
      const stepCount = steps.length
      if (ok && stepCount) {
        const v = target / (frames - 1)
        setActiveStep(Math.min(stepCount - 1, Math.floor(v * stepCount)))
      }
    }

    const schedule = () => {
      if (rafId != null || pausedRef.current) return // coalescer + pausa fuera de viewport
      rafId = requestAnimationFrame(() => {
        rafId = null
        if (pausedRef.current) return
        const t = targetFrom(scrollYProgress.get())
        if (t !== lastTarget) {
          // ventana de precarga alrededor del target (auditoría §5C)
          const lo = Math.max(0, t - WINDOW / 2)
          const hi = Math.min(frames - 1, t + WINDOW / 2)
          for (let n = lo; n <= hi; n++) load(n)
          // soltar frames lejanos (limpieza de memoria)
          for (const key of Object.keys(cacheRef.current)) {
            const n = Number(key)
            if (n < t - WINDOW || n > t + WINDOW) delete cacheRef.current[n]
          }
          lastTarget = t
          stateRef.current.target = t
        }
        paintTarget()
      })
    }

    const unsub = scrollYProgress.on('change', schedule)

    return () => { unsub(); if (rafId != null) cancelAnimationFrame(rafId) }
  }, [reduce]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <section
      ref={sectionRef}
      id={id}
      aria-label={steps[0]?.title || 'Recorrido en imágenes'}
      className={`relative ${heightClass} lnd`}
      style={{ background: 'var(--noche)' }}
    >
      <div className="sticky top-0 h-screen overflow-hidden">
        {reduce ? (
          <img
            src={src(frames - 1)}
            alt={steps.at(-1)?.title || 'Tienda en funcionamiento'}
            className="absolute inset-0 h-full w-full object-cover"
          />
        ) : (
          <canvas
            ref={canvasRef}
            width={960}
            height={540}
            aria-hidden="true"
            className="absolute inset-0 h-full w-full object-cover bg-[#101613]"
          />
        )}

        {/* Veta oscura estable para legibilidad (auditoría §6B) */}
        <div
          className="absolute inset-0"
          style={{
            background:
              'linear-gradient(to top, rgba(16,22,19,.94) 0%, rgba(16,22,19,.55) 30%, rgba(16,22,19,.15) 55%, rgba(16,22,19,.45) 100%)',
          }}
        />

        <div className="absolute inset-x-0 bottom-12 sm:bottom-16 px-5 sm:px-8">
          <div className="mx-auto max-w-3xl space-y-5">
            <div
              className="flex items-center gap-3 font-mono text-[11px] tracking-widest uppercase"
              style={{ color: 'var(--tinta-suave)' }}
            >
              <span>Del mostrador a la claridad</span>
              <span className="h-px flex-1" style={{ background: 'var(--linea)' }} />
              <span style={{ color: 'var(--ambar)' }}>
                {String(activeStep + 1).padStart(2, '0')}/{String(steps.length).padStart(2, '0')}
              </span>
            </div>

            {reduce ? (
              /* Sin motion: la historia completa, apilada y legible (SKILL.md:
                 el canvas necesita alternativa textual equivalente, y el
                 contenido no puede depender de la animación). */
              <div className="space-y-4">
                {steps.map((s, i) => (
                  <div key={s.title}>
                    <h3
                      className="text-2xl font-black tracking-tight"
                      style={{ color: 'var(--crema)', lineHeight: 1.08 }}
                    >
                      {String(i + 1).padStart(2, '0')} — {s.title}
                    </h3>
                    <p className="mt-1 max-w-xl text-sm leading-relaxed" style={{ color: '#d5ddd6' }}>
                      {s.text}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="relative h-[140px] sm:h-[170px]">
                {steps.map((s, i) => (
                  <motion.div
                    key={s.title}
                    initial={false}
                    animate={{
                      opacity: i === activeStep ? 1 : 0,
                      y: i === activeStep ? 0 : 8,
                    }}
                    // Curva final explícita (auditoría §3A): 420ms, cubic-bezier(.22,1,.36,1)
                    transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
                    className={i === activeStep ? 'block' : 'hidden'}
                  >
                    <h3
                      className="text-2xl sm:text-4xl font-black tracking-tight"
                      style={{ color: 'var(--crema)', lineHeight: 1.08 }}
                    >
                      {s.title}
                    </h3>
                    <p
                      className="mt-2 max-w-xl text-sm sm:text-base leading-relaxed"
                      style={{ color: '#d5ddd6' }}
                    >
                      {s.text}
                    </p>
                  </motion.div>
                ))}
              </div>
            )}

            <div className="flex gap-1.5">
              {steps.map((_, i) => (
                <div
                  key={i}
                  className="h-1 flex-1 rounded-full transition-opacity duration-300"
                  style={{ background: 'var(--crema)', opacity: i <= activeStep ? 0.9 : 0.25 }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
