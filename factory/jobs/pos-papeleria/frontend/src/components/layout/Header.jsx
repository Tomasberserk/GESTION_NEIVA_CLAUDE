import { LogOut, Menu } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

export default function Header({ onMenuToggle }) {
  const { usuario, logout } = useAuth()

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-4 sm:px-6 shrink-0">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          aria-label="Abrir menú"
          className="text-slate-400 hover:text-slate-700 transition-colors md:hidden"
        >
          <Menu size={22} />
        </button>
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right hidden sm:block">
          <p className="text-xs text-slate-500 leading-none">
            {usuario?.rol === 'admin' ? 'Administrador' : 'Cajero'}
          </p>
          <p className="text-sm font-medium text-slate-700 truncate max-w-[180px]">
            {usuario?.email ?? ''}
          </p>
        </div>
        <button
          onClick={logout}
          title="Cerrar sesión"
          className="flex items-center gap-1.5 text-slate-400 hover:text-red-500 transition-colors text-sm"
        >
          <LogOut size={17} />
        </button>
      </div>
    </header>
  )
}
