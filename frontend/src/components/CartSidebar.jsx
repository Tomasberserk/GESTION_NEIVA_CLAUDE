import { useState } from 'react'
import { useCart } from '../context/CartContext'
import { useVentas } from '../hooks/useVentas'

export default function CartSidebar() {
  const { carrito, carritoAbierto, setCarritoAbierto, agregar, restar, eliminar, vaciar, total } =
    useCart()
  const { registrar } = useVentas()
  const [procesando, setProcesando] = useState(false)
  const [mensaje, setMensaje] = useState(null)

  const checkout = async () => {
    if (!carrito.length) return
    setProcesando(true)
    setMensaje(null)
    try {
      const detalles = carrito.map(i => ({ producto_id: i.id, cantidad: i.cantidad }))
      const resultado = await registrar(detalles)
      setMensaje({
        tipo: 'ok',
        texto: `Venta registrada — Total: $${resultado.total.toLocaleString('es-CO')}`,
      })
      vaciar()
      setTimeout(() => setMensaje(null), 5000)
    } catch (e) {
      setMensaje({ tipo: 'error', texto: e.message })
    } finally {
      setProcesando(false)
    }
  }

  return (
    <>
      {carritoAbierto && (
        <div
          className="fixed inset-0 bg-black/30 z-30"
          onClick={() => setCarritoAbierto(false)}
        />
      )}

      <div
        className={`fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-40 flex flex-col transition-transform duration-300 ${
          carritoAbierto ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="font-bold text-lg">Carrito</h2>
          <button
            onClick={() => setCarritoAbierto(false)}
            className="text-gray-400 hover:text-gray-700 text-xl leading-none"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {carrito.length === 0 ? (
            <p className="text-center text-gray-400 mt-10 text-sm">El carrito está vacío</p>
          ) : (
            carrito.map(item => (
              <div key={item.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{item.nombre}</p>
                  <p className="text-violet-600 text-sm">
                    ${item.precio_venta.toLocaleString('es-CO')}
                  </p>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => restar(item.id)}
                    className="w-7 h-7 bg-gray-200 hover:bg-gray-300 rounded text-sm font-bold"
                  >
                    −
                  </button>
                  <span className="w-6 text-center text-sm font-medium">{item.cantidad}</span>
                  <button
                    onClick={() => agregar(item)}
                    className="w-7 h-7 bg-gray-200 hover:bg-gray-300 rounded text-sm font-bold"
                  >
                    +
                  </button>
                </div>
                <button
                  onClick={() => eliminar(item.id)}
                  className="text-red-400 hover:text-red-600 text-sm ml-1"
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>

        {mensaje && (
          <div
            className={`mx-4 p-3 rounded-lg text-sm ${
              mensaje.tipo === 'ok'
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {mensaje.tipo === 'ok' ? '✅ ' : '❌ '}
            {mensaje.texto}
          </div>
        )}

        <div className="p-4 border-t space-y-3">
          <div className="flex justify-between font-bold text-lg">
            <span>Total</span>
            <span className="text-violet-600">${total.toLocaleString('es-CO')}</span>
          </div>
          <button
            onClick={checkout}
            disabled={!carrito.length || procesando}
            className="w-full bg-violet-600 hover:bg-violet-700 disabled:bg-gray-200 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {procesando ? 'Procesando...' : 'Cobrar venta'}
          </button>
          {carrito.length > 0 && (
            <button
              onClick={vaciar}
              className="w-full text-sm text-gray-400 hover:text-red-500 transition-colors"
            >
              Vaciar carrito
            </button>
          )}
        </div>
      </div>
    </>
  )
}
