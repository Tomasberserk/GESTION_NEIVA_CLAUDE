import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  CheckCircle2,
  Circle,
  Package,
  ShoppingCart,
  TrendingUp,
  HelpCircle,
  X,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from 'lucide-react'

export default function GuiaPrimerosPasos({ totalProductos = 0, ventasHoy = 0, onVerTutorial }) {
  const [oculto, setOculto] = useState(() => {
    return localStorage.getItem('guia_primeros_pasos_oculta') === 'true'
  })
  const [colapsado, setColapsado] = useState(false)

  const paso1Completo = totalProductos > 0
  const paso3Completo = ventasHoy > 0
  const paso2Completo = paso1Completo // Si ya agregó productos, conoce el mostrador
  const paso4Completo = paso3Completo // Si ya vendió, puede consultar su información

  const pasos = [
    {
      id: 1,
      titulo: 'Agrega tu primer producto',
      descripcion: 'Registra el nombre, precio de costo y precio de venta de tus artículos.',
      completo: paso1Completo,
      link: '/inventario',
      linkTexto: 'Ir a Productos',
      icono: Package,
    },
    {
      id: 2,
      titulo: 'Conoce cómo funciona el mostrador',
      descripcion: 'Aprende a buscar artículos, ingresar cantidades o pesos y usar el carrito.',
      completo: paso2Completo,
      link: '/inventario',
      linkTexto: 'Ver Mostrador',
      icono: ShoppingCart,
    },
    {
      id: 3,
      titulo: 'Registra tu primera venta real',
      descripcion: 'Realiza el cobro de tu primera venta con un cliente en tu tienda.',
      completo: paso3Completo,
      link: '/inventario',
      linkTexto: 'Cobrar en Mostrador',
      icono: ShoppingCart,
    },
    {
      id: 4,
      titulo: 'Consulta la información de tu negocio',
      descripcion: 'Revisa tus ganancias limpias y qué productos necesitas reabastecer.',
      completo: paso4Completo,
      link: '/reportes',
      linkTexto: 'Ver Reportes',
      icono: TrendingUp,
    },
  ]

  const completados = pasos.filter((p) => p.completo).length
  const porcentaje = Math.round((completados / pasos.length) * 100)

  const handleCerrarGuia = () => {
    localStorage.setItem('guia_primeros_pasos_oculta', 'true')
    setOculto(true)
  }

  if (oculto) return null

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden mb-6 transition-all">
      {/* Cabecera de la guía */}
      <div className="p-4 sm:p-5 flex items-center justify-between border-b border-slate-100 bg-gradient-to-r from-emerald-50/50 via-white to-white">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm">
            🌱
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-slate-800 text-sm sm:text-base">
                Primeros pasos para organizar tu tienda
              </h2>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                {completados} de {pasos.length} completados ({porcentaje}%)
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Sigue esta guía sencilla para familiarizarte con las funciones esenciales
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {onVerTutorial && (
            <button
              type="button"
              onClick={onVerTutorial}
              className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 px-2.5 py-1.5 rounded-lg hover:bg-emerald-50 transition-colors hidden sm:inline-flex items-center gap-1"
            >
              <span>Ver video guía</span>
            </button>
          )}

          <button
            type="button"
            onClick={() => setColapsado(!colapsado)}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
            title={colapsado ? 'Expandir guía' : 'Colapsar guía'}
          >
            {colapsado ? <ChevronDown size={18} /> : <ChevronUp size={18} />}
          </button>

          <button
            type="button"
            onClick={handleCerrarGuia}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
            title="Ocultar guía de primeros pasos"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="w-full bg-slate-100 h-1.5">
        <div
          className="bg-emerald-600 h-1.5 transition-all duration-500"
          style={{ width: `${porcentaje}%` }}
        />
      </div>

      {/* Lista de pasos colapsable */}
      {!colapsado && (
        <div className="p-4 sm:p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {pasos.map((paso) => {
            const Icon = paso.icono
            return (
              <div
                key={paso.id}
                className={`p-3.5 rounded-xl border transition-all flex flex-col justify-between ${
                  paso.completo
                    ? 'bg-emerald-50/40 border-emerald-200'
                    : 'bg-[#fafaf9] border-slate-200/80 hover:border-slate-300'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-500">Paso {paso.id}</span>
                    {paso.completo ? (
                      <CheckCircle2 size={18} className="text-emerald-600" />
                    ) : (
                      <Circle size={18} className="text-slate-300" />
                    )}
                  </div>
                  <h3
                    className={`font-semibold text-xs sm:text-sm ${
                      paso.completo ? 'text-emerald-950 font-bold' : 'text-slate-800'
                    }`}
                  >
                    {paso.titulo}
                  </h3>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {paso.descripcion}
                  </p>
                </div>

                <div className="pt-3 mt-2 border-t border-slate-200/60 flex items-center justify-between">
                  <Link
                    to={paso.link}
                    className={`text-xs font-bold transition-colors ${
                      paso.completo
                        ? 'text-emerald-700 hover:text-emerald-800'
                        : 'text-violet-600 hover:text-violet-700'
                    }`}
                  >
                    {paso.linkTexto} →
                  </Link>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
