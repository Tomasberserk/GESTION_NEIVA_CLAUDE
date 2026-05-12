import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useProductos } from '../hooks/useProductos'
import ProductoCard from '../components/ProductoCard'
import ModalProducto from '../components/ModalProducto'

export default function Inventario() {
  const { usuario } = useAuth()
  const { productos, tienda, cargando, error, crear, actualizar, eliminar, cargar } = useProductos()
  const [busqueda, setBusqueda] = useState('')

  useEffect(() => {
    const handler = () => cargar()
    window.addEventListener('venta-realizada', handler)
    return () => window.removeEventListener('venta-realizada', handler)
  }, [cargar])
  const [modalAbierto, setModalAbierto] = useState(false)
  const [productoEditar, setProductoEditar] = useState(null)
  const esAdmin = usuario?.rol === 'admin'

  const filtrados = productos.filter(
    p =>
      p.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
      p.codigo_barras.includes(busqueda)
  )

  const guardar = async (payload) => {
    if (productoEditar) {
      await actualizar(productoEditar.id, payload)
    } else {
      await crear(payload)
    }
  }

  const abrirEditar = (producto) => {
    setProductoEditar(producto)
    setModalAbierto(true)
  }

  const abrirNuevo = () => {
    setProductoEditar(null)
    setModalAbierto(true)
  }

  const confirmarEliminar = async (id) => {
    if (!window.confirm('¿Eliminar este producto?')) return
    try {
      await eliminar(id)
    } catch (e) {
      alert(e.message)
    }
  }

  if (cargando) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-500" />
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">{tienda || 'Inventario'}</h1>
          <p className="text-gray-500 text-sm">{productos.length} productos</p>
        </div>
        <div className="flex gap-3 w-full sm:w-auto">
          <input
            type="text"
            placeholder="Buscar por nombre o código..."
            value={busqueda}
            onChange={e => setBusqueda(e.target.value)}
            className="flex-1 sm:w-64 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
          />
          {esAdmin && (
            <button
              onClick={abrirNuevo}
              className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap"
            >
              + Producto
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4 text-sm">{error}</div>
      )}

      {filtrados.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <div className="text-5xl mb-3">📭</div>
          <p>{busqueda ? 'Sin resultados para esa búsqueda' : 'No hay productos aún'}</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {filtrados.map(p => (
            <ProductoCard
              key={p.id}
              producto={p}
              onEditar={abrirEditar}
              onEliminar={confirmarEliminar}
            />
          ))}
        </div>
      )}

      {modalAbierto && (
        <ModalProducto
          producto={productoEditar}
          onGuardar={guardar}
          onCerrar={() => setModalAbierto(false)}
        />
      )}
    </div>
  )
}
