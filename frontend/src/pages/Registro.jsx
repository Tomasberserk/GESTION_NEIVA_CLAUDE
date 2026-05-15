import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Registro() {
  const { registrar } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    nombre_comercial: '',
    nit_o_cedula: '',
    email: '',
    password: '',
  })
  const [error, setError] = useState(null)
  const [cargando, setCargando] = useState(false)

  const cambiar = (e) => setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))

  const handleRegistro = async (e) => {
    e.preventDefault()
    setCargando(true)
    setError(null)
    try {
      await registrar({ ...form, rol: 'admin' })
      navigate('/dashboard', { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex items-center justify-center p-6 font-sans">
      
      <div className="w-full max-w-sm flex flex-col items-center">
        
        <div className="text-center mb-8">
          <div className="text-6xl mb-4 drop-shadow-sm">📝</div>
          <h1 className="text-3xl font-bold text-[#111827] tracking-tight">Crear cuenta</h1>
          <p className="text-[#6B7280] text-sm font-medium mt-2">
            Registra tu empresa y administrador.
          </p>
        </div>

        <form onSubmit={handleRegistro} className="w-full space-y-5">
          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-[15px] text-sm text-center border border-red-100">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="block text-xs font-bold text-[#374151] uppercase tracking-wider ml-1">
              Nombre comercial
            </label>
            <input
              type="text"
              name="nombre_comercial"
              value={form.nombre_comercial}
              onChange={cambiar}
              required
              placeholder="Tienda La Esperanza"
              className="w-full bg-white border border-[#E5E7EB] rounded-[20px] px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-[#10B981] focus:border-transparent transition-all shadow-sm"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-[#374151] uppercase tracking-wider ml-1">
              NIT o Cédula
            </label>
            <input
              type="text"
              name="nit_o_cedula"
              value={form.nit_o_cedula}
              onChange={cambiar}
              required
              placeholder="900123456-1"
              className="w-full bg-white border border-[#E5E7EB] rounded-[20px] px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-[#10B981] focus:border-transparent transition-all shadow-sm"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-[#374151] uppercase tracking-wider ml-1">
              Correo Electrónico
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={cambiar}
              required
              autoComplete="email"
              placeholder="admin@empresa.com"
              className="w-full bg-white border border-[#E5E7EB] rounded-[20px] px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-[#10B981] focus:border-transparent transition-all shadow-sm"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-[#374151] uppercase tracking-wider ml-1">
              Contraseña <span className="text-[#9CA3AF] font-normal normal-case tracking-normal">(mín. 8 caracteres)</span>
            </label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={cambiar}
              required
              minLength={8}
              autoComplete="new-password"
              placeholder="••••••••"
              className="w-full bg-white border border-[#E5E7EB] rounded-[20px] px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-[#10B981] focus:border-transparent transition-all shadow-sm"
            />
          </div>

          <button
            type="submit"
            disabled={cargando}
            className="w-full bg-[#10B981] hover:bg-[#059669] disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-bold py-4 rounded-[20px] transition-all shadow-lg shadow-emerald-100 active:scale-[0.97] mt-6"
          >
            {cargando ? 'Creando cuenta...' : 'Crear cuenta'}
          </button>
        </form>

        <footer className="mt-10 text-center">
          <p className="text-sm text-[#9CA3AF]">
            ¿Ya tienes cuenta?{' '}
            <Link to="/login" className="text-[#3B82F6] hover:text-[#2563EB] font-bold transition-colors">
              Ingresar
            </Link>
          </p>
        </footer>
      </div>
    </div>
  )
}
