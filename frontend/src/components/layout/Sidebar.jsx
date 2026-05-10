import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  BarChart3,
  Settings,
} from "lucide-react";
import { cn } from "../../lib/utils";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/inventario", label: "Inventario", icon: Package },
  { to: "/ventas", label: "Ventas", icon: ShoppingCart },
  { to: "/reportes", label: "Reportes", icon: BarChart3 },
  { to: "/configuracion", label: "Configuración", icon: Settings },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 flex flex-col shrink-0 h-full">
      <div className="h-14 flex items-center px-6 border-b border-slate-700">
        <span className="text-slate-400 text-xs font-semibold uppercase tracking-widest">
          Menú
        </span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
