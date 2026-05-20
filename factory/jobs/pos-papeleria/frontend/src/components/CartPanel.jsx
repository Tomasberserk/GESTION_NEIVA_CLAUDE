import { useState } from 'react'
import { useCart } from '../context/CartContext'
import { useVentas } from '../hooks/useVentas'
import { ShoppingCart } from 'lucide-react'

const fmt = (n) => Number(n).toLocaleString('es-CO', { maximumFractionDigits: 0 })

export default function CartPanel({ onVentaCompletada }) {
  const { carrito, agregar, restar, eliminar, vaciar, total, totalItems } = useCart()
  const { registrar } = useVentas()
  const [procesando, setProcesando] = useState(false)
  const [mensaje, setMensaje] = useState(null)

  const checkout = async () => {
    if (!carrito.length) return
    setProcesando(true)
    setMensaje(null)
    try {
      const items = carrito.map(i => ({ producto_id: i.id, cantidad: i.cantidad }))
      const resultado = await registrar(items)
      setMensaje({
        tipo: 'ok',
        texto: `Cobrado: $${fmt(resultado.total)}`,
      })
      vaciar()
      onVentaCompletada?.()
      setTimeout(() => setMensaje(null), 4000)
    } catch (e) {
      setMensaje({ tipo: 'error', texto: e.message })
    } finally {
      setProcesando(false)
    }
  }

  return (
    <div className="w-72 xl:w-80 border-l border-slate-200 bg-white flex flex-col shrink-0">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-100 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingCart size={16} className="text-slate-500" />
            <h2 className="font-semibold text-slate-800 text-sm">Orden actual</h2>
          </div>
          {totalItems > 0 && (
            <span className="bg-indigo-100 text-indigo-700 text-xs font-bold px-2 py-0.5 rounded-full">
              {totalItems}
            </span>
          )}
        </div>
      </div>

      {/* Items list */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
        {carrito.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-12 text-slate-400">
            <ShoppingCart size={36} className="mb-3 text-slate-300" />
            <p className="text-sm font-medium">Sin productos</p>
            <p className="text-xs mt-1 text-slate-300 text-center">
              Haz clic en un producto para agregarlo
            </p>
          </div>
        ) : (
          carrito.map(item => (
            <div key={item.id} className="bg-slate-50 rounded-xl p-3">
              <div className="flex items-start justify-between gap-2 mb-2">
                <p className="font-medium text-sm text-slate-800 leading-snug flex-1 truncate">
                  {item.nombre}
                </p>
                <button
                  onClick={() => eliminar(item.id)}
                  className="text-slate-300 hover:text-red-500 transition-colors shrink-0 text-sm leading-none"
                >
                  ✕
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => restar(item.id)}
                    className="w-7 h-7 bg-white border border-slate-200 hover:bg-red-50 hover:border-red-200 rounded-lg text-sm font-bold text-slate-600 transition-colors"
                  >
                    −
                  </button>
                  <span className="w-8 text-center text-sm font-semibold text-slate-800">
                    {item.cantidad}
                  </span>
                  <button
                    onClick={() => agregar(item)}
                    disabled={item.cantidad >= item.cantidad_actual}
                    className="w-7 h-7 bg-white border border-slate-200 hover:bg-emerald-50 hover:border-emerald-200 disabled:opacity-30 disabled:cursor-not-allowed rounded-lg text-sm font-bold text-slate-600 transition-colors"
                  >
                    +
                  </button>
                </div>
                <span className="text-sm font-semibold text-slate-700">
                  ${fmt(item.precio_venta * item.cantidad)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-slate-100 space-y-3 shrink-0">
        {mensaje && (
          <div
            className={`p-3 rounded-xl text-sm text-center font-medium ${
              mensaje.tipo === 'ok'
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {mensaje.texto}
          </div>
        )}

        <div className="flex items-baseline justify-between">
          <span className="text-sm text-slate-500">Total</span>
          <span className="text-2xl font-bold text-slate-900">${fmt(total)}</span>
        </div>

        <button
          onClick={checkout}
          disabled={!carrito.length || procesando}
          className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-200 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl transition-all text-base active:scale-[0.98] shadow-sm shadow-emerald-200"
        >
          {procesando ? 'Procesando...' : 'Cobrar'}
        </button>

        {carrito.length > 0 && (
          <button
            onClick={vaciar}
            className="w-full text-xs text-slate-400 hover:text-red-500 transition-colors py-1"
          >
            Vaciar orden
          </button>
        )}
      </div>
    </div>
  )
}
