import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'

const BASE = 'http://localhost:8000'

export default function ProductoCard({ producto, onEditar, onEliminar }) {
  const { agregar } = useCart()
  const { usuario } = useAuth()
  const esAdmin = usuario?.rol === 'admin'
  const sinStock = producto.cantidad_actual === 0

  return (
    <div
      className={`bg-white rounded-xl shadow-sm border flex flex-col gap-3 p-4 ${
        sinStock ? 'opacity-60' : ''
      }`}
    >
      {producto.foto_url ? (
        <img
          src={`${BASE}${producto.foto_url}`}
          alt={producto.nombre}
          className="w-full h-36 object-cover rounded-lg"
        />
      ) : (
        <div className="w-full h-36 bg-violet-50 rounded-lg flex items-center justify-center text-4xl">
          📦
        </div>
      )}

      <div>
        <h3 className="font-semibold text-gray-800 truncate text-sm">{producto.nombre}</h3>
        <p className="text-xs text-gray-400">Cód: {producto.codigo_barras}</p>
      </div>

      <div className="flex items-center justify-between">
        <span className="font-bold text-violet-600">
          ${producto.precio_venta.toLocaleString('es-CO')}
        </span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            sinStock
              ? 'bg-red-100 text-red-600'
              : producto.cantidad_actual <= 5
              ? 'bg-yellow-100 text-yellow-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {sinStock ? 'Sin stock' : `${producto.cantidad_actual} uds`}
        </span>
      </div>

      <div className="flex gap-2 mt-auto">
        <button
          onClick={() => agregar(producto)}
          disabled={sinStock}
          className="flex-1 bg-violet-600 hover:bg-violet-700 disabled:bg-gray-200 disabled:cursor-not-allowed text-white text-sm py-2 rounded-lg transition-colors"
        >
          Agregar
        </button>
        {esAdmin && (
          <>
            <button
              onClick={() => onEditar(producto)}
              title="Editar"
              className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              ✏️
            </button>
            <button
              onClick={() => onEliminar(producto.id)}
              title="Eliminar"
              className="px-3 py-2 text-sm bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors"
            >
              🗑️
            </button>
          </>
        )}
      </div>
    </div>
  )
}
