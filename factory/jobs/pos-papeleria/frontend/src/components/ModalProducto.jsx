import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

const CATEGORIAS = [
  'Utiles escolares',
  'Papel y resmas',
  'Tecnologia',
  'Servicios',
  'Miscelanea',
]

const UNIDADES = [
  { value: 'unidad',  label: 'Unidad' },
  { value: 'paquete', label: 'Paquete' },
]

const cls = 'w-full border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-all bg-white'

export default function ModalProducto({ producto, onGuardar, onCerrar }) {
  const { usuario } = useAuth()
  const esEdicion = Boolean(producto)

  const [form, setForm] = useState({
    nombre: '',
    codigo_barras: '',
    precio_costo: '',
    precio_venta: '',
    cantidad_actual: '',
    stock_minimo: '5',
    unidad_medida: 'unidad',
    categoria: 'Utiles escolares',
    empresa_id: usuario?.empresa_id ?? '',
  })
  const [error, setError]     = useState(null)
  const [guardando, setGuardando] = useState(false)

  useEffect(() => {
    if (producto) {
      setForm({
        nombre:          producto.nombre,
        codigo_barras:   producto.codigo_barras,
        precio_costo:    producto.precio_costo,
        precio_venta:    producto.precio_venta,
        cantidad_actual: producto.cantidad_actual,
        stock_minimo:    producto.stock_minimo ?? 5,
        unidad_medida:   producto.unidad_medida ?? 'unidad',
        categoria:       producto.categoria ?? 'Utiles escolares',
        empresa_id:      producto.empresa_id,
      })
    }
  }, [producto])

  const cambiar = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const guardar = async (e) => {
    e.preventDefault()
    setGuardando(true)
    setError(null)
    try {
      const payload = {
        ...form,
        precio_costo:    parseFloat(form.precio_costo)    || 0,
        precio_venta:    parseFloat(form.precio_venta)    || 0,
        cantidad_actual: parseInt(form.cantidad_actual, 10) || 0,
        stock_minimo:    parseInt(form.stock_minimo, 10)   || 5,
      }
      await onGuardar(payload)
      onCerrar()
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">

        <div className="flex items-center justify-between p-6 border-b border-slate-100">
          <h2 className="font-bold text-slate-800">
            {esEdicion ? 'Editar producto' : 'Nuevo producto'}
          </h2>
          <button
            type="button"
            onClick={onCerrar}
            className="text-slate-400 hover:text-slate-700 text-xl leading-none transition-colors"
          >
            ✕
          </button>
        </div>

        <form onSubmit={guardar} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-xl text-sm border border-red-100">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
              Nombre *
            </label>
            <input name="nombre" value={form.nombre} onChange={cambiar}
              required={!esEdicion} type="text" className={cls} />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
              Código de barras *
            </label>
            <input name="codigo_barras" value={form.codigo_barras} onChange={cambiar}
              required={!esEdicion} type="text" placeholder="Escribe o escanea" className={cls} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
                Precio costo
              </label>
              <input name="precio_costo" value={form.precio_costo} onChange={cambiar}
                type="number" step="0.01" min="0" className={cls} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
                Precio venta
              </label>
              <input name="precio_venta" value={form.precio_venta} onChange={cambiar}
                type="number" step="0.01" min="0" className={cls} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
                Stock actual
              </label>
              <input name="cantidad_actual" value={form.cantidad_actual} onChange={cambiar}
                type="number" step="1" min="0" className={cls} />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
                Stock mínimo
              </label>
              <input name="stock_minimo" value={form.stock_minimo} onChange={cambiar}
                type="number" step="1" min="0" className={cls} />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
              Categoría *
            </label>
            <select name="categoria" value={form.categoria} onChange={cambiar}
              className={`${cls} bg-white`}>
              {CATEGORIAS.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
              Unidad de medida
            </label>
            <select name="unidad_medida" value={form.unidad_medida} onChange={cambiar}
              className={`${cls} bg-white`}>
              {UNIDADES.map(u => (
                <option key={u.value} value={u.value}>{u.label}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onCerrar}
              className="flex-1 border border-slate-200 text-slate-600 py-2.5 rounded-xl hover:bg-slate-50 transition-colors text-sm"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={guardando}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 text-white py-2.5 rounded-xl transition-colors text-sm font-semibold"
            >
              {guardando ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
