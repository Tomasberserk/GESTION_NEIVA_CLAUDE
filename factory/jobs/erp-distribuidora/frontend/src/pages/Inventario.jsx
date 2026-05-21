import { useState, useEffect, useCallback } from 'react'
import { Search, Plus, Package, Pencil, Trash2, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useProductos } from '../hooks/useProductos'

const fmt = (n) => Number(n ?? 0).toLocaleString('es-CO', { maximumFractionDigits: 0 })

const UNIDADES = ['UNIDAD', 'CAJA', 'BULTO', 'KG', 'LITRO', 'METRO']

function ModalProducto({ producto, onGuardar, onCerrar }) {
  const [form, setForm] = useState({
    nombre: producto?.nombre ?? '',
    codigo_barras: producto?.codigo_barras ?? '',
    categoria: producto?.categoria ?? '',
    precio_costo: producto?.precio_costo ?? '',
    precio_venta: producto?.precio_venta ?? '',
    cantidad_actual: producto?.cantidad_actual ?? '',
    unidad_medida: producto?.unidad_medida ?? 'UNIDAD',
  })
  const [error, setError] = useState('')
  const [guardando, setGuardando] = useState(false)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setGuardando(true)
    try {
      await onGuardar({
        ...form,
        precio_costo: parseFloat(form.precio_costo),
        precio_venta: parseFloat(form.precio_venta),
        cantidad_actual: parseFloat(form.cantidad_actual),
      })
      onCerrar()
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="font-semibold text-slate-900">{producto ? 'Editar producto' : 'Nuevo producto'}</h2>
          <button onClick={onCerrar} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <p className="text-sm text-red-600 bg-red-50 rounded-lg p-3">{error}</p>}
          {[
            { label: 'Nombre', key: 'nombre', type: 'text', required: true },
            { label: 'Código de barras', key: 'codigo_barras', type: 'text', required: true },
            { label: 'Categoría', key: 'categoria', type: 'text' },
            { label: 'Precio costo', key: 'precio_costo', type: 'number', required: true },
            { label: 'Precio venta', key: 'precio_venta', type: 'number', required: true },
            { label: 'Cantidad actual', key: 'cantidad_actual', type: 'number', required: true },
          ].map(({ label, key, type, required }) => (
            <div key={key}>
              <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
              <input
                type={type}
                required={required}
                step={type === 'number' ? 'any' : undefined}
                value={form[key]}
                onChange={set(key)}
                className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </div>
          ))}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Unidad de medida</label>
            <select
              value={form.unidad_medida}
              onChange={set('unidad_medida')}
              className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
            >
              {UNIDADES.map(u => <option key={u} value={u}>{u}</option>)}
            </select>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onCerrar} className="flex-1 py-2 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50">
              Cancelar
            </button>
            <button type="submit" disabled={guardando} className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-medium">
              {guardando ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Inventario() {
  const { usuario } = useAuth()
  const { productos, cargando, cargar, crear, actualizar, eliminar } = useProductos()
  const [busqueda, setBusqueda] = useState('')
  const [modalAbierto, setModalAbierto] = useState(false)
  const [editando, setEditando] = useState(null)
  const esAdmin = usuario?.rol === 'admin'

  useEffect(() => { cargar() }, [cargar])

  const buscar = useCallback(() => { cargar(busqueda) }, [cargar, busqueda])

  useEffect(() => {
    const t = setTimeout(buscar, 300)
    return () => clearTimeout(t)
  }, [busqueda, buscar])

  const guardar = async (payload) => {
    if (editando) await actualizar(editando.id, payload)
    else await crear(payload)
    cargar(busqueda)
  }

  const handleEliminar = async (p) => {
    if (!confirm(`¿Desactivar "${p.nombre}"?`)) return
    try {
      await eliminar(p.id)
      cargar(busqueda)
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="bg-white border-b border-slate-200 px-4 sm:px-6 py-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-md">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por nombre..."
              value={busqueda}
              onChange={e => setBusqueda(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
            />
          </div>
          {esAdmin && (
            <button
              onClick={() => { setEditando(null); setModalAbierto(true) }}
              className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-medium"
            >
              <Plus size={15} />
              <span className="hidden sm:inline">Nuevo</span>
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        {cargando ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
          </div>
        ) : productos.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400">
            <Package size={32} className="mb-3" />
            <p className="text-sm">{busqueda ? 'Sin resultados' : 'Sin productos en el catálogo'}</p>
          </div>
        ) : (
          <div className="space-y-2">
            {productos.map(p => (
              <div key={p.id} className="bg-white rounded-xl border border-slate-200 px-4 py-3 flex items-center gap-4">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-800 text-sm truncate">{p.nombre}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{p.codigo_barras} · {p.categoria || 'Sin categoría'} · {p.unidad_medida}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold text-slate-800">${fmt(p.precio_venta)}</p>
                  <p className="text-xs text-slate-400">costo: ${fmt(p.precio_costo)}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className={`text-sm font-bold ${p.cantidad_actual <= 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                    {p.cantidad_actual}
                  </p>
                  <p className="text-xs text-slate-400">stock</p>
                </div>
                {esAdmin && (
                  <div className="flex gap-1 shrink-0">
                    <button
                      onClick={() => { setEditando(p); setModalAbierto(true) }}
                      className="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                    >
                      <Pencil size={15} />
                    </button>
                    <button
                      onClick={() => handleEliminar(p)}
                      className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {modalAbierto && (
        <ModalProducto
          producto={editando}
          onGuardar={guardar}
          onCerrar={() => setModalAbierto(false)}
        />
      )}
    </div>
  )
}
