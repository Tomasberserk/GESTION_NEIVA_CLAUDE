import { Bell, User } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Header() {
  const { usuario, logout } = useAuth();

  return (
    <header className="h-14 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-6 shrink-0">
      <span className="text-white font-semibold text-lg tracking-tight">
        Gestión Neiva
      </span>
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
          <span>{usuario?.email ?? "Usuario"}</span>
        </button>
      </div>
    </header>
  );
}
