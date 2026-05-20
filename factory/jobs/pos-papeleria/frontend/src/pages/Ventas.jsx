import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useProductos } from '../hooks/useProductos'
import ProductoCard from '../components/ProductoCard'
import CartPanel from '../components/CartPanel'
import ModalProducto from '../components/ModalProducto'
import { Search, Plus } from 'lucide-react'

const CATEGORIAS = [
  { value: null,               label: 'Todas',    icon: '🏷️' },
  { value: 'Utiles escolares', label: 'Útiles',   icon: '✏️' },
  { value: 'Papel y resmas',   label: 'Papel',    icon: '📄' },
  { value: 'Tecnologia',       label: 'Tech',     icon: '💻' },
  { value: 'Servicios',        label: 'Servicios',icon: '🖨️' },
  { value: 'Miscelanea',       label: 'Otros',    icon: '🗂️' },
]

export default function Ventas() {
  const { usuario } = useAuth()
  const { productos, cargando, cargar, crear, actualizar, eliminar } = useProductos()
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

  const handleVentaCompletada = () => {
    cargar()
    window.dispatchEvent(new Event('venta-completada'))
  }

  return (
    <div className="h-full flex overflow-hidden">

      {/* Left: product browser */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Sticky top bar */}
        <div className="bg-slate-50 px-4 sm:px-5 pt-4 pb-3 border-b border-slate-200 shrink-0">

          {/* Search row */}
          <div className="flex items-center gap-3 mb-3">
            <div className="relative flex-1">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar producto o código..."
                value={busqueda}
                onChange={e => setBusqueda(e.target.value)}
                className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400"
              />
            </div>
            {esAdmin && (
              <button
                onClick={() => { setProductoEditar(null); setModalAbierto(true) }}
                title="Nuevo producto"
                className="w-10 h-10 bg-white border border-slate-200 hover:border-indigo-300 hover:text-indigo-600 text-slate-500 rounded-xl flex items-center justify-center transition-colors shrink-0"
              >
                <Plus size={17} />
              </button>
            )}
          </div>

          {/* Category pills */}
          <div className="flex gap-2 overflow-x-auto pb-0.5 scrollbar-hide">
            {CATEGORIAS.map(cat => (
              <button
                key={cat.value ?? 'all'}
                onClick={() => setCategoria(cat.value)}
                className={[
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all shrink-0',
                  categoria === cat.value
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-white text-slate-600 border border-slate-200 hover:border-indigo-300 hover:text-indigo-600',
                ].join(' ')}
              >
                <span>{cat.icon}</span>
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Product grid */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5">
          {cargando ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
            </div>
          ) : filtrados.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-400">
              <span className="text-4xl mb-3">✏️</span>
              <p className="text-sm">
                {busqueda || categoria ? 'Sin resultados' : 'No hay productos en el catálogo'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3">
              {filtrados.map(p => (
                <ProductoCard
                  key={p.id}
                  producto={p}
                  modo="pos"
                  onEditar={esAdmin ? (prod) => { setProductoEditar(prod); setModalAbierto(true) } : undefined}
                  onEliminar={esAdmin ? eliminar : undefined}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right: cart panel — always visible */}
      <CartPanel onVentaCompletada={handleVentaCompletada} />

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
