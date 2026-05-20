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
      navigate('/ventas', { replace: true })
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  const inputCls = 'w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition-all'
  const labelCls = 'block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5'

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-[#1e1b4b] text-2xl mb-4 shadow-lg">
            ✏️
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Registrar empresa</h1>
          <p className="text-sm text-slate-500 mt-1">Crea la cuenta de administrador</p>
        </div>

        <form onSubmit={handleRegistro} className="space-y-4">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-xl text-sm text-center border border-red-100">
              {error}
            </div>
          )}

          <div>
            <label className={labelCls}>Nombre comercial</label>
            <input type="text" name="nombre_comercial" value={form.nombre_comercial}
              onChange={cambiar} required placeholder="Papelería El Estudiante"
              className={inputCls} />
          </div>

          <div>
            <label className={labelCls}>NIT o Cédula</label>
            <input type="text" name="nit_o_cedula" value={form.nit_o_cedula}
              onChange={cambiar} required placeholder="900123456-1"
              className={inputCls} />
          </div>

          <div>
            <label className={labelCls}>Correo electrónico</label>
            <input type="email" name="email" value={form.email}
              onChange={cambiar} required autoComplete="email"
              placeholder="admin@empresa.com" className={inputCls} />
          </div>

          <div>
            <label className={labelCls}>
              Contraseña{' '}
              <span className="text-slate-400 font-normal normal-case tracking-normal">
                (mín. 8 caracteres)
              </span>
            </label>
            <input type="password" name="password" value={form.password}
              onChange={cambiar} required minLength={8} autoComplete="new-password"
              placeholder="••••••••" className={inputCls} />
          </div>

          <button
            type="submit"
            disabled={cargando}
            className="w-full bg-[#1e1b4b] hover:bg-indigo-900 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-semibold py-3.5 rounded-xl transition-all active:scale-[0.98] mt-2 text-sm"
          >
            {cargando ? 'Creando cuenta...' : 'Crear cuenta'}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-8">
          ¿Ya tienes cuenta?{' '}
          <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors">
            Iniciar sesión
          </Link>
        </p>
      </div>
    </div>
  )
}
