import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)

  const cambiar = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const enviar = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError(null)
    try {
      await login(form.email, form.password)
      navigate('/ventas', { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  const inputCls = 'w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-all'

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-[340px]">

        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#1e1b4b] text-3xl mb-5 shadow-lg">
            ✏️
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">POS Papelería</h1>
          <p className="text-sm text-slate-500 mt-1">Sistema de punto de venta</p>
        </div>

        <form onSubmit={enviar} className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-xl text-sm text-center border border-red-100">
              {error}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide ml-0.5">
              Correo electrónico
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={cambiar}
              required
              autoComplete="email"
              placeholder="usuario@empresa.com"
              className={inputCls}
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide ml-0.5">
              Contraseña
            </label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={cambiar}
              required
              autoComplete="current-password"
              placeholder="••••••••"
              className={inputCls}
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={cargando}
              className="w-full bg-[#1e1b4b] hover:bg-indigo-900 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold text-sm py-3.5 rounded-xl transition-all active:scale-[0.98]"
            >
              {cargando ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </button>
          </div>
        </form>

        <p className="text-center text-sm text-slate-500 mt-8">
          ¿Sin cuenta?{' '}
          <Link to="/registro" className="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors">
            Registrar empresa
          </Link>
        </p>
      </div>
    </div>
  )
}
