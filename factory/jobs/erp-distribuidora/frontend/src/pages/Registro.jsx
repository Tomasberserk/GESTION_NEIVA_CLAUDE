import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Registro() {
  const { registrar } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    nombre_comercial: '',
    nit_o_cedula: '',
    email: '',
    password: '',
    rol: 'admin',
  })
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 8) {
      setError('La contraseña debe tener mínimo 8 caracteres')
      return
    }
    setCargando(true)
    try {
      await registrar(form)
      navigate('/dashboard')
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  const set = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 w-full max-w-sm p-8">
        <div className="text-center mb-8">
          <p className="text-3xl mb-2">🏭</p>
          <h1 className="text-xl font-bold text-slate-900">Registrar Distribuidora</h1>
          <p className="text-sm text-slate-500 mt-1">Crea tu cuenta de administrador</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Razón social</label>
            <input
              type="text"
              required
              value={form.nombre_comercial}
              onChange={set('nombre_comercial')}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400"
              placeholder="Distribuidora Mayorista S.A.S."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">NIT o Cédula</label>
            <input
              type="text"
              required
              value={form.nit_o_cedula}
              onChange={set('nit_o_cedula')}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400"
              placeholder="860123456-7"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={set('email')}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400"
              placeholder="admin@distribuidora.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Contraseña</label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={set('password')}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400"
              placeholder="Mínimo 8 caracteres"
            />
          </div>
          <button
            type="submit"
            disabled={cargando}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-medium text-sm transition-colors"
          >
            {cargando ? 'Registrando...' : 'Crear cuenta'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-indigo-600 hover:underline font-medium">
            Ingresar
          </Link>
        </p>
      </div>
    </div>
  )
}
