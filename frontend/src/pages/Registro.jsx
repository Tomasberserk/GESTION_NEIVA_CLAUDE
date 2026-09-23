import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Store, ArrowLeft, Loader2, CheckCircle2, Shield } from 'lucide-react'

export default function Registro() {
  const { registrar } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    nombre_comercial: '',
    nit_o_cedula: '',
    email: '',
    password: '',
  })

  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  const cambiar = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    if (error) setError(null)
  }

  const validarFormulario = () => {
    if (!form.nombre_comercial.trim()) {
      return 'Por favor ingresa el nombre de tu tienda o negocio.'
    }
    if (!form.nit_o_cedula.trim()) {
      return 'Por favor ingresa tu número de cédula o NIT.'
    }
    if (!form.email.trim() || !form.email.includes('@')) {
      return 'Por favor ingresa un correo electrónico válido.'
    }
    if (form.password.length < 8) {
      return 'La contraseña debe tener al menos 8 caracteres.'
    }
    const tieneMayus = /[A-Z]/.test(form.password)
    const tieneMinus = /[a-z]/.test(form.password)
    const tieneNum = /[0-9]/.test(form.password)
    const tieneEspecial = /[!@#$%^&*(),.?":{}|<>]/.test(form.password)

    if (!tieneMayus || !tieneMinus || !tieneNum || !tieneEspecial) {
      return 'La contraseña debe incluir al menos una mayúscula, una minúscula, un número y un símbolo (ej: Clave2026!).'
    }
    return null
  }

  const enviar = async (e) => {
    e.preventDefault()
    const errorValidacion = validarFormulario()
    if (errorValidacion) {
      setError(errorValidacion)
      return
    }

    setCargando(true)
    setError(null)

    try {
      const payload = {
        nombre_comercial: form.nombre_comercial.trim(),
        nit_o_cedula: form.nit_o_cedula.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        rol: 'admin',
      }
      await registrar(payload)
      // Guardar bandera para que el OnboardingModal reconozca primer ingreso
      localStorage.setItem('onboarding_pendiente', 'true')
      navigate('/dashboard?bienvenida=1', { replace: true })
    } catch (err) {
      setError(err.message || 'Ocurrió un error al registrar la tienda. Intenta nuevamente.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#fafaf9] flex flex-col justify-between p-4 sm:p-6 font-sans">
      <div className="max-w-md w-full mx-auto pt-4 sm:pt-8">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-emerald-700 transition-colors mb-6"
        >
          <ArrowLeft size={16} />
          <span>Volver a la página principal</span>
        </Link>

        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center mx-auto shadow-sm">
              <Store size={24} />
            </div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Registra tu negocio
            </h1>
            <p className="text-xs sm:text-sm text-slate-500">
              Crea tu cuenta y comienza a configurar tu tienda en Gestión Neiva.
            </p>
          </div>

          {error && (
            <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs leading-relaxed">
              {error}
            </div>
          )}

          <form onSubmit={enviar} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Nombre de la tienda o negocio
              </label>
              <input
                type="text"
                name="nombre_comercial"
                value={form.nombre_comercial}
                onChange={cambiar}
                required
                placeholder="Ej: Tienda La Floresta"
                className="w-full bg-[#fafaf9] border border-slate-200 rounded-xl px-3.5 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Cédula o NIT del propietario
              </label>
              <input
                type="text"
                name="nit_o_cedula"
                value={form.nit_o_cedula}
                onChange={cambiar}
                required
                placeholder="Ej: 1075234567 o 901234567-1"
                className="w-full bg-[#fafaf9] border border-slate-200 rounded-xl px-3.5 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />
              <span className="text-[11px] text-slate-400 mt-1 block">
                Identificación para el registro exclusivo de tu negocio.
              </span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Correo electrónico
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
              <span className="text-[11px] text-slate-400 mt-1 block">
                Este correo será tu usuario para entrar a la tienda.
              </span>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Contraseña segura
              </label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={cambiar}
                required
                autoComplete="new-password"
                placeholder="Mínimo 8 caracteres (letras, número y símbolo)"
                className="w-full bg-[#fafaf9] border border-slate-200 rounded-xl px-3.5 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition"
              />
              <span className="text-[11px] text-slate-400 mt-1 block leading-tight">
                Incluye al menos una mayúscula, un número y un símbolo (ej: Clave2026!).
              </span>
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={cargando}
                className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold text-sm py-3.5 rounded-xl transition-all shadow-sm active:scale-98 flex items-center justify-center gap-2"
              >
                {cargando ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    <span>Creando tu tienda...</span>
                  </>
                ) : (
                  'Crear mi Tienda'
                )}
              </button>
            </div>
          </form>

          <div className="pt-4 border-t border-slate-100 text-center text-xs text-slate-500 space-y-2">
            <p>
              ¿Ya tienes una cuenta registrada?{' '}
              <Link to="/login" className="text-emerald-700 font-bold hover:underline">
                Inicia sesión aquí
              </Link>
            </p>
            <div className="flex items-center justify-center gap-1 text-[11px] text-slate-400 pt-1">
              <Shield size={12} className="text-emerald-600" />
              <span>Tu información pertenece a tu negocio y permanece separada.</span>
            </div>
          </div>
        </div>
      </div>

      <div className="text-center text-xs text-slate-400 py-6">
        Gestión Neiva · Apoyando el comercio popular y local
      </div>
    </div>
  )
}
