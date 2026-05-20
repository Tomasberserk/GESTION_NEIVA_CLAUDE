import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'

const BASE = import.meta.env.VITE_API_URL || '/api'

const ICONO_CAT = {
  'Utiles escolares': '✏️',
  'Papel y resmas':   '📄',
  'Tecnologia':       '💻',
  'Servicios':        '🖨️',
  'Miscelanea':       '🗂️',
}

const fmt = (n) => Number(n).toLocaleString('es-CO', { maximumFractionDigits: 0 })

function StockBadge({ cantidad, minimo }) {
  if (cantidad === 0) {
    return (
      <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-red-100 text-red-600">
        Agotado
      </span>
    )
  }
  if (cantidad <= minimo) {
    return (
      <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700">
        {cantidad} uds
      </span>
    )
  }
  return (
    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700">
      {cantidad} uds
    </span>
  )
}

export default function ProductoCard({ producto, modo = 'pos', onEditar, onEliminar }) {
  const { agregar } = useCart()
  const { usuario } = useAuth()
  const esAdmin = usuario?.rol === 'admin'
  const sinStock = producto.cantidad_actual === 0
  const icono = ICONO_CAT[producto.categoria] || '🗂️'

  const fotoUrl = producto.foto_url
    ? (producto.foto_url.startsWith('http') ? producto.foto_url : `${BASE}${producto.foto_url}`)
    : null

  if (modo === 'pos') {
    return (
      <button
        type="button"
        onClick={() => !sinStock && agregar(producto)}
        disabled={sinStock}
        className={[
          'group relative bg-white rounded-xl border-2 text-left transition-all w-full',
          sinStock
            ? 'border-slate-100 opacity-50 cursor-not-allowed'
            : 'border-transparent hover:border-indigo-200 hover:shadow-lg hover:shadow-indigo-100/40 active:scale-[0.97] cursor-pointer shadow-sm',
        ].join(' ')}
      >
        {/* Image / icon area */}
        <div
          className={[
            'h-24 rounded-t-xl flex items-center justify-center overflow-hidden',
            sinStock ? 'bg-slate-100' : 'bg-indigo-50 group-hover:bg-indigo-100 transition-colors',
          ].join(' ')}
        >
          {fotoUrl ? (
            <img src={fotoUrl} alt={producto.nombre} className="w-full h-full object-cover" />
          ) : (
            <span className="text-4xl">{icono}</span>
          )}
        </div>

        {/* Info */}
        <div className="p-3">
          <p className="text-[10px] font-medium text-indigo-400 uppercase tracking-wide truncate">
            {producto.categoria}
          </p>
          <p className="font-semibold text-slate-800 text-sm leading-snug mt-0.5 truncate">
            {producto.nombre}
          </p>
          <div className="flex items-center justify-between mt-2">
            <span className="text-base font-bold text-slate-900">
              ${fmt(producto.precio_venta)}
            </span>
            <StockBadge cantidad={producto.cantidad_actual} minimo={producto.stock_minimo} />
          </div>
        </div>

        {/* Hover CTA */}
        {!sinStock && (
          <div className="absolute inset-x-0 bottom-0 flex items-center justify-center pb-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <span className="text-[10px] font-bold text-indigo-500">+ Agregar</span>
          </div>
        )}
      </button>
    )
  }

  // modo === 'gestion' — horizontal layout for Inventario
  return (
    <div
      className={[
        'bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4',
        sinStock ? 'opacity-60' : '',
      ].join(' ')}
    >
      <div className="w-11 h-11 rounded-lg bg-indigo-50 flex items-center justify-center text-2xl shrink-0">
        {fotoUrl ? (
          <img src={fotoUrl} alt={producto.nombre} className="w-full h-full object-cover rounded-lg" />
        ) : (
          icono
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="font-semibold text-sm text-slate-800 truncate">{producto.nombre}</p>
            <p className="text-[11px] text-slate-400 mt-0.5 truncate">
              {producto.codigo_barras} · {producto.categoria}
            </p>
          </div>
          <StockBadge cantidad={producto.cantidad_actual} minimo={producto.stock_minimo} />
        </div>
        <div className="flex items-center gap-4 mt-1.5">
          <span className="text-xs text-slate-500">
            Costo: <span className="font-medium text-slate-700">${fmt(producto.precio_costo)}</span>
          </span>
          <span className="text-xs text-slate-500">
            Venta: <span className="font-bold text-indigo-600">${fmt(producto.precio_venta)}</span>
          </span>
          <span className="text-xs text-slate-400">
            Mín: {producto.stock_minimo}
          </span>
        </div>
      </div>

      {esAdmin && onEditar && (
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => onEditar(producto)}
            className="px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Editar
          </button>
          {onEliminar && (
            <button
              onClick={() => onEliminar(producto.id)}
              className="px-3 py-1.5 text-xs font-medium text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            >
              Eliminar
            </button>
          )}
        </div>
      )}
    </div>
  )
}
