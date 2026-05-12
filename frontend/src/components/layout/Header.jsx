import { Bell, User, Menu } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export default function Header({ onMenuToggle }) {
  const { usuario, logout } = useAuth()

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

        <span className="text-white font-semibold text-lg tracking-tight">
          Gestión Neiva
        </span>
      </div>

      <div className="flex items-center gap-4">
        <button className="text-slate-400 hover:text-white transition-colors">
          <Bell size={18} />
        </button>
        <button
          onClick={logout}
          className="flex items-center gap-2 text-slate-300 hover:text-white text-sm transition-colors"
          title="Cerrar sesión"
        >
          <User size={18} />
          {/* Email oculto en pantallas muy pequeñas para no achicar el header */}
          <span className="hidden sm:block truncate max-w-[140px]">
            {usuario?.email ?? 'Usuario'}
          </span>
        </button>
      </div>
    </header>
  )
}
