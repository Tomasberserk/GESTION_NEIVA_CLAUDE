import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Package, Users, ShoppingCart, CreditCard, X } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const navBase = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/inventario', label: 'Inventario', icon: Package },
  { to: '/proveedores', label: 'Proveedores', icon: Users },
  { to: '/compras', label: 'Compras', icon: ShoppingCart },
]

const navAdmin = [
  { to: '/cuentas-por-pagar', label: 'Cuentas por Pagar', icon: CreditCard },
]

export default function Sidebar({ abierto, onCerrar }) {
  const { usuario } = useAuth()
  const esAdmin = usuario?.rol === 'admin'
  const items = esAdmin ? [...navBase, ...navAdmin] : navBase

  return (
    <>
      {/* Overlay mobile */}
      {abierto && (
        <div
          className="fixed inset-0 bg-black/40 z-20 lg:hidden"
          onClick={onCerrar}
        />
      )}

      <aside
        className={[
          'fixed top-0 left-0 h-full w-64 z-30 flex flex-col transition-transform duration-200',
          'lg:static lg:translate-x-0',
          abierto ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
        style={{ backgroundColor: '#1e1b4b' }}
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
          <div>
            <p className="text-white font-bold text-base leading-tight">🏭 ERP Distribuidora</p>
            <p className="text-indigo-300 text-xs mt-0.5">Sistema · Medium</p>
          </div>
          <button
            onClick={onCerrar}
            className="lg:hidden text-indigo-300 hover:text-white transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {items.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onCerrar}
              className={({ isActive }) => [
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-indigo-500 text-white'
                  : 'text-indigo-200 hover:bg-white/10 hover:text-white',
              ].join(' ')}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-3 border-t border-white/10">
          <p className="text-indigo-400 text-xs">Tier Medium · v1.0</p>
        </div>
      </aside>
    </>
  )
}
