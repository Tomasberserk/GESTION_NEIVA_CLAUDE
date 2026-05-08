import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function Navbar() {
  const { usuario, logout } = useAuth()
  const { carrito, setCarritoAbierto } = useCart()
  const totalItems = carrito.reduce((a, i) => a + i.cantidad, 0)

  return (
    <nav className="bg-violet-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <span className="font-bold text-lg tracking-tight">TiendApp</span>

        <div className="flex items-center gap-6 text-sm">
          {[
            { to: '/inventario', label: 'Inventario' },
            { to: '/ventas', label: 'Ventas' },
            { to: '/reportes', label: 'Reportes' },
          ].map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                isActive
                  ? 'font-semibold underline underline-offset-4'
                  : 'hover:text-violet-200 transition-colors'
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCarritoAbierto(true)}
            className="relative bg-violet-500 hover:bg-violet-400 px-3 py-1.5 rounded-lg transition-colors text-sm"
          >
            🛒
            {totalItems > 0 && (
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                {totalItems}
              </span>
            )}
          </button>
          <span className="text-xs text-violet-200 hidden sm:block">{usuario?.email}</span>
          <button
            onClick={logout}
            className="text-xs bg-violet-700 hover:bg-violet-800 px-3 py-1.5 rounded-lg transition-colors"
          >
            Salir
          </button>
        </div>
      </div>
    </nav>
  )
}
