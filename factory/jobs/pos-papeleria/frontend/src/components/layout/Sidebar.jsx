import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  BarChart3,
  X,
} from 'lucide-react'
import { cn } from '../../lib/utils'

const navItems = [
  { to: '/dashboard',  label: 'Dashboard',       icon: LayoutDashboard },
  { to: '/ventas',     label: 'Punto de Venta',  icon: ShoppingCart },
  { to: '/inventario', label: 'Inventario',      icon: Package },
  { to: '/reportes',   label: 'Reportes',        icon: BarChart3 },
]

export default function Sidebar({ abierto, onCerrar }) {
  return (
    <>
      {abierto && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onCerrar}
        />
      )}

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-60 flex flex-col h-full transition-transform duration-300',
          'md:relative md:z-auto md:translate-x-0 md:shrink-0',
          abierto ? 'translate-x-0' : '-translate-x-full',
        )}
        style={{ backgroundColor: '#1e1b4b' }}
      >
        {/* Brand */}
        <div className="h-14 flex items-center justify-between px-5 border-b border-white/10 shrink-0">
          <div className="flex items-center gap-2.5">
            <span className="text-xl">✏️</span>
            <span className="text-white font-semibold text-sm tracking-tight leading-tight">
              POS Papelería
            </span>
          </div>
          <button
            onClick={onCerrar}
            aria-label="Cerrar menú"
            className="text-indigo-300 hover:text-white transition-colors md:hidden"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onCerrar}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all',
                  isActive
                    ? 'bg-indigo-500 text-white shadow-sm shadow-indigo-900'
                    : 'text-indigo-200 hover:bg-white/10 hover:text-white',
                )
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-white/10 shrink-0">
          <p className="text-indigo-400 text-[11px] font-medium uppercase tracking-wider">
            Sistema POS · Basic
          </p>
        </div>
      </aside>
    </>
  )
}
