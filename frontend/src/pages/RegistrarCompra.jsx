import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Plus, Trash2, ShoppingCart, ChevronDown, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useProveedores } from '../hooks/useProveedores'
import { useProductos } from '../hooks/useProductos'
import { useCompras } from '../hooks/useCompras'

const fmt = (n) => Number(n ?? 0).toLocaleString('es-CO', { maximumFractionDigits: 0 })

const METODOS_PAGO = ['EFECTIVO', 'CREDITO', 'TRANSFERENCIA']

function BuscadorProducto({ onAgregar }) {
  const { productos, cargando, cargar } = useProductos()
  const [q, setQ] = useState('')
  const [abierto, setAbierto] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const t = setTimeout(() => { if (q) { cargar(q); setAbierto(true) } else setAbierto(false) }, 300)
    return () => clearTimeout(t)
  }, [q, cargar])

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setAbierto(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const seleccionar = (p) => {
    onAgregar(p)
    setQ('')
    setAbierto(false)
  }

  return (
    <div ref={ref} className="relative">
      <div className="relative">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Buscar producto para agregar..."
          className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
      </div>
      {abierto && (
        <div className="absolute z-10 top-full mt-1 left-0 right-0 bg-white border border-slate-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
          {cargando ? (
            <p className="p-3 text-sm text-slate-400 text-center">Buscando...</p>
          ) : productos.length === 0 ? (
            <p className="p-3 text-sm text-slate-400 text-center">Sin resultados</p>
          ) : (
            productos.map(p => (
              <button
                key={p.id}
                type="button"
                onClick={() => seleccionar(p)}
                className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-slate-50 text-left transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-slate-800">{p.nombre}</p>
                  <p className="text-xs text-slate-400">{p.codigo_barras} · stock: {Number(p.cantidad_actual)}</p>
                </div>
                <p className="text-xs text-slate-500 shrink-0 ml-4">${fmt(p.precio_costo)}</p>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default function RegistrarCompra() {
  const navigate = useNavigate()
  const { proveedores, cargar: cargarProveedores } = useProveedores()
  const { registrar } = useCompras()

  const [proveedorId, setProveedorId] = useState('')
  const [numeroFactura, setNumeroFactura] = useState('')
  const [metodoPago, setMetodoPago] = useState('EFECTIVO')
  const [fechaVencimiento, setFechaVencimiento] = useState('')
  const [items, setItems] = useState([])
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState('')
  const [exito, setExito] = useState(null)

  useEffect(() => { cargarProveedores() }, [cargarProveedores])

  const agregarProducto = useCallback((producto) => {
    setItems(prev => {
      const existe = prev.find(i => i.producto_id === producto.id)
      if (existe) {
        return prev.map(i => i.producto_id === producto.id
          ? { ...i, cantidad: i.cantidad + 1 }
          : i)
      }
      return [...prev, {
        producto_id: producto.id,
        nombre: producto.nombre,
        cantidad: 1,
        precio_costo: producto.precio_costo ?? 0,
      }]
    })
  }, [])

  const actualizarItem = (idx, field, value) => {
    setItems(prev => prev.map((item, i) => i === idx ? { ...item, [field]: value } : item))
  }

  const eliminarItem = (idx) => {
    setItems(prev => prev.filter((_, i) => i !== idx))
  }

  const total = items.reduce((acc, i) => acc + (parseFloat(i.cantidad) || 0) * (parseFloat(i.precio_costo) || 0), 0)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!proveedorId) { setError('Selecciona un proveedor'); return }
    if (items.length === 0) { setError('Agrega al menos un producto'); return }
    if (metodoPago === 'CREDITO' && !fechaVencimiento) {
      setError('La fecha de vencimiento es obligatoria para compras a crédito')
      return
    }
    for (const item of items) {
      if (!item.cantidad || parseFloat(item.cantidad) <= 0) {
        setError(`Cantidad inválida para \"${item.nombre}\"`)
        return
      }
      if (!item.precio_costo || parseFloat(item.precio_costo) <= 0) {
        setError(`Precio de costo inválido para \"${item.nombre}\"`)
        return
      }
    }

    setEnviando(true)
    try {
      const payload = {
        proveedor_id: proveedorId,
        numero_factura: numeroFactura || null,
        metodo_pago: metodoPago,
        fecha_vencimiento: metodoPago === 'CREDITO' ? new Date(fechaVencimiento).toISOString() : null,
        items: items.map(i => ({
          producto_id: i.producto_id,
          cantidad: parseFloat(i.cantidad),
          precio_costo: parseFloat(i.precio_costo),
        })),
      }
      const resultado = await registrar(payload)
      setExito(resultado)
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  if (exito) {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl border border-slate-200 p-8 max-w-md w-full text-center">
          <CheckCircle2 size={48} className="text-emerald-500 mx-auto mb-4" />
          <h2 className="text-lg font-bold text-slate-900 mb-2">Compra registrada</h2>
          <p className="text-sm text-slate-600 mb-1">Factura: <strong>{exito.numero_factura || 'Sin número'}</strong></p>
          <p className="text-sm text-slate-600 mb-1">Total: <strong>${fmt(exito.total)}</strong></p>
          <p className="text-sm text-slate-600 mb-1">Estado: <strong>{exito.estado}</strong></p>
          {exito.cuenta_por_pagar_id && (
            <p className="text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-2 mt-3">
              Se creó una cuenta por pagar automáticamente (compra a crédito)
            </p>
          )}
          <div className="flex gap-3 mt-6">
            <button
              onClick={() => { setExito(null); setItems([]); setNumeroFactura(''); setProveedorId(''); setMetodoPago('EFECTIVO'); setFechaVencimiento('') }}
              className="flex-1 py-2.5 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Nueva compra
            </button>
            <button
              onClick={() => navigate('/compras')}
              className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-medium"
            >
              Ver historial
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto p-4 sm:p-6">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-slate-900">Registrar Compra</h1>
          <p className="text-sm text-slate-500 mt-0.5">Registra una factura de proveedor e incrementa el stock</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              {error}
            </div>
          )}

          {/* Datos del encabezado */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
            <h2 className="font-semibold text-slate-800 text-sm">Datos de la compra</h2>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Proveedor *</label>
              <div className="relative">
                <select
                  value={proveedorId}
                  onChange={e => setProveedorId(e.target.value)}
                  className="w-full appearance-none px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                >
                  <option value="">Seleccionar proveedor...</option>
                  {proveedores.map(p => (
                    <option key={p.id} value={p.id}>{p.razon_social} ({p.nit_o_cedula})</option>
                  ))}
                </select>
                <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">N° Factura proveedor</label>
                <input
                  type="text"
                  value={numeroFactura}
                  onChange={e => setNumeroFactura(e.target.value)}
                  placeholder="FAC-8973"
                  className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Método de pago *</label>
                <div className="relative">
                  <select
                    value={metodoPago}
                    onChange={e => setMetodoPago(e.target.value)}
                    className="w-full appearance-none px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-white"
                  >
                    {METODOS_PAGO.map(m => <option key={m} value={m}>{m}</option>)}
                  </select>
                  <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                </div>
              </div>
            </div>

            {metodoPago === 'CREDITO' && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Fecha de vencimiento *
                  <span className="text-xs text-amber-600 ml-1">(obligatoria para crédito)</span>
                </label>
                <input
                  type="date"
                  value={fechaVencimiento}
                  onChange={e => setFechaVencimiento(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2.5 border border-amber-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-amber-300 bg-amber-50"
                />
              </div>
            )}
          </div>

          {/* Items de la compra */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
            <h2 className="font-semibold text-slate-800 text-sm">Productos</h2>

            <BuscadorProducto onAgregar={agregarProducto} />

            {items.length === 0 ? (
              <div className="text-center py-8 text-slate-400">
                <ShoppingCart size={28} className="mx-auto mb-2" />
                <p className="text-sm">Busca y agrega productos a la compra</p>
              </div>
            ) : (
              <div className="space-y-2">
                {/* Encabezados */}
                <div className="grid grid-cols-12 gap-2 text-xs font-medium text-slate-500 px-1">
                  <span className="col-span-4">Producto</span>
                  <span className="col-span-3 text-right">Cantidad</span>
                  <span className="col-span-4 text-right">Precio costo</span>
                  <span className="col-span-1" />
                </div>
                {items.map((item, idx) => (
                  <div key={idx} className="grid grid-cols-12 gap-2 items-center bg-slate-50 rounded-xl px-3 py-2">
                    <div className="col-span-4 min-w-0">
                      <p className="text-sm font-medium text-slate-800 truncate">{item.nombre}</p>
                      <p className="text-xs text-slate-400">subtotal: ${fmt((parseFloat(item.cantidad) || 0) * (parseFloat(item.precio_costo) || 0))}</p>
                    </div>
                    <div className="col-span-3">
                      <input
                        type="number"
                        min="0.001"
                        step="any"
                        value={item.cantidad}
                        onChange={e => actualizarItem(idx, 'cantidad', e.target.value)}
                        className="w-full text-right px-2 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                      />
                    </div>
                    <div className="col-span-4">
                      <input
                        type="number"
                        min="0.01"
                        step="any"
                        value={item.precio_costo}
                        onChange={e => actualizarItem(idx, 'precio_costo', e.target.value)}
                        className="w-full text-right px-2 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                      />
                    </div>
                    <div className="col-span-1 flex justify-end">
                      <button type="button" onClick={() => eliminarItem(idx)} className="text-slate-300 hover:text-red-500 transition-colors">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}

                {/* Total */}
                <div className="flex justify-end pt-2 border-t border-slate-200">
                  <div className="text-right">
                    <p className="text-xs text-slate-500">{items.length} producto{items.length !== 1 ? 's' : ''}</p>
                    <p className="text-lg font-bold text-slate-900">${fmt(total)}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Acciones */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex-1 py-3 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={enviando || items.length === 0}
              className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-medium"
            >
              {enviando ? 'Registrando...' : `Registrar compra · $${fmt(total)}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}