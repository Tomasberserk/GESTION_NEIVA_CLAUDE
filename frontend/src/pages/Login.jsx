import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { ArrowLeft } from 'lucide-react'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)

  const sesionExpirada = typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('expirado') === '1'

  const cambiar = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const enviar = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError(null)
    try {
      const data = await login(form.email, form.password)
      const rutaDestino = data?.usuario?.rol === 'admin' ? '/dashboard' : '/ventas'
      navigate(rutaDestino, { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#fafaf9] flex flex-col justify-between p-4 font-sans">
      <div className="w-full max-w-[360px] mx-auto pt-6">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-emerald-700 transition-colors mb-6"
        >
          <ArrowLeft size={16} />
          <span>Volver a la página principal</span>
        </Link>

        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
          <div className="text-center">
            <div className="text-5xl mb-3">📦</div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight mb-1">Gestión Neiva</h1>
            <p className="text-xs text-slate-500 font-medium">Ingreso a tu tienda y punto de venta</p>
          </div>

          <form onSubmit={enviar} className="space-y-4">
            {sesionExpirada && !error && (
              <div className="bg-amber-50 text-amber-800 p-3 rounded-2xl text-xs text-center font-medium border border-amber-200 leading-relaxed">
                ⚠️ Tu sesión terminó por seguridad o inactividad. Por favor inicia sesión nuevamente.
              </div>
            )}

            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-2xl text-xs text-center font-medium border border-red-100">
                {error}
              </div>
            )}

            <div className="space-y-1">
              <label className="block text-xs font-bold text-slate-700">
                Correo Electrónico
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={cambiar}
                required
                autoComplete="email"
                placeholder="nombre@tutienda.com"
                className="w-full bg-[#fafaf9] border border-slate-200 rounded-xl px-3.5 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />
            </div>

            <div className="space-y-1">
              <label className="block text-xs font-bold text-slate-700">
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
                className="w-full bg-[#fafaf9] border border-slate-200 rounded-xl px-3.5 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={cargando}
                className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold text-sm py-3.5 rounded-xl transition-all shadow-sm active:scale-98"
              >
                {cargando ? 'Ingresando...' : 'Entrar a mi Tienda'}
              </button>
            </div>
          </form>

          <div className="pt-4 border-t border-slate-100 text-center text-xs text-slate-500 space-y-2">
            <p>
              ¿Aún no has registrado tu tienda?{' '}
              <Link to="/registro" className="text-emerald-700 font-bold hover:underline">
                Crear cuenta aquí
              </Link>
            </p>
          </div>
        </div>
      </div>

      <div className="text-center text-xs text-slate-400 py-6">
        Gestión Neiva · Punto de venta y administración para el comercio local
      </div>
    </div>
  )
}
