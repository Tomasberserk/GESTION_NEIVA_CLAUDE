import { useState, useEffect, useCallback } from 'react'
import { Search, Plus, Users, Pencil, Trash2, X, Phone, Mail, MapPin } from 'lucide-react'
import { useProveedores } from '../hooks/useProveedores'

function ModalProveedor({ proveedor, onGuardar, onCerrar }) {
  const [form, setForm] = useState({
    nit_o_cedula: proveedor?.nit_o_cedula ?? '',
    razon_social: proveedor?.razon_social ?? '',
    contacto_nombre: proveedor?.contacto_nombre ?? '',
    telefono: proveedor?.telefono ?? '',
    email: proveedor?.email ?? '',
    direccion: proveedor?.direccion ?? '',
  })
  const [error, setError] = useState('')
  const [guardando, setGuardando] = useState(false)

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setGuardando(true)
    try {
      await onGuardar(form)
      onCerrar()
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  const campos = [
    { label: 'NIT o Cédula', key: 'nit_o_cedula', required: true, placeholder: '890102030-9' },
    { label: 'Razón social', key: 'razon_social', required: true, placeholder: 'Distribuidora Nacional S.A.S.' },
    { label: 'Contacto', key: 'contacto_nombre', placeholder: 'Carlos Mendoza' },
    { label: 'Teléfono', key: 'telefono', placeholder: '+57 315 123 4567' },
    { label: 'Email', key: 'email', type: 'email', placeholder: 'ventas@proveedor.com' },
    { label: 'Dirección', key: 'direccion', placeholder: 'Calle 10 # 4-50, Bogotá' },
  ]

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 sticky top-0 bg-white rounded-t-2xl">
          <h2 className="font-semibold text-slate-900">{proveedor ? 'Editar proveedor' : 'Nuevo proveedor'}</h2>
          <button onClick={onCerrar} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <p className="text-sm text-red-600 bg-red-50 rounded-lg p-3">{error}</p>}
          {campos.map(({ label, key, required, type, placeholder }) => (
            <div key={key}>
              <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
              <input
                type={type || 'text'}
                required={required}
                value={form[key]}
                onChange={set(key)}
                placeholder={placeholder}
                className="w-full px-3 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
              />
            </div>
          ))}
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

export default function Proveedores() {
  const { proveedores, total, cargando, cargar, crear, actualizar, eliminar } = useProveedores()
  const [busqueda, setBusqueda] = useState('')
  const [modalAbierto, setModalAbierto] = useState(false)
  const [editando, setEditando] = useState(null)

  const buscar = useCallback(() => { cargar(busqueda) }, [cargar, busqueda])

  useEffect(() => {
    const t = setTimeout(buscar, 300)
    return () => clearTimeout(t)
  }, [busqueda, buscar])

  useEffect(() => { cargar() }, [cargar])

  const guardar = async (payload) => {
    if (editando) await actualizar(editando.id, payload)
    else await crear(payload)
    cargar(busqueda)
  }

  const handleEliminar = async (p) => {
    if (!confirm(`¿Desactivar a "${p.razon_social}"?\nNo podrás si tiene compras activas.`)) return
    try {
      await eliminar(p.id)
      cargar(busqueda)
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Toolbar */}
      <div className="bg-white border-b border-slate-200 px-4 sm:px-6 py-4 shrink-0">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="text-lg font-bold text-slate-900">Proveedores</h1>
            <p className="text-xs text-slate-500 mt-0.5">{total} proveedores activos</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar proveedor..."
                value={busqueda}
                onChange={e => setBusqueda(e.target.value)}
                className="pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 w-52"
              />
            </div>
            <button
              onClick={() => { setEditando(null); setModalAbierto(true) }}
              className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-medium whitespace-nowrap"
            >
              <Plus size={15} />
              <span className="hidden sm:inline">Nuevo proveedor</span>
            </button>
          </div>
        </div>
      </div>

      {/* Lista */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6">
        {cargando ? (
          <div className="flex items-center justify-center h-48">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500" />
          </div>
        ) : proveedores.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400">
            <Users size={32} className="mb-3" />
            <p className="text-sm">{busqueda ? 'Sin resultados' : 'Sin proveedores registrados'}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {proveedores.map(p => (
              <div key={p.id} className="bg-white rounded-xl border border-slate-200 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-semibold text-slate-900 text-sm">{p.razon_social}</p>
                      <span className="text-xs text-slate-400 font-mono bg-slate-100 px-2 py-0.5 rounded-md">{p.nit_o_cedula}</span>
                    </div>
                    {p.contacto_nombre && (
                      <p className="text-sm text-slate-600 mb-2">{p.contacto_nombre}</p>
                    )}
                    <div className="flex flex-wrap gap-3">
                      {p.telefono && (
                        <span className="flex items-center gap-1 text-xs text-slate-500">
                          <Phone size={11} />
                          {p.telefono}
                        </span>
                      )}
                      {p.email && (
                        <span className="flex items-center gap-1 text-xs text-slate-500">
                          <Mail size={11} />
                          {p.email}
                        </span>
                      )}
                      {p.direccion && (
                        <span className="flex items-center gap-1 text-xs text-slate-500">
                          <MapPin size={11} />
                          {p.direccion}
                        </span>
                      )}
                    </div>
                  </div>
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
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {modalAbierto && (
        <ModalProveedor
          proveedor={editando}
          onGuardar={guardar}
          onCerrar={() => setModalAbierto(false)}
        />
      )}
    </div>
  )
}
