import { Bell, User, Menu, LogOut, ShoppingCart } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { useCart } from '../../context/CartContext'
import { isAdmin } from '../../utils/permissions'

export default function Header({ onMenuToggle }) {
  const { usuario, logout } = useAuth()
  const { carrito, setCarritoAbierto } = useCart()
  const esAdmin = isAdmin(usuario)
  const nombreMostrar = usuario?.nombre?.trim() || usuario?.email?.split('@')[0] || 'Usuario'
  const rolTexto = esAdmin ? 'Administrador' : 'Cajero'

  return (
    <header className="h-14 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4 sm:px-6 shrink-0">
      <div className="flex items-center gap-3">
        {/* Hamburguesa — solo visible en mobile */}
        <button
          onClick={onMenuToggle}
          aria-label="Abrir menú"
          className="text-slate-400 hover:text-white transition-colors md:hidden"
        >
          <Menu size={22} />
        </button>

        <div className="flex items-center gap-2">
          <span className="text-white font-semibold text-lg tracking-tight">
            Gestión Neiva
          </span>
          <span className="hidden md:inline-block text-slate-500 text-xs font-mono">
            v1.0
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2.5 sm:gap-4">
        {/* Botón permanente del Carrito / Caja Registradora */}
        <button
          type="button"
          onClick={() => setCarritoAbierto((prev) => !prev)}
          className="relative flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-xl text-xs font-bold transition-all shadow-sm active:scale-95"
          title="Abrir mostrador de ventas"
        >
          <ShoppingCart size={16} />
          <span className="hidden sm:inline">Caja / Mostrador</span>
          {carrito.length > 0 && (
            <span className="ml-1 px-1.5 py-0.5 rounded-full bg-white text-emerald-800 text-[10px] font-black leading-none">
              {carrito.length}
            </span>
          )}
        </button>

        {/* Identidad del usuario con badge sutil */}
        <div className="flex items-center gap-2 text-slate-300 text-sm">
          <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-slate-200 text-xs font-bold">
            {nombreMostrar.charAt(0).toUpperCase()}
          </div>
          <div className="hidden sm:flex flex-col text-left">
            <span className="font-medium text-slate-200 truncate max-w-[150px] leading-tight">
              {nombreMostrar}
            </span>
            <span
              className={`text-[10px] font-medium leading-none mt-0.5 px-1.5 py-0.5 rounded w-fit ${
                esAdmin
                  ? 'bg-violet-900/60 text-violet-300 border border-violet-700/50'
                  : 'bg-emerald-900/60 text-emerald-300 border border-emerald-700/50'
              }`}
            >
              {rolTexto}
            </span>
          </div>
        </div>

        {/* Botón de cerrar sesión */}
        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-700/50 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ml-1"
          title="Cerrar sesión"
        >
          <LogOut size={16} />
          <span className="hidden md:inline">Salir</span>
        </button>
      </div>
    </header>
  )
}
