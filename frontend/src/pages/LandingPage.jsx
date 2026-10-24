import { useState, useLayoutEffect, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import './../styles/landing.css'
import {
  Store,
  ChevronDown,
  Play,
  X,
  CheckCircle2,
  HelpCircle,
  Users,
  ShieldCheck,
  Scale,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Package,
  BookOpen,
  HeartHandshake,
  MessageCircle,
} from 'lucide-react'

export default function LandingPage() {
  const [videoModalAbierto, setVideoModalAbierto] = useState(false)
  const [faqAbierta, setFaqAbierta] = useState(null)
  const [scrolled, setScrolled] = useState(false)
  const rootRef = useRef(null)
  const hdSentinelRef = useRef(null)

  // Arma los reveals ANTES del primer paint (el contenido es visible sin JS:
  // la clase .js-reveal-arm se pierde => CSS deja los elementos visibles).
  useLayoutEffect(() => {
    rootRef.current?.classList.add('lnd', 'js-reveal-arm')
  }, [])

  useEffect(() => {
    // Header: sólido cuando el FIN del hero cruza la línea del header (~88px).
    // Lectura directa del sentinel en cada scroll: los saltos por ancla no
    // siempre disparan eventos de IntersectionObserver, pero sí scroll.
    let obsHeader
    const mount = () => {
      const sentinel = hdSentinelRef.current
      if (!sentinel) return
      let last = null
      const update = () => {
        const solid = sentinel.getBoundingClientRect().top < 88
        if (solid !== last) { last = solid; setScrolled(solid) }
      }
      update()
      window.addEventListener('scroll', update, { passive: true })
      window.addEventListener('resize', update, { passive: true })
      obsHeader = { disconnect: () => {
        window.removeEventListener('scroll', update)
        window.removeEventListener('resize', update)
      } }
    }
    mount()
    // Reveals: un solo ciclo por elemento (IO se desconecta al entrar una vez)
    const obs = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('in-view')
            obs.unobserve(e.target)
          }
        }),
      { threshold: 0.13 },
    )
    document.querySelectorAll('[data-reveal]').forEach((el) => obs.observe(el))
    return () => {
      obsHeader?.disconnect()
      obs.disconnect()
    }
  }, [])

  // Guion del scroll-telling (video real: llegas → stock → cobro → app → asistente → cierre)
  const pasosScrollTelling = [
    {
      title: 'El día empieza en tu mostrador',
      text: 'La tienda abre, la gente entra y las compras van y vienen. Como siempre. La diferencia empieza cuando todo lo que pasa aquí lo sabes al momento.',
    },
    {
      title: 'Tu stock, sin inventarios interminables',
      text: 'Cada artículo con su precio y su existencia, a un vistazo desde tu celular. Sabrás qué falta antes de que se agote en la góndola.',
    },
    {
      title: 'El cobro corre a tu ritmo',
      text: 'En caja escaneas o escoges productos, confirmas la venta en segundos y sigues atendiendo a la fila que te espera.',
    },
    {
      title: 'Y el día entero cabe en tu teléfono',
      text: 'Dashboard, inventario, carrito y ventas: lo que se vendió, lo que entró y lo que hay que surtir en un solo lugar, desde tu celular.',
    },
    {
      title: 'Tus números sin cuentas de cabeza',
      text: 'Ingresos de hoy, ganancia limpia y presupuesto de reinversión, explicados en lenguaje de tienda. Decisiones claras, sin tinta roja.',
    },
    {
      title: 'Y si algo se enreda, se lo dices',
      text: '«Vendí 2 arroz» — y el Asistente POS registra la venta por voz o texto, te la confirma y la deja lista. Tu negocio, ordenado y tranquilo.',
    },
  ]

  const toggleFaq = (idx) => {
    setFaqAbierta(faqAbierta === idx ? null : idx)
  }

  const preguntasFrecuentes = [
    {
      q: '¿Qué es exactamente GIN?',
      a: 'Es una herramienta digital sencilla que te ayuda a registrar lo que entra y lo que sale, saber qué productos tienes disponibles y conocer tu ganancia real, sin cuadernos ni cuentas manuales.',
    },
    {
      q: '¿A quién está dirigido?',
      a: 'A comercios, emprendimientos y negocios familiares de cualquier área: tiendas, servicios, comida, ventas desde casa. Si necesitas llevar el registro de tu stock y tus cuentas, GIN es para ti.',
    },
    {
      q: 'Mi negocio es pequeño y gano poco, ¿esto es para mí?',
      a: 'Sí. GIN está hecho justo para eso: negocios que apenas empiezan o que son pequeños. No necesitas un equipo ni procesos complicados — solo el deseo de tener tus números ordenados.',
    },
    {
      q: '¿La información de mi negocio se ve al público en algún lado?',
      a: 'No. Tu registro es privado: solo tú y las personas que tú autorices pueden consultarlo. Nada de tu inventario ni de tus ventas se publica en ningún lugar.',
    },
    {
      q: 'Yo hoy lo llevo en un cuaderno, ¿puedo migrarlo?',
      a: 'Sí. Empieza con lo básico: agrega tus productos más vendidos con sus cantidades. No necesitas trasladar todo el cuaderno de una vez — el registro crece con tu rutina.',
    },
    {
      q: '¿Necesito conocimientos técnicos de computación?',
      a: 'No. El sistema fue diseñado desde cero para personas que nunca han utilizado un software de gestión. Los botones son claros, la tipografía es legible y los pasos se adaptan al ritmo de trabajo habitual de tu negocio.',
    },
    {
      q: '¿Puedo utilizarlo desde mi teléfono celular?',
      a: 'Sí. Puedes acceder a GIN desde cualquier navegador web en tu teléfono celular o tableta, así como desde un computador portátil o de escritorio.',
    },
    {
      q: '¿Necesito un lector de código de barras para empezar?',
      a: 'No es indispensable. Puedes buscar y registrar tus productos escribiendo su nombre. Si cuentas con un lector USB o deseas usar la cámara de tu celular, el sistema también te permite escanear códigos de barras.',
    },
    {
      q: '¿Cómo puedo comenzar a utilizarlo?',
      a: 'Solo debes pulsar en "Crear cuenta", ingresar el nombre de tu negocio y tus datos básicos. En pocos pasos podrás agregar tus primeros artículos y comenzar a registrar tus operaciones.',
    },
  ]

  return (
    <div ref={rootRef} className="min-h-screen bg-[#faf7f1] text-slate-800 font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* ─────────────────────────────────────────────────────────────
          1. NAVEGACIÓN PRINCIPAL
      ───────────────────────────────────────────────────────────── */}
      <header
        className={`fixed top-0 z-40 transition-[background-color,border-color] duration-200 ${
          scrolled
            ? 'bg-white/95 backdrop-blur-md border-b border-slate-200/80'
            : 'bg-transparent border-b border-transparent lnd-hd-float'
        }`}
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-xl shadow-sm">
              <Store size={22} />
            </div>
            <div className="min-w-0">
              <span className="lnd-hd-word font-extrabold text-slate-900 text-lg tracking-tight block leading-tight whitespace-nowrap">
                GIN
              </span>
              <span className="lnd-hd-sub text-[10px] text-emerald-700 font-medium tracking-wide block whitespace-nowrap">
                Gestión de Inventario Inteligente
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
            <a href="#problema" className="hover:text-emerald-700 transition-colors inline-block px-2 py-3 whitespace-nowrap">
              El problema
            </a>
            <a href="#proposito" className="hover:text-emerald-700 transition-colors inline-block px-2 py-3 whitespace-nowrap">
              Nuestra propuesta
            </a>
            <a href="#quienes" className="hover:text-emerald-700 transition-colors inline-block px-2 py-3 whitespace-nowrap">
              ¿A quién ayudamos?
            </a>
            <a href="#historias" className="hover:text-emerald-700 transition-colors inline-block px-2 py-3 whitespace-nowrap">
              Historias
            </a>
            <a href="#como-funciona" className="hover:text-emerald-700 transition-colors inline-block px-2 py-3 whitespace-nowrap">
              ¿Cómo funciona?
            </a>
            <a href="#faq" className="hover:text-emerald-700 transition-colors inline-block px-2 py-3 whitespace-nowrap">
              Preguntas
            </a>
          </nav>

          <div className="flex items-center gap-3 shrink-0">
            <Link
              to="/login"
              className="lnd-hd-login hidden sm:inline-block text-sm font-semibold text-slate-700 hover:text-emerald-700 px-3 py-3 rounded-xl transition-colors whitespace-nowrap"
            >
              Entrar a mi cuenta
            </Link>
            <Link
              to="/registro"
              className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold px-4 py-3 rounded-xl transition-all shadow-sm active:scale-95 flex items-center gap-1.5 whitespace-nowrap"
            >
              <span>Crear cuenta</span>
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </header>

      <main>
        {/* ─────────────────────────────────────────────────────────────
            2. HERO SECTION
        ───────────────────────────────────────────────────────────── */}
        <section
          className="relative min-h-[100svh] flex items-center overflow-hidden"
          style={{ background: 'var(--noche)' }}
        >
          {/* El spot corre solo (mudo + loop + playsInline): lo primero que ve el visitante */}
          <video
            className="absolute inset-0 h-full w-full object-cover"
            src="/media/viaje/hero.mp4"
            poster="/media/viaje/hero-poster.jpg"
            autoPlay
            muted
            loop
            playsInline
            preload="auto"
            aria-hidden="true"
          />
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              background:
                'linear-gradient(90deg, rgba(10,15,12,.94) 0%, rgba(10,15,12,.80) 42%, rgba(10,15,12,.32) 70%, rgba(10,15,12,.18) 100%)',
            }}
          />
          <div
            className="absolute inset-x-0 bottom-0 h-28 pointer-events-none"
            style={{ background: 'linear-gradient(to top, rgba(10,15,12,.88), transparent)' }}
          />

          <div className="relative w-full max-w-6xl mx-auto px-4 sm:px-6 pt-20 pb-12" data-reveal>
            <div className="max-w-2xl mx-auto lg:mx-0 space-y-6 text-center lg:text-left">
              <div
                className="inline-flex items-center gap-2 max-w-full px-3.5 py-1.5 rounded-full text-xs font-semibold"
                style={{ background: 'rgba(216,154,61,.12)', border: '1px solid rgba(216,154,61,.35)', color: 'var(--ambar)' }}
              >
                <HeartHandshake size={15} className="shrink-0" />
                <span className="leading-snug">Para comercios pequeños, emprendimientos y negocios familiares</span>
              </div>

              <h1
                className="text-3xl sm:text-5xl font-black tracking-tight leading-[1.15]"
                style={{ color: 'var(--crema)' }}
              >
                Anota tu stock y tus cuentas desde el celular, y deja de llevarlas en
                <span className="italic-rk" style={{ color: 'var(--ambar)' }}> la memoria</span>
              </h1>

              <p className="text-base sm:text-lg max-w-2xl mx-auto lg:mx-0 leading-relaxed" style={{ color: 'var(--tinta-suave)' }}>
                Tu negocio no necesita página web ni sistemas complicados. Necesita un registro confiable:
                qué tienes, qué se movió y cómo va. GIN guarda tus números y te los muestra
                desde donde estés.
              </p>

              <div className="pt-2 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3">
                <Link
                  to="/registro"
                  className="w-full sm:w-auto font-bold text-base px-7 py-3.5 rounded-2xl transition-all shadow-md hover:shadow-lg active:scale-95 flex items-center justify-center gap-2"
                  style={{ background: 'var(--ambar)', color: 'var(--noche)' }}
                >
                  <span>Empieza a anotar tu negocio hoy</span>
                  <ArrowRight size={18} />
                </Link>
                <button
                  onClick={() => setVideoModalAbierto(true)}
                  className="w-full sm:w-auto font-semibold text-base px-6 py-3.5 rounded-2xl transition-all flex items-center justify-center gap-2 border"
                  style={{ color: 'var(--crema)', borderColor: 'var(--linea)', background: 'rgba(245,239,230,.05)' }}
                >
                  <Play size={18} style={{ color: 'var(--ambar)' }} />
                  <span>Ver cómo funciona</span>
                </button>
              </div>

              <div className="pt-4 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-xs font-medium" style={{ color: 'var(--tinta-suave)' }}>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 size={16} style={{ color: 'var(--ambar)' }} />
                  Sin conocimientos técnicos y funciona en el celular
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 size={16} style={{ color: 'var(--ambar)' }} />
                  Tu registro es privado: solo tú y tu equipo lo ven
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 size={16} style={{ color: 'var(--ambar)' }} />
                  Desde cualquier parte: mira cómo va tu negocio sin estar en la tienda
                </span>
              </div>
            </div>

            </div>

          {/* Cinta inferior: contexto honesto de lo que se está viendo */}
          <div className="absolute bottom-5 inset-x-0">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 flex items-center gap-3 text-[10px] sm:text-[11px] font-mono tracking-widest uppercase" style={{ color: 'rgba(245,239,230,.72)' }}>
              <span className="inline-block h-1.5 w-1.5 rounded-full shrink-0" style={{ background: 'var(--ambar)' }} />
              <span className="whitespace-nowrap">Un negocio real, de cualquier área</span>
              <span className="h-px flex-1" style={{ background: 'rgba(245,239,230,.18)' }} />
              <span className="whitespace-nowrap hidden sm:inline">Del mostrador a tu celular</span>
            </div>
          </div>

          {/* Sentinel del header: cambia a sólido al superarse el final del hero */}
          <div ref={hdSentinelRef} className="pointer-events-none absolute bottom-0 left-0 h-px w-px opacity-0" aria-hidden="true" />
        </section>

        {/* ─────────────────────────────────────────────────────────────
            3. EL PROBLEMA COTIDIANO (STORYTELLING)
        ───────────────────────────────────────────────────────────── */}
        <section id="problema" className="py-16 md:py-20 max-w-5xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-[5fr_6fr] gap-10 lg:gap-14 items-center">
            {/* Fotografía real: la manos que cuentan el día en el mostrador */}
            <div className="relative order-2 lg:order-1" data-reveal>
              <img
                src="/media/pago-manos.jpg"
                alt="Manos intercambiando el pago en el mostrador de una tienda de barrio"
                className="w-full h-[340px] sm:h-[400px] lg:h-[480px] object-cover rounded-[2rem] shadow-[0_24px_48px_-20px_rgba(20,37,31,0.35)]"
                loading="lazy"
                decoding="async"
              />
            </div>

            {/* Bloque editorial: numeración 01/02/03, sin tarjetas */}
            <div className="order-1 lg:order-2">
              <div className="mb-8" data-reveal>
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                  La realidad cotidiana
                </span>
                <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1 leading-tight">
                  Atender el mostrador y llevar las cuentas al mismo tiempo no es tarea fácil
                </h2>
                <p className="text-sm text-slate-600 mt-3 max-w-xl">
                  En una tienda de barrio las cosas pasan muy rápido: clientes que llegan al tiempo,
                  proveedores que entregan mercancía y cuentas anotadas en hojas sueltas.
                </p>
              </div>

              <div className="space-y-0" data-reveal>
                {[
                  {
                    n: '01',
                    t: 'Cuentas en libretas y papeles',
                    d: 'Anotar cada venta o cada gasto en un cuaderno hace que al final del día sea difícil y agotador calcular cuánto dinero entró realmente a la caja.',
                  },
                  {
                    n: '02',
                    t: 'Incertidumbre en el surtido',
                    d: 'Descubrir que un producto se agotó solo cuando el cliente lo pide, o enterarse de que otra mercancía venció en la estantería sin haber alcanzado a venderla.',
                  },
                  {
                    n: '03',
                    t: 'Confusión entre venta y ganancia',
                    d: 'No todo el dinero recaudado es ganancia de bolsillo. Una parte importante corresponde a lo que costó comprar la mercancía y debe apartarse para reponer surtido.',
                  },
                ].map((p) => (
                  <div key={p.n} className="py-4 border-t" style={{ borderColor: '#e7ddcc' }}>
                    <div className="flex items-baseline gap-4">
                      <span className="font-mono text-[11px] tracking-widest shrink-0 w-6" style={{ color: 'var(--ambar)' }}>
                        {p.n}
                      </span>
                      <div className="space-y-1">
                        <h3 className="font-bold text-slate-800">{p.t}</h3>
                        <p className="text-sm text-slate-600 leading-relaxed">{p.d}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            4. NUESTRA PROPUESTA DE VALOR
        ───────────────────────────────────────────────────────────── */}
        <section id="proposito" className="py-16 md:py-20 bg-[#fffdf8] border-y border-[#ece3d4]">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="max-w-2xl mb-12">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                Nuestra propuesta
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
                Menos tiempo intentando recordar qué pasó. Más claridad para saber qué está ocurriendo.
              </h2>
              <p className="text-sm text-slate-600 mt-2">
                GIN no busca vender tecnología por sí misma. El propósito es entregarte una
                herramienta limpia y comprensible para respaldar el esfuerzo de tu trabajo diario.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="p-5 rounded-2xl bg-[#fafaf9] space-y-2">
                <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                  <Package size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Control de productos y stock</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Conoce cuántas unidades o libras tienes en bodega. El inventario se descuenta de
                  forma automática con cada venta realizada.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] space-y-2">
                <div className="w-9 h-9 rounded-lg bg-violet-100 text-violet-700 flex items-center justify-center font-bold">
                  <Scale size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Venta por peso y granel</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Admite productos por unidad o fraccionados por gramos, libras y kilos, calculando
                  el precio exacto sin errores manuales.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] space-y-2">
                <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
                  <TrendingUp size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Ganancia real del negocio</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  El sistema descuenta lo que te costó comprar la mercancía y te muestra tu ganancia
                  limpia, separando el capital de reposición.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] space-y-2">
                <div className="w-9 h-9 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center font-bold">
                  ⚠️
                </div>
                <h3 className="font-bold text-slate-800 text-base">Alertas de vencimiento</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Aviso visual para productos próximos a vencer en los siguientes 15 días,
                  ayudándote a rotarlos a tiempo antes de que se pierdan.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] space-y-2">
                <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                  <Users size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Anota entre varios</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Un familiar o socio puede registrar movimientos contigo, sin acceso a tus
                  reportes privados ni a tus precios de costo.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] space-y-2">
                <div className="w-9 h-9 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center font-bold">
                  📄
                </div>
                <h3 className="font-bold text-slate-800 text-base">Historial y exportación</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Revisa las ventas de hoy o de la semana en orden cronológico, con la opción de
                  descargar tu historial a Excel cuando lo requieras.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            5. ¿A QUIÉNES AYUDAMOS?
        ───────────────────────────────────────────────────────────── */}
        <section id="quienes" className="py-16 md:py-20 max-w-5xl mx-auto px-4 sm:px-6">
          <div className="max-w-2xl mb-10">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              ¿A quiénes ayudamos?
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1 leading-tight">
              Pensado para cualquier negocio que solo quiere tener sus cuentas en orden
            </h2>
            <p className="text-sm text-slate-600 mt-2">
              Tiendas, servicios, comida, papelerías, ferreterías, talleres, ventas desde casa:
              da igual el área. Si tu negocio necesita anotar qué tienes, qué se movió y cómo va,
              GIN está hecho para ti.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-[6fr_5fr] gap-10 lg:gap-14 items-center">
            {/* Fotografía real: la gente que este sistema sirve */}
            <div data-reveal>
              <img
                src="/media/tienda-cliente.jpg"
                alt="Persona atendiendo a un cliente detrás del mostrador de su comercio"
                className="w-full h-[340px] sm:h-[420px] object-cover rounded-[2rem] shadow-[0_24px_48px_-20px_rgba(20,37,31,0.35)]"
                loading="lazy"
                decoding="async"
              />
            </div>

            <div data-reveal>
              <p className="text-sm text-slate-600 leading-relaxed">
                No necesitas instalación, ni página web, ni conocimientos técnicos. Solo el deseo
                de tener tus números ordenados, desde el celular y sin exponer nada al público.
              </p>
              <div className="flex flex-wrap gap-2 mt-5">
                {['Tiendas', 'Servicios', 'Comida', 'Papelerías', 'Ferreterías', 'Talleres', 'Ventas desde casa'].map((chip) => (
                  <span
                    key={chip}
                    className="px-3 py-1.5 rounded-full text-xs font-semibold bg-[#fafaf9] border border-[#e7ddcc] text-slate-700"
                  >
                    {chip}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            6. HISTORIAS REALES (DOCUMENTAL: ANTES -> DURANTE -> DESPUÉS)
        ───────────────────────────────────────────────────────────── */}
        <section id="historias" className="py-16 md:py-20 bg-[#fffdf8] border-y border-[#ece3d4]">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="max-w-2xl mb-10">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                Historias que nos inspiran
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
                La experiencia de quienes atienden su propio negocio
              </h2>
              <p className="text-sm text-slate-600 mt-2">
                Creemos en el valor de los testimonios documentales y respetuosos. Esta sección está
                reservada para compartir vivencias reales de comerciantes de cualquier área mediante la
                estructura de su experiencia: cómo gestionaban antes, cómo fue su proceso y qué
                cambió en su tranquilidad.
              </p>
            </div>

            {/* Mientras se documentan las historias reales: panel honesto (sin placeholders) */}
            <div className="rounded-2xl p-8 md:p-10 border border-dashed border-slate-300 bg-[#fafaf9] relative" data-reveal>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold">
                <span>Historias reales en documentación</span>
              </span>
              <p className="text-sm text-slate-600 mt-4 max-w-xl leading-relaxed">
                No vamos a inventar testimonios. Estamos entrevistando a las primeras tiendas que
                trabajan con GIN para documentar, con su permiso, cómo llevaban sus
                cuentas antes y qué cambió después. Cuando estén listas, las verás aquí.
              </p>
              <a
                href="https://chat.whatsapp.com/gestion-inventario-inteligente"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-5 inline-flex items-center gap-2 text-sm font-bold text-emerald-700 hover:text-emerald-800 transition-colors"
              >
                ¿Tienes una tienda y quieres contar tu historia? Escríbenos aquí
                <ArrowRight size={16} />
              </a>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            7. ALFABETIZACIÓN DIGITAL
        ───────────────────────────────────────────────────────────── */}
        <section className="py-16 md:py-20 max-w-5xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
            <div className="space-y-4">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                Acompañamiento
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
                Tecnología que se adapta a las personas, no al revés
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed">
                Entendemos que dar el paso de la libreta a una herramienta digital puede generar
                inquietud o temor a equivocarse. Por eso, GIN no es un software empresarial
                pesado; es un puente sencillo para familiarizarse con la gestión digital.
              </p>

              <div className="space-y-3 pt-2 text-sm text-slate-700">
                <div className="flex items-start gap-3">
                  <CheckCircle2 size={18} className="text-emerald-600 shrink-0 mt-0.5" />
                  <span>
                    <strong>Botones claros y tipografía grande:</strong> Diseñado para verse bien en
                    pantallas de teléfonos sencillos.
                  </span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 size={18} className="text-emerald-600 shrink-0 mt-0.5" />
                  <span>
                    <strong>Aprende a tu propio ritmo:</strong> El sistema incluye guías sencillas y
                    ayuda en cada pantalla para resolver dudas puntuales.
                  </span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 size={18} className="text-emerald-600 shrink-0 mt-0.5" />
                  <span>
                    <strong>Sin términos enredados:</strong> Hablamos de productos, ventas, precios y
                    ganancias en el lenguaje que tú utilizas.
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white p-7 rounded-3xl border border-slate-200 shadow-sm space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                <BookOpen size={24} />
              </div>
              <h3 className="font-bold text-slate-800 text-lg">¿Cómo entendemos la alfabetización digital?</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Para nosotros no significa hacer cursos teóricos complejos. Significa que un dueño
                de negocio pueda registrar una venta en 10 segundos, mirar su celular al cerrar y saber con
                certeza cuánto vendió hoy. La confianza se gana usando herramientas que no complican
                la vida.
              </p>
              <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-900 font-medium">
                "La mejor tecnología para un pequeño comercio es la que se entiende sin esfuerzo."
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            8. ECONOMÍA POPULAR Y COMERCIO LOCAL
        ───────────────────────────────────────────────────────────── */}
        <section
          className="relative py-16 md:py-24 overflow-hidden"
          style={{ background: 'var(--noche)' }}
        >
          {/* Fondo real ESTÁTICO: solo el hero lleva ken-burns (auditoría §3D) */}
          <img
            src="/media/mercado-noche.jpg"
            alt=""
            aria-hidden="true"
            className="absolute inset-0 h-full w-full object-cover opacity-45"
            loading="lazy"
          />
          <div
            className="absolute inset-0"
            style={{ background: 'linear-gradient(180deg, rgba(16,22,19,.75) 0%, rgba(16,22,19,.92) 60%, rgba(16,22,19,.98) 100%)' }}
          />

          <div className="relative max-w-5xl mx-auto px-4 sm:px-6 space-y-8">
            <div className="max-w-2xl" data-reveal>
              <span className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--ambar)' }}>
                  Economía popular
                </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1">
                El corazón productivo de nuestras comunidades
              </h2>
              <p className="text-sm text-slate-300 mt-2 leading-relaxed">
                Las tiendas de barrio y los micromercados son mucho más que puntos de venta: son
                espacios de encuentro, confianza entre vecinos y sustento digno para miles de familias.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
              <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--ambar)' }}>
                  Por qué nos importa
                </span>
                <h3 className="font-bold text-white text-base">Cercanía y dignidad</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  El comercio popular resuelve el día a día de las familias. Apoyar su labor con
                  herramientas claras es reconocer el valor que aportan al tejido social de cada barrio.
                </p>
              </div>

              <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--ambar)' }}>
                  Acceso equitativo
                </span>
                <h3 className="font-bold text-white text-base">Tecnología sin barreras</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Creemos que el acceso a herramientas de gestión digital no debe ser exclusivo de
                  grandes cadenas con presupuestos altos de sistemas.
                </p>
              </div>

              <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider" style={{ color: 'var(--ambar)' }}>
                  Nuestro papel
                </span>
                <h3 className="font-bold text-white text-base">Un puente sencillo</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  GIN busca acompañar de forma práctica a los negocios pequeños de cualquier área,
                  ofreciendo orden en sus números para que tomen mejores decisiones para su negocio.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            9. ¿CÓMO FUNCIONA? (PASOS VERIFICADOS)
        ───────────────────────────────────────────────────────────── */}
        <section id="como-funciona" className="py-16 md:py-20 max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              Paso a paso
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
              ¿Cómo funciona GIN en tu negocio?
            </h2>
            <p className="text-sm text-slate-600 mt-2">
              Un flujo de trabajo transparente y directo, sin pasos ocultos ni configuraciones
              enredadas.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {pasosScrollTelling.map((s, i) => (
              <article key={s.title} className="rounded-2xl overflow-hidden border border-[#ece3d4] bg-white shadow-sm" data-reveal>
                <img
                  src={`/media/viaje/v${String([10, 36, 54, 76, 98, 114][i]).padStart(3, '0')}.webp`}
                  alt={`Paso ${i + 1}: ${s.title}`}
                  loading="lazy"
                  decoding="async"
                  className="w-full h-36 object-cover"
                />
                <div className="p-5">
                  <span className="text-[10px] font-mono font-bold tracking-widest text-emerald-700">
                    {String(i + 1).padStart(2, '0')} / 06
                  </span>
                  <h3 className="text-base font-bold text-slate-900 mt-1">{s.title}</h3>
                  <p className="text-sm text-slate-600 mt-1.5 leading-relaxed">{s.text}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            10. VIDEO TUTORIAL GUIADO (CON CARGA DIFERIDA)
        ───────────────────────────────────────────────────────────── */}
        <section className="py-16 md:py-20 bg-[#fffdf8] border-y border-[#ece3d4]">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center space-y-6">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              Aprende en video
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Conoce visualmente cómo funciona la aplicación
            </h2>
            <p className="text-sm text-slate-600 max-w-xl mx-auto">
              Una demostración guiada de 60 a 90 segundos que muestra la interfaz real de la
              tienda: cómo se agrega un producto, cómo se cobra y cómo se consultan las ganancias.
            </p>

            {/* Poster / Gatillo del Video */}
            <div className="relative max-w-2xl mx-auto rounded-3xl overflow-hidden border border-slate-200 shadow-lg bg-slate-900 aspect-video flex flex-col items-center justify-center group cursor-pointer">
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/20" />
              <div className="relative z-10 text-center space-y-3 px-4">
                <button
                  type="button"
                  onClick={() => setVideoModalAbierto(true)}
                  className="w-16 h-16 rounded-full bg-emerald-600 text-white flex items-center justify-center mx-auto shadow-xl group-hover:scale-110 transition-transform"
                  aria-label="Reproducir video demostrativo"
                >
                  <Play size={28} className="fill-white translate-x-0.5" />
                </button>
                <p className="text-white font-bold text-base">Aprende a usar GIN</p>
                <span className="text-xs text-slate-300 block">
                  Duración aproximada: 1 minuto · Carga bajo demanda
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            11. COMUNIDAD Y REDES SOCIALES
        ───────────────────────────────────────────────────────────── */}
        <section id="comunidad" className="py-16 md:py-20 max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-8">
          <div className="max-w-xl mx-auto space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              Canales Oficiales & Redes
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Gestión de Inventario Inteligente en Redes
            </h2>
            <p className="text-sm text-slate-600">
              Síguenos para aprender trucos de mostrador, conocer experiencias de otros negocios y participar en capacitaciones gratuitas.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-left">
            {/* Instagram */}
            <a
              href="https://www.instagram.com/gestion.inventario.inteligente"
              target="_blank"
              rel="noopener noreferrer"
              className="group p-4 rounded-2xl bg-white border border-slate-200 hover:border-pink-300 hover:shadow-md transition-all flex items-start gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 group-hover:text-pink-600 transition-colors">
                    Instagram
                  </span>
                  <span className="text-[10px] text-slate-400 group-hover:translate-x-0.5 transition-transform">↗</span>
                </div>
                <p className="text-xs font-medium text-slate-700 truncate">@gestion.inventario.inteligente</p>
                <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">Tips diarios de mostrador y fotos de comercios</p>
              </div>
            </a>

            {/* Facebook */}
            <a
              href="https://www.facebook.com/gestion.inventario.inteligente"
              target="_blank"
              rel="noopener noreferrer"
              className="group p-4 rounded-2xl bg-white border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all flex items-start gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
                    Facebook
                  </span>
                  <span className="text-[10px] text-slate-400 group-hover:translate-x-0.5 transition-transform">↗</span>
                </div>
                <p className="text-xs font-medium text-slate-700 truncate">Gestión de Inventario Inteligente</p>
                <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">Comunidad de negocios y emprendimientos</p>
              </div>
            </a>

            {/* TikTok */}
            <a
              href="https://www.tiktok.com/@gestioninventarioint"
              target="_blank"
              rel="noopener noreferrer"
              className="group p-4 rounded-2xl bg-white border border-slate-200 hover:border-slate-400 hover:shadow-md transition-all flex items-start gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-xs">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.24 1.07-.14 1.61.24 1.64 1.82 2.89 3.5 2.78 1.15-.02 2.22-.61 2.82-1.59.39-.61.59-1.34.61-2.07.02-3.95.01-7.9.01-11.85z"/>
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 group-hover:text-slate-900 transition-colors">
                    TikTok
                  </span>
                  <span className="text-[10px] text-slate-400 group-hover:translate-x-0.5 transition-transform">↗</span>
                </div>
                <p className="text-xs font-medium text-slate-700 truncate">@gestioninventarioint</p>
                <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">Videos cortos de 30s con trucos prácticos</p>
              </div>
            </a>

            {/* YouTube */}
            <a
              href="https://www.youtube.com/@GestionInventarioInteligente"
              target="_blank"
              rel="noopener noreferrer"
              className="group p-4 rounded-2xl bg-white border border-slate-200 hover:border-red-300 hover:shadow-md transition-all flex items-start gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-red-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 group-hover:text-red-600 transition-colors">
                    YouTube
                  </span>
                  <span className="text-[10px] text-slate-400 group-hover:translate-x-0.5 transition-transform">↗</span>
                </div>
                <p className="text-xs font-medium text-slate-700 truncate">Gestión de Inventario Inteligente</p>
                <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">Tutoriales guiados y cursos paso a paso</p>
              </div>
            </a>

            {/* Comunidad WhatsApp */}
            <a
              href="https://chat.whatsapp.com/gestion-inventario-inteligente"
              target="_blank"
              rel="noopener noreferrer"
              className="group sm:col-span-2 lg:col-span-2 p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 hover:border-emerald-400 hover:shadow-md transition-all flex items-start gap-3.5"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-xs">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-emerald-900 group-hover:text-emerald-700 transition-colors">
                    Comunidad WhatsApp: Comerciantes GIN
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                    Comunidad Oficial
                  </span>
                </div>
                <p className="text-xs font-semibold text-emerald-800 mt-0.5">Gestión de Inventario Inteligente</p>
                <p className="text-[11px] text-emerald-700 mt-0.5">
                  Grupo abierto para resolver dudas, compartir consejos de abastecimiento y conectar con otros comerciantes.
                </p>
              </div>
            </a>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            12. PREGUNTAS FRECUENTES (FAQ REALISTA)
        ───────────────────────────────────────────────────────────── */}
        <section id="faq" className="py-16 md:py-20 bg-[#fffdf8] border-y border-[#ece3d4]">
          <div className="max-w-3xl mx-auto px-4 sm:px-6 space-y-8">
            <div className="text-center space-y-2">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                Respuestas claras
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
                Preguntas frecuentes
              </h2>
              <p className="text-sm text-slate-600">
                Información transparente sobre el uso de la aplicación en tu negocio.
              </p>
            </div>

            <div className="space-y-3">
              {preguntasFrecuentes.map((item, idx) => (
                <div
                  key={idx}
                  className="rounded-2xl border border-slate-200 bg-[#fafaf9] overflow-hidden transition-colors"
                >
                  <button
                    type="button"
                    aria-expanded={faqAbierta === idx}
                    onClick={() => toggleFaq(idx)}
                    className="w-full text-left p-5 font-semibold text-slate-800 text-sm sm:text-base flex items-center justify-between gap-4"
                  >
                    <span>{item.q}</span>
                    <ChevronDown
                      size={18}
                      className={`text-slate-400 transition-transform ${
                        faqAbierta === idx ? 'rotate-180 text-emerald-600' : ''
                      }`}
                    />
                  </button>
                  {faqAbierta === idx && (
                    <div className="px-5 pb-5 text-xs sm:text-sm text-slate-600 leading-relaxed border-t border-slate-200/60 pt-3">
                      {item.a}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            13. LLAMADO A LA ACCIÓN (CTA FINAL)
        ───────────────────────────────────────────────────────────── */}
        <section className="py-16 md:py-24 max-w-4xl mx-auto px-4 sm:px-6 text-center space-y-6">
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Empieza a anotar tu negocio hoy
          </h2>
          <p className="text-base text-slate-600 max-w-xl mx-auto leading-relaxed">
            Un registro confiable: qué tienes, qué se movió y cómo va. GIN guarda tus números
            y te los muestra desde donde estés.
          </p>
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/registro"
              className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base px-8 py-4 rounded-2xl transition-all shadow-md active:scale-98 flex items-center justify-center gap-2"
            >
              <span>Empieza a anotar tu negocio hoy</span>
              <ArrowRight size={18} />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 font-semibold text-base px-7 py-4 rounded-2xl transition-all"
            >
              Ya tengo una cuenta registrada
            </Link>
          </div>
        </section>
      </main>

      {/* ─────────────────────────────────────────────────────────────
          14. FOOTER INSTITUCIONAL
      ───────────────────────────────────────────────────────────── */}
      <footer className="border-t border-[#ece3d4] bg-[#fffdf8] py-12 text-slate-500 text-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold">
              <Store size={18} />
            </div>
            <div>
              <span className="font-bold text-slate-800 text-sm block">GIN</span>
              <span>Herramienta digital para pequeños comercios</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-5 text-slate-600 font-medium">
            <a href="#problema" className="hover:text-emerald-700">El problema</a>
            <a href="#proposito" className="hover:text-emerald-700">Nuestra propuesta</a>
            <a href="#como-funciona" className="hover:text-emerald-700">Cómo funciona</a>
            <a href="#comunidad" className="hover:text-emerald-700">Redes sociales</a>
            <a href="#faq" className="hover:text-emerald-700">Preguntas</a>
            <Link to="/login" className="hover:text-emerald-700 font-semibold text-emerald-800">Entrar a mi cuenta</Link>
          </div>

          <div className="text-center sm:text-right text-[11px] text-slate-400">
            <span>Disponible desde tu celular, desde donde estés</span>
            <span className="block mt-0.5">Gestión de Inventario Inteligente</span>
            <span className="block text-[10px] text-slate-400">Tecnología que se adapta a las personas</span>
          </div>
        </div>
      </footer>

      {/* ─────────────────────────────────────────────────────────────
          MODAL DE VIDEO TUTORIAL (CARGA DIFERIDA)
      ───────────────────────────────────────────────────────────── */}
      {videoModalAbierto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-3xl w-full p-4 sm:p-6 relative shadow-2xl space-y-4">
            <div className="flex items-center justify-between text-white pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Play size={18} className="text-emerald-500" />
                <h3 className="font-bold text-sm sm:text-base">Demostración: ¿Cómo funciona GIN?</h3>
              </div>
              <button
                type="button"
                onClick={() => setVideoModalAbierto(false)}
                className="text-slate-400 hover:text-white p-1"
                aria-label="Cerrar video"
              >
                <X size={20} />
              </button>
            </div>

            <div className="rounded-2xl overflow-hidden bg-black aspect-video flex items-center justify-center">
              <video
                controls
                autoPlay
                className="w-full h-full object-contain"
                poster=""
              >
                <source src="/Grabación de pantalla 2026-06-03 115051.mp4" type="video/mp4" />
                Tu navegador no soporta la reproducción de video HTML5.
              </video>
            </div>

            <p className="text-xs text-slate-400 text-center">
              Demostración de las funciones reales de inventario, venta en mostrador y consulta de ganancias.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
