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
              Síguenos para aprender trucos de mostrador, conocer experiencias de tenderos de Neiva y el Huila, y participar en capacitaciones gratuitas.
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
                <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">Comunidad regional de tenderos y eventos</p>
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
                    Comunidad WhatsApp: Comerciantes Neiva & Huila
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                    Comunidad Oficial
                  </span>
                </div>
                <p className="text-xs font-semibold text-emerald-800 mt-0.5">Gestión de Inventario Inteligente</p>
                <p className="text-[11px] text-emerald-700 mt-0.5">
                  Grupo abierto para resolver dudas, compartir consejos de abastecimiento y conectar con otros comerciantes de la región.
                </p>
              </div>
            </a>
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

          <div className="flex flex-wrap items-center gap-5 text-slate-600 font-medium">
            <a href="#problema" className="hover:text-emerald-700">El problema</a>
            <a href="#proposito" className="hover:text-emerald-700">Nuestra propuesta</a>
            <a href="#como-funciona" className="hover:text-emerald-700">Cómo funciona</a>
            <a href="#comunidad" className="hover:text-emerald-700">Redes sociales</a>
            <a href="#faq" className="hover:text-emerald-700">Preguntas</a>
            <Link to="/login" className="hover:text-emerald-700 font-semibold text-emerald-800">Acceso a tienda</Link>
          </div>

          <div className="text-center sm:text-right text-[11px] text-slate-400">
            <span>Neiva, Huila, Colombia</span>
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
