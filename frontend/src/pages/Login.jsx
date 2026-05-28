import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
      navigate('/inventario', { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f8f9fa] flex flex-col items-center justify-center p-4 font-sans">
      <div className="w-full max-w-[340px]">
        <div className="text-center mb-10">
          <div className="text-6xl mb-4">📦</div>
          <h1 className="text-[28px] font-extrabold text-[#1a1f2c] tracking-tight mb-1">TiendAppS</h1>
          <p className="text-[15px] text-slate-500 font-medium">Acceso Administrativo</p>
        </div>

        <form onSubmit={enviar} className="space-y-5">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-2xl text-sm text-center font-medium border border-red-100">
              {error}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="block text-[11px] font-bold text-[#475569] uppercase tracking-widest ml-1">
              Correo Electrónico
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={cambiar}
              required
              autoComplete="email"
              placeholder="nombre@empresa.com"
              className="w-full bg-white border border-slate-200/80 rounded-2xl px-4 py-3.5 text-[15px] text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#10b981]/20 focus:border-[#10b981] transition-all shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)]"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-[11px] font-bold text-[#475569] uppercase tracking-widest ml-1">
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
              className="w-full bg-white border border-slate-200/80 rounded-2xl px-4 py-3.5 text-[15px] text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#10b981]/20 focus:border-[#10b981] transition-all shadow-[0_2px_10px_-4px_rgba(0,0,0,0.05)]"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={cargando}
              className="w-full bg-[#10b981] hover:bg-[#059669] disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold text-[15px] py-4 rounded-2xl transition-all shadow-sm hover:shadow active:scale-[0.98]"
            >
              {cargando ? 'Ingresando...' : 'Entrar al Panel'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
