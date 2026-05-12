import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

const CAMPOS = [
  { label: 'Nombre', name: 'nombre', type: 'text', required: true },
  { label: 'Código de barras', name: 'codigo_barras', type: 'text' },
  { label: 'Precio costo', name: 'precio_costo', type: 'number', step: '0.01', min: '0' },
  { label: 'Precio venta', name: 'precio_venta', type: 'number', step: '0.01', min: '0' },
  { label: 'Stock', name: 'cantidad_actual', type: 'number', step: '0.001', min: '0' },
]

const UNIDADES = [
  { value: 'unidad', label: 'Unidad' },
  { value: 'gramo',  label: 'Gramo' },
  { value: 'libra',  label: 'Libra' },
  { value: 'kilo',   label: 'Kilo' },
]

export default function ModalProducto({ producto, onGuardar, onCerrar }) {
  const { usuario } = useAuth()
  const esEdicion = Boolean(producto)

  const [form, setForm] = useState({
    nombre: '',
    codigo_barras: '',
    precio_costo: '',
    precio_venta: '',
    cantidad_actual: '',
    unidad_medida: 'unidad',
    fecha_vencimiento: '',
    empresa_id: usuario?.empresa_id ?? '',
  })
  const [error, setError] = useState(null)
  const [guardando, setGuardando] = useState(false)

  useEffect(() => {
    if (producto) {
      setForm({
        nombre: producto.nombre,
        codigo_barras: producto.codigo_barras,
        precio_costo: producto.precio_costo,
        precio_venta: producto.precio_venta,
        cantidad_actual: producto.cantidad_actual,
        unidad_medida: producto.unidad_medida ?? 'unidad',
        fecha_vencimiento: producto.fecha_vencimiento ?? '',
        empresa_id: producto.empresa_id,
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
        precio_costo: parseFloat(form.precio_costo) || 0,
        precio_venta: parseFloat(form.precio_venta) || 0,
        cantidad_actual: parseFloat(form.cantidad_actual) || 0,
        fecha_vencimiento: form.fecha_vencimiento || null,
      }
      await onGuardar(payload)
      onCerrar()
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  const inputClass = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400'

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="font-bold text-lg">
            {esEdicion ? 'Editar producto' : 'Nuevo producto'}
          </h2>
          <button onClick={onCerrar} className="text-gray-400 hover:text-gray-700 text-xl leading-none">
            ✕
          </button>
        </div>

        <form onSubmit={guardar} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
          )}

          {CAMPOS.map(({ label, name, required, ...rest }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                name={name}
                value={form[name]}
                onChange={cambiar}
                required={required && !esEdicion}
                className={inputClass}
                {...rest}
              />
            </div>
          ))}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Unidad de medida
            </label>
            <select
              name="unidad_medida"
              value={form.unidad_medida}
              onChange={cambiar}
              className={`${inputClass} bg-white`}
            >
              {UNIDADES.map(u => (
                <option key={u.value} value={u.value}>{u.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha de vencimiento
              <span className="text-gray-400 font-normal ml-1">(opcional)</span>
            </label>
            <input
              type="date"
              name="fecha_vencimiento"
              value={form.fecha_vencimiento}
              onChange={cambiar}
              className={inputClass}
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onCerrar}
              className="flex-1 border border-gray-300 text-gray-700 py-2.5 rounded-lg hover:bg-gray-50 transition-colors text-sm"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={guardando}
              className="flex-1 bg-violet-600 hover:bg-violet-700 disabled:bg-gray-200 text-white py-2.5 rounded-lg transition-colors text-sm font-medium"
            >
              {guardando ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
