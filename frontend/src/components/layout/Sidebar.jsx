import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  BarChart3,
  MessageCircle,
  Settings,
  X,
  Rocket,
  Users,
  CreditCard,
  Receipt,
} from 'lucide-react'
import { cn } from '../../lib/utils'
import authService from '../../services/authService'

const BASE = import.meta.env.VITE_API_URL || '/api'

const navItems = [
  { to: '/dashboard',       label: 'Dashboard',        icon: LayoutDashboard },
  { to: '/inventario',      label: 'Inventario',        icon: Package },
  { to: '/ventas',          label: 'Ventas',            icon: ShoppingCart },
  { to: '/proveedores',     label: 'Proveedores',      icon: Users,          planes: ['medium', 'premium'] },
  { to: '/compras',         label: 'Compras',          icon: Receipt,        planes: ['medium', 'premium'] },
  { to: '/cuentas-por-pagar', label: 'Cuentas por Pagar', icon: CreditCard,   planes: ['medium', 'premium'] },
  { to: '/reportes',        label: 'Reportes',          icon: BarChart3 },
  { to: '/soporte',         label: 'Soporte Técnico',   icon: MessageCircle },
  { to: '/fabrica-apps',    label: 'Fábrica Apps',      icon: Rocket },
  { to: '/configuracion',   label: 'Configuración',     icon: Settings },
]

export default function Sidebar({ abierto, onCerrar }) {
  const [empresa, setEmpresa] = useState(null)

  useEffect(() => {
    authService
      .fetchAuth(`${BASE}/empresas/mi-empresa`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => setEmpresa(data))
      .catch(() => {})
  }, [])

  return (
    <>
      {/* Backdrop — solo mobile cuando el menú está abierto */}
      {abierto && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onCerrar}
        />
      )}

      {/* Drawer: fixed en mobile, relative en desktop */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 flex flex-col h-full transition-transform duration-300',
          'md:relative md:z-auto md:translate-x-0 md:shrink-0',
          abierto ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Cabecera del sidebar */}
        <div className="h-14 flex items-center justify-between px-6 border-b border-slate-700 shrink-0">
          <span className="text-slate-400 text-xs font-semibold uppercase tracking-widest">
            Menú
          </span>
          {/* Botón cerrar — solo visible en mobile */}
          <button
            onClick={onCerrar}
            aria-label="Cerrar menú"
            className="text-slate-400 hover:text-white transition-colors md:hidden"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems
            .filter((item) => !item.planes || item.planes.includes(empresa?.plan || 'basic'))
            .map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                onClick={onCerrar}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-3 rounded-md text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-indigo-600 text-white'
                      : 'text-slate-400 hover:bg-slate-800 hover:text-white',
                  )
                }
              >
                <Icon size={18} />
                {label}
              </NavLink>
            ))}
        </nav>
      </aside>
    </>
  )
}
