import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useProductos } from '../hooks/useProductos'
import ProductoCard from '../components/ProductoCard'
import ModalProducto from '../components/ModalProducto'
import { Search, Plus } from 'lucide-react'

const CATS = [
  { value: null,               label: 'Todos' },
  { value: 'Utiles escolares', label: '✏️ Útiles' },
  { value: 'Papel y resmas',   label: '📄 Papel' },
  { value: 'Tecnologia',       label: '💻 Tech' },
  { value: 'Servicios',        label: '🖨️ Servicios' },
  { value: 'Miscelanea',       label: '🗂️ Otros' },
]

export default function Inventario() {
  const { usuario } = useAuth()
  const { productos, tienda, cargando, error, cargar, crear, actualizar, eliminar } = useProductos()
  const [busqueda, setBusqueda] = useState('')
  const [categoria, setCategoria] = useState(null)
  const [modalAbierto, setModalAbierto] = useState(false)
  const [productoEditar, setProductoEditar] = useState(null)
  const esAdmin = usuario?.rol === 'admin'

  useEffect(() => {
    window.addEventListener('venta-completada', cargar)
    return () => window.removeEventListener('venta-completada', cargar)
  }, [cargar])

  const filtrados = productos.filter(p => {
    const matchBusqueda = !busqueda ||
      p.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
      p.codigo_barras.includes(busqueda)
    const matchCat = !categoria || p.categoria === categoria
    return matchBusqueda && matchCat
  })

  const guardar = async (payload) => {
    if (productoEditar) await actualizar(productoEditar.id, payload)
    else await crear(payload)
  }

  const confirmarEliminar = async (id) => {
    if (!window.confirm('¿Eliminar este producto?')) return
    try {
      await eliminar(id)
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4 sm:p-6">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
          <div>
            <h1 className="text-xl font-bold text-slate-900">{tienda || 'Inventario'}</h1>
            <p className="text-sm text-slate-500 mt-0.5">{productos.length} productos en catálogo</p>
          </div>
          {esAdmin && (
            <button
              onClick={() => { setProductoEditar(null); setModalAbierto(true) }}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-colors"
            >
              <Plus size={15} />
              Nuevo producto
            </button>
          )}
        </div>

        {/* Search + filter */}
        <div className="flex flex-col sm:flex-row gap-3 mb-5">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o código..."
              value={busqueda}
              onChange={e => setBusqueda(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400"
            />
          </div>
          <div className="flex gap-1.5 flex-wrap">
            {CATS.map(cat => (
              <button
                key={cat.value ?? 'all'}
                onClick={() => setCategoria(cat.value)}
                className={`px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  categoria === cat.value
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-slate-600 border border-slate-200 hover:border-indigo-300'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-4 text-sm border border-red-100">
            {error}
          </div>
        )}

        {cargando ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
          </div>
        ) : filtrados.length === 0 ? (
          <div className="text-center py-16 text-slate-400">
            <div className="text-4xl mb-3">📋</div>
            <p className="text-sm">
              {busqueda || categoria ? 'Sin resultados para esa búsqueda' : 'No hay productos aún'}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtrados.map(p => (
              <ProductoCard
                key={p.id}
                producto={p}
                modo="gestion"
                onEditar={esAdmin ? (prod) => { setProductoEditar(prod); setModalAbierto(true) } : undefined}
                onEliminar={esAdmin ? confirmarEliminar : undefined}
              />
            ))}
          </div>
        )}
      </div>

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
