import { useState } from 'react'
import { Link } from 'react-router-dom'
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

  const toggleFaq = (idx) => {
    setFaqAbierta(faqAbierta === idx ? null : idx)
  }

  const preguntasFrecuentes = [
    {
      q: '¿Qué es exactamente Gestión Neiva?',
      a: 'Es una herramienta digital sencilla pensada para pequeños comerciantes, tenderos y negocios familiares. Te ayuda a registrar tus ventas diarias, saber qué productos tienes disponibles en tus estanterías y conocer tu ganancia real sin necesidad de llevar cuadernos ni hacer cuentas manuales.',
    },
    {
      q: '¿A quién está dirigido?',
      a: 'Principalmente a tenderos de barrio, micromercados, panaderías, cafeterías y pequeños establecimientos comerciales de Neiva y la región que buscan trabajar con mayor orden y tranquilidad en su día a día.',
    },
    {
      q: '¿Necesito conocimientos técnicos de computación?',
      a: 'No. El sistema fue diseñado desde cero para personas que nunca han utilizado un software de gestión. Los botones son claros, la tipografía es legible y los pasos se adaptan al ritmo de trabajo habitual del mostrador.',
    },
    {
      q: '¿Puedo utilizarlo desde mi teléfono celular?',
      a: 'Sí. Puedes acceder a Gestión Neiva desde cualquier navegador web en tu teléfono celular o tableta, así como desde un computador portátil o de escritorio.',
    },
    {
      q: '¿Cómo se protege la información de mi tienda?',
      a: 'Tu información pertenece exclusivamente a tu negocio y permanece estrictamente separada de la de otras tiendas. Nadie fuera de los usuarios autorizados por ti puede consultar tus ventas ni tu inventario.',
    },
    {
      q: '¿Necesito un lector de código de barras para empezar?',
      a: 'No es indispensable. Puedes buscar y registrar tus productos escribiendo su nombre. Si cuentas con un lector USB o deseas usar la cámara de tu celular, el sistema también te permite escanear códigos de barras.',
    },
    {
      q: '¿Cómo puedo comenzar a utilizarlo?',
      a: 'Solo debes pulsar en "Crear cuenta", ingresar el nombre de tu tienda y tus datos básicos. En pocos pasos podrás agregar tus primeros artículos y comenzar a registrar tus operaciones.',
    },
  ]

  return (
    <div className="min-h-screen bg-[#fafaf9] text-slate-800 font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* ─────────────────────────────────────────────────────────────
          1. NAVEGACIÓN PRINCIPAL
      ───────────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 transition-all">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-xl shadow-sm">
              <Store size={22} />
            </div>
            <div>
              <span className="font-extrabold text-slate-900 text-lg tracking-tight block leading-tight">
                Gestión Neiva
              </span>
              <span className="text-[11px] text-emerald-700 font-medium tracking-wide block">
                Comercio local y popular
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
            <a href="#problema" className="hover:text-emerald-700 transition-colors">
              El problema
            </a>
            <a href="#proposito" className="hover:text-emerald-700 transition-colors">
              Nuestra propuesta
            </a>
            <a href="#quienes" className="hover:text-emerald-700 transition-colors">
              ¿A quién ayudamos?
            </a>
            <a href="#historias" className="hover:text-emerald-700 transition-colors">
              Historias
            </a>
            <a href="#como-funciona" className="hover:text-emerald-700 transition-colors">
              ¿Cómo funciona?
            </a>
            <a href="#faq" className="hover:text-emerald-700 transition-colors">
              Preguntas
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="text-sm font-semibold text-slate-700 hover:text-emerald-700 px-3 py-2 rounded-xl transition-colors"
            >
              Entrar a mi Tienda
            </Link>
            <Link
              to="/registro"
              className="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold px-4 py-2.5 rounded-xl transition-all shadow-sm active:scale-95 flex items-center gap-1.5"
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
        <section className="relative pt-12 pb-16 md:pt-20 md:pb-24 overflow-hidden border-b border-slate-200/60 bg-gradient-to-b from-emerald-50/40 via-[#fafaf9] to-[#fafaf9]">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-100/80 border border-emerald-200 text-emerald-800 text-xs font-semibold">
              <HeartHandshake size={15} />
              <span>Para tenderos, micromercados y negocios familiares</span>
            </div>

            <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-[1.15]">
              Ayudamos a los pequeños comerciantes a entender y controlar su negocio con tranquilidad
            </h1>

            <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
              Un comerciante no debería tener que depender de la memoria, revisar varios cuadernos o
              hacer cuentas una y otra vez para saber cómo va su día. Gestión Neiva hace que
              administrar tu tienda sea más claro, ordenado y cercano.
            </p>

            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/registro"
                className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base px-7 py-3.5 rounded-2xl transition-all shadow-md active:scale-98 flex items-center justify-center gap-2"
              >
                <span>Crea tu cuenta y comienza</span>
                <ArrowRight size={18} />
              </Link>
              <button
                onClick={() => setVideoModalAbierto(true)}
                className="w-full sm:w-auto bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 font-semibold text-base px-6 py-3.5 rounded-2xl transition-all flex items-center justify-center gap-2"
              >
                <Play size={18} className="text-emerald-600 fill-emerald-600" />
                <span>Ver cómo funciona</span>
              </button>
            </div>

            <div className="pt-6 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500 font-medium">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={16} className="text-emerald-600" />
                Sin necesidad de conocimientos técnicos
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={16} className="text-emerald-600" />
                Venta por unidades o por peso (libras/kilos)
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={16} className="text-emerald-600" />
                Diseñado para el comercio popular de Neiva
              </span>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            3. EL PROBLEMA COTIDIANO (STORYTELLING)
        ───────────────────────────────────────────────────────────── */}
        <section id="problema" className="py-16 md:py-20 max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              La realidad cotidiana
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
              Atender el mostrador y llevar las cuentas al mismo tiempo no es tarea fácil
            </h2>
            <p className="text-sm text-slate-600 mt-2">
              En una tienda de barrio las cosas pasan muy rápido: clientes que llegan al tiempo,
              proveedores que entregan mercancía y cuentas anotadas en hojas sueltas.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center text-xl font-bold">
                📝
              </div>
              <h3 className="font-bold text-slate-800 text-lg">Cuentas en libretas y papeles</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Anotar cada venta o cada gasto en un cuaderno hace que al final del día sea difícil y
                agotador calcular cuánto dinero entró realmente a la caja.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-700 flex items-center justify-center text-xl font-bold">
                📦
              </div>
              <h3 className="font-bold text-slate-800 text-lg">Incertidumbre en el surtido</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Descubrir que un producto se agotó solo cuando el cliente lo pide, o enterarse de que
                otra mercancía venció en la estantería sin haber alcanzado a venderla.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center text-xl font-bold">
                🪙
              </div>
              <h3 className="font-bold text-slate-800 text-lg">Confusión entre venta y ganancia</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                No todo el dinero recaudado es ganancia de bolsillo. Una parte importante corresponde
                a lo que costó comprar la mercancía y debe apartarse para reponer surtido.
              </p>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            4. NUESTRA PROPUESTA DE VALOR
        ───────────────────────────────────────────────────────────── */}
        <section id="proposito" className="py-16 md:py-20 bg-white border-y border-slate-200">
          <div className="max-w-5xl mx-auto px-4 sm:px-6">
            <div className="max-w-2xl mb-12">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                Nuestra propuesta
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
                Menos tiempo intentando recordar qué pasó. Más claridad para saber qué está ocurriendo.
              </h2>
              <p className="text-sm text-slate-600 mt-2">
                Gestión Neiva no busca vender tecnología por sí misma. El propósito es entregarte una
                herramienta limpia y comprensible para respaldar el esfuerzo de tu trabajo diario.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="p-5 rounded-2xl bg-[#fafaf9] border border-slate-200 space-y-2">
                <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
                  <Package size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Control de productos y stock</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Conoce cuántas unidades o libras tienes en bodega. El inventario se descuenta de
                  forma automática con cada venta realizada.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] border border-slate-200 space-y-2">
                <div className="w-9 h-9 rounded-lg bg-violet-100 text-violet-700 flex items-center justify-center font-bold">
                  <Scale size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Venta por peso y granel</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Admite productos por unidad o fraccionados por gramos, libras y kilos, calculando
                  el precio exacto sin errores manuales.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] border border-slate-200 space-y-2">
                <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center font-bold">
                  <TrendingUp size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Ganancia real del negocio</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  El sistema descuenta lo que te costó comprar la mercancía y te muestra tu ganancia
                  limpia, separando el capital de reposición.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] border border-slate-200 space-y-2">
                <div className="w-9 h-9 rounded-lg bg-rose-100 text-rose-700 flex items-center justify-center font-bold">
                  ⚠️
                </div>
                <h3 className="font-bold text-slate-800 text-base">Alertas de vencimiento</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Aviso visual para productos próximos a vencer en los siguientes 15 días,
                  ayudándote a rotarlos a tiempo antes de que se pierdan.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] border border-slate-200 space-y-2">
                <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                  <Users size={18} />
                </div>
                <h3 className="font-bold text-slate-800 text-base">Acceso para tus colaboradores</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Permite que tus cajeros o familiares registren ventas en mostrador sin que tengan
                  acceso a tus precios de costo ni reportes privados.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#fafaf9] border border-slate-200 space-y-2">
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
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              Cercanía y contexto
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">
              Pensado para los negocios que dan vida a nuestras calles y barrios
            </h2>
            <p className="text-sm text-slate-600 mt-2">
              Hablamos de personas y familias que atienden con dedicación a sus vecinos, no de
              grandes corporaciones ni de estructuras complejas.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 text-center space-y-2">
              <span className="text-3xl block">🏪</span>
              <h3 className="font-bold text-slate-800 text-base">Tiendas de barrio</h3>
              <p className="text-xs text-slate-500">
                Puntos de abastecimiento cotidiano con productos secos, granos, aseo y bebidas.
              </p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 text-center space-y-2">
              <span className="text-3xl block">🛒</span>
              <h3 className="font-bold text-slate-800 text-base">Micromercados</h3>
              <p className="text-xs text-slate-500">
                Negocios con mayor variedad de estanterías que requieren rapidez en mostrador.
              </p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 text-center space-y-2">
              <span className="text-3xl block">🥖</span>
              <h3 className="font-bold text-slate-800 text-base">Panaderías y cafeterías</h3>
              <p className="text-xs text-slate-500">
                Venta ágil de productos frescos del día con cobro rápido en mostrador.
              </p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 text-center space-y-2">
              <span className="text-3xl block">👨‍👩‍👧‍👦</span>
              <h3 className="font-bold text-slate-800 text-base">Negocios familiares</h3>
              <p className="text-xs text-slate-500">
                Comercios atendidos en equipo donde varios integrantes colaboran en la atención.
              </p>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            6. HISTORIAS REALES (DOCUMENTAL: ANTES -> DURANTE -> DESPUÉS)
        ───────────────────────────────────────────────────────────── */}
        <section id="historias" className="py-16 md:py-20 bg-white border-y border-slate-200">
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
                reservada para compartir vivencias reales de comerciantes en Neiva mediante la
                estructura de su experiencia: cómo gestionaban antes, cómo fue su proceso y qué
                cambió en su tranquilidad.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Tarjeta de caso pendiente 1 */}
              <div className="bg-[#fafaf9] rounded-2xl p-6 border border-dashed border-slate-300 relative space-y-4">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold">
                  <span>[HISTORIA REAL PENDIENTE]</span>
                </div>

                <div className="space-y-3 pt-2">
                  <div className="border-l-2 border-amber-400 pl-3">
                    <span className="text-[11px] font-bold uppercase text-amber-700 tracking-wider block">
                      Antes
                    </span>
                    <p className="text-xs text-slate-600 mt-0.5 italic">
                      "Situación inicial del comerciante antes de incorporar una herramienta digital
                      en el negocio..."
                    </p>
                  </div>

                  <div className="border-l-2 border-blue-400 pl-3">
                    <span className="text-[11px] font-bold uppercase text-blue-700 tracking-wider block">
                      Durante
                    </span>
                    <p className="text-xs text-slate-600 mt-0.5 italic">
                      "Cómo fue su proceso de aprendizaje y cómo incorporó el registro diario en su
                      mostrador..."
                    </p>
                  </div>

                  <div className="border-l-2 border-emerald-500 pl-3">
                    <span className="text-[11px] font-bold uppercase text-emerald-700 tracking-wider block">
                      Después
                    </span>
                    <p className="text-xs text-slate-600 mt-0.5 italic">
                      "Qué cambios percibió en el control de sus productos y en el orden de sus
                      ganancias..."
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-200 text-xs text-slate-400 flex items-center justify-between">
                  <span>Comercio local en Neiva</span>
                  <span>Documentación en proceso</span>
                </div>
              </div>

              {/* Tarjeta de caso pendiente 2 */}
              <div className="bg-[#fafaf9] rounded-2xl p-6 border border-dashed border-slate-300 relative space-y-4">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-200 text-slate-700 text-xs font-semibold">
                  <span>[HISTORIA REAL PENDIENTE]</span>
                </div>

                <div className="space-y-3 pt-2">
                  <div className="border-l-2 border-amber-400 pl-3">
                    <span className="text-[11px] font-bold uppercase text-amber-700 tracking-wider block">
                      Antes
                    </span>
                    <p className="text-xs text-slate-600 mt-0.5 italic">
                      "Dificultades frecuentes con las cuentas de surtido y la rotación de mercancía
                      a granel..."
                    </p>
                  </div>

                  <div className="border-l-2 border-blue-400 pl-3">
                    <span className="text-[11px] font-bold uppercase text-blue-700 tracking-wider block">
                      Durante
                    </span>
                    <p className="text-xs text-slate-600 mt-0.5 italic">
                      "Familiarización progresiva de la familia con el punto de venta en el celular..."
                    </p>
                  </div>

                  <div className="border-l-2 border-emerald-500 pl-3">
                    <span className="text-[11px] font-bold uppercase text-emerald-700 tracking-wider block">
                      Después
                    </span>
                    <p className="text-xs text-slate-600 mt-0.5 italic">
                      "Claridad al final de cada semana para saber cuánto reponer a los distribuidores..."
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-200 text-xs text-slate-400 flex items-center justify-between">
                  <span>Negocio familiar en Neiva</span>
                  <span>Documentación en proceso</span>
                </div>
              </div>
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
                inquietud o temor a equivocarse. Por eso, Gestión Neiva no es un software empresarial
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
                Para nosotros no significa hacer cursos teóricos complejos. Significa que un tendero
                pueda registrar una venta en 10 segundos, mirar su celular al cerrar y saber con
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
        <section className="py-16 md:py-20 bg-slate-900 text-slate-100">
          <div className="max-w-5xl mx-auto px-4 sm:px-6 space-y-8">
            <div className="max-w-2xl">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                Economía popular
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-white mt-1">
                El corazón productivo de nuestras comunidades
              </h2>
              <p className="text-sm text-slate-300 mt-2 leading-relaxed">
                Las tiendas de barrio y los micromercados son mucho más que puntos de venta: son
                espacios de encuentro, confianza entre vecinos y sustento digno para miles de familias
                en Neiva.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
              <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  Por qué nos importa
                </span>
                <h3 className="font-bold text-white text-base">Cercanía y dignidad</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  El comercio popular resuelve el día a día de las familias. Apoyar su labor con
                  herramientas claras es reconocer el valor que aportan al tejido social de la ciudad.
                </p>
              </div>

              <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  Acceso equitativo
                </span>
                <h3 className="font-bold text-white text-base">Tecnología sin barreras</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Creemos que el acceso a herramientas de gestión digital no debe ser exclusivo de
                  grandes cadenas con presupuestos altos de sistemas.
                </p>
              </div>

              <div className="bg-slate-800/80 p-6 rounded-2xl border border-slate-700 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  Nuestro papel
                </span>
                <h3 className="font-bold text-white text-base">Un puente sencillo</h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Gestión Neiva busca acompañar de forma práctica a los comerciantes locales,
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
              ¿Cómo funciona Gestión Neiva en tu negocio?
            </h2>
            <p className="text-sm text-slate-600 mt-2">
              Un flujo de trabajo transparente y directo, sin pasos ocultos ni configuraciones
              enredadas.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
              <span className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold text-sm flex items-center justify-center">
                1
              </span>
              <h3 className="font-bold text-slate-800 text-base">Crea tu cuenta</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Ingresa el nombre de tu tienda y tus datos básicos para comenzar a configurar tu
                espacio.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
              <span className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold text-sm flex items-center justify-center">
                2
              </span>
              <h3 className="font-bold text-slate-800 text-base">Agrega tus productos</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Escribe el nombre de tus artículos, su precio de compra, precio de venta y cantidad
                disponible.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
              <span className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold text-sm flex items-center justify-center">
                3
              </span>
              <h3 className="font-bold text-slate-800 text-base">Registra tus ventas</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                En el mostrador, selecciona los productos o pésalos si son a granel y confirma la
                venta en segundos.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
              <span className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 font-bold text-sm flex items-center justify-center">
                4
              </span>
              <h3 className="font-bold text-slate-800 text-base">Consulta tus números</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Revisa cuánto vendiste hoy, qué productos están por agotarse y cuál es tu ganancia
                limpia.
              </p>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            10. VIDEO TUTORIAL GUIADO (CON CARGA DIFERIDA)
        ───────────────────────────────────────────────────────────── */}
        <section className="py-16 md:py-20 bg-white border-y border-slate-200">
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
                <p className="text-white font-bold text-base">Aprende a usar Gestión Neiva</p>
                <span className="text-xs text-slate-300 block">
                  Duración aproximada: 1 minuto · Carga bajo demanda
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            11. COMUNIDAD Y REDES SOCIALES (CON PLACEHOLDERS)
        ───────────────────────────────────────────────────────────── */}
        <section className="py-16 md:py-20 max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-8">
          <div className="max-w-xl mx-auto space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              Comunidad
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Síguenos y conoce lo que estamos construyendo
            </h2>
            <p className="text-sm text-slate-600">
              Gestión Neiva es una iniciativa viva en constante diálogo con los comerciantes de
              nuestra ciudad. Conéctate con nosotros en nuestros canales oficiales:
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <span className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 shadow-xs">
              Instagram: [URL INSTAGRAM]
            </span>
            <span className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 shadow-xs">
              Facebook: [URL FACEBOOK]
            </span>
            <span className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 shadow-xs">
              TikTok: [URL TIKTOK]
            </span>
            <span className="px-4 py-2 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 shadow-xs">
              YouTube: [URL YOUTUBE]
            </span>
            <span className="px-4 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-800 shadow-xs">
              Comunidad WhatsApp: [WHATSAPP COMUNIDAD]
            </span>
          </div>
        </section>

        {/* ─────────────────────────────────────────────────────────────
            12. PREGUNTAS FRECUENTES (FAQ REALISTA)
        ───────────────────────────────────────────────────────────── */}
        <section id="faq" className="py-16 md:py-20 bg-white border-y border-slate-200">
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
            Comienza a organizar tu negocio con mayor orden y tranquilidad
          </h2>
          <p className="text-base text-slate-600 max-w-xl mx-auto leading-relaxed">
            Únete a la iniciativa que busca acercar herramientas útiles y comprensibles al comercio
            popular de Neiva.
          </p>
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to="/registro"
              className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base px-8 py-4 rounded-2xl transition-all shadow-md active:scale-98 flex items-center justify-center gap-2"
            >
              <span>Crear cuenta y comenzar</span>
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
      <footer className="border-t border-slate-200 bg-white py-12 text-slate-500 text-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold">
              <Store size={18} />
            </div>
            <div>
              <span className="font-bold text-slate-800 text-sm block">Gestión Neiva</span>
              <span>Herramienta digital para pequeños comercios y economía popular</span>
            </div>
          </div>

          <div className="flex items-center gap-6 text-slate-600 font-medium">
            <a href="#problema" className="hover:text-emerald-700">El problema</a>
            <a href="#proposito" className="hover:text-emerald-700">Nuestra propuesta</a>
            <a href="#como-funciona" className="hover:text-emerald-700">Cómo funciona</a>
            <a href="#faq" className="hover:text-emerald-700">Preguntas</a>
            <Link to="/login" className="hover:text-emerald-700">Acceso a tienda</Link>
          </div>

          <div className="text-center sm:text-right text-[11px] text-slate-400">
            <span>Neiva, Huila, Colombia</span>
            <span className="block mt-0.5">Tecnología que se adapta a las personas</span>
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
                <h3 className="font-bold text-sm sm:text-base">Demostración: ¿Cómo funciona Gestión Neiva?</h3>
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
