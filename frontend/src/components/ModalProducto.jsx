import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import BarcodeScanner from './BarcodeScanner'

// Campos genéricos (sin codigo_barras, que se renderiza aparte con el escáner)
const CAMPOS = [
  { label: 'Nombre', name: 'nombre', type: 'text', required: true },
  { label: 'Precio costo', name: 'precio_costo', type: 'number', step: '0.01', min: '0' },
  { label: 'Precio venta', name: 'precio_venta', type: 'number', step: '0.01', min: '0' },
  { label: 'Stock',        name: 'cantidad_actual', type: 'number', step: '0.001', min: '0' },
]

const UNIDADES = [
  { value: 'unidad', label: 'Unidad' },
  { value: 'gramo',  label: 'Gramo' },
  { value: 'libra',  label: 'Libra' },
  { value: 'kilo',   label: 'Kilo' },
]

const CATEGORIAS = [
  'Bebidas', 'Snacks', 'Aseo', 'Lacteos', 'Limpieza', 'Panaderia',
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
    categoria: '',
    foto_url: '',
    empresa_id: usuario?.empresa_id ?? '',
  })
  const [error,      setError]      = useState(null)
  const [guardando,  setGuardando]  = useState(false)
  const [escaneando, setEscaneando] = useState(false)

  useEffect(() => {
    if (producto) {
      setForm({
        nombre:            producto.nombre,
        codigo_barras:     producto.codigo_barras,
        precio_costo:      producto.precio_costo,
        precio_venta:      producto.precio_venta,
        cantidad_actual:   producto.cantidad_actual,
        unidad_medida:     producto.unidad_medida     ?? 'unidad',
        fecha_vencimiento: producto.fecha_vencimiento ? producto.fecha_vencimiento.split('T')[0] : '',
        categoria:         producto.categoria         ?? '',
        foto_url:          producto.foto_url          ?? '',
        empresa_id:        producto.empresa_id,
      })
    }
  }, [producto])

  const cambiar = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const alEscanear = (codigo) => {
    setForm(prev => ({ ...prev, codigo_barras: codigo }))
    setEscaneando(false)
  }

  const guardar = async (e) => {
    e.preventDefault()
    setGuardando(true)
    setError(null)
    try {
      const payload = {
        ...form,
        precio_costo:      parseFloat(form.precio_costo)    || 0,
        precio_venta:      parseFloat(form.precio_venta)    || 0,
        cantidad_actual:   parseFloat(form.cantidad_actual) || 0,
        fecha_vencimiento: form.fecha_vencimiento || null,
        categoria:         form.categoria         || null,
        foto_url:          form.foto_url          || null,
      }
      await onGuardar(payload)
      onCerrar()
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  const cls = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400'

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">

        {/* Encabezado */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="font-bold text-lg">
            {esEdicion ? 'Editar producto' : 'Nuevo producto'}
          </h2>
          <button
            type="button"
            onClick={onCerrar}
            className="text-gray-400 hover:text-gray-700 text-xl leading-none"
          >
            ✕
          </button>
        </div>

        <form onSubmit={guardar} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error}</div>
          )}

          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              name="nombre"
              value={form.nombre}
              onChange={cambiar}
              required={!esEdicion}
              className={cls}
              type="text"
            />
          </div>

          {/* Código de barras + botón cámara */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Código de barras
            </label>
            <div className="flex gap-2">
              <input
                name="codigo_barras"
                value={form.codigo_barras}
                onChange={cambiar}
                type="text"
                placeholder="Escribe o escanea"
                className={`${cls} flex-1`}
              />
              <button
                type="button"
                onClick={() => setEscaneando(prev => !prev)}
                title={escaneando ? 'Cerrar cámara' : 'Escanear con cámara'}
                className={`shrink-0 px-3 rounded-lg border text-lg transition-colors ${
                  escaneando
                    ? 'bg-violet-100 border-violet-400 text-violet-700'
                    : 'border-gray-300 text-gray-500 hover:border-violet-400 hover:text-violet-600'
                }`}
              >
                📷
              </button>
            </div>

            {/* Visor de cámara — aparece justo debajo del input */}
            {escaneando && (
              <BarcodeScanner
                onScan={alEscanear}
                onClose={() => setEscaneando(false)}
              />
            )}
          </div>

          {/* Precio costo, Precio venta, Stock */}
          {CAMPOS.slice(1).map(({ label, name, required, ...rest }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                name={name}
                value={form[name]}
                onChange={cambiar}
                required={required && !esEdicion}
                className={cls}
                {...rest}
              />
            </div>
          ))}

          {/* Unidad de medida */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Unidad de medida
            </label>
            <select name="unidad_medida" value={form.unidad_medida} onChange={cambiar} className={`${cls} bg-white`}>
              {UNIDADES.map(u => (
                <option key={u.value} value={u.value}>{u.label}</option>
              ))}
            </select>
          </div>

          {/* Categoría */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Categoría <span className="text-gray-400 font-normal">(opcional)</span>
            </label>
            <select name="categoria" value={form.categoria} onChange={cambiar} className={`${cls} bg-white`}>
              <option value="">Sin categoría</option>
              {CATEGORIAS.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Fecha de vencimiento */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha de vencimiento <span className="text-gray-400 font-normal">(opcional)</span>
            </label>
            <input
              type="date"
              name="fecha_vencimiento"
              value={form.fecha_vencimiento}
              onChange={cambiar}
              className={cls}
            />
          </div>

          {/* Foto URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL de la Imagen <span className="text-gray-400 font-normal">(opcional)</span>
            </label>
            <input
              type="url"
              name="foto_url"
              value={form.foto_url}
              onChange={cambiar}
              placeholder="https://ejemplo.com/imagen.jpg"
              className={cls}
            />
          </div>

          {/* Acciones */}
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
