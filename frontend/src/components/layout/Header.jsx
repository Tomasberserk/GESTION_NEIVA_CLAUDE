import { Bell, User } from "lucide-react";

export default function Header() {
  return (
    <header className="h-14 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-6 shrink-0">
      <span className="text-white font-semibold text-lg tracking-tight">
        Gestión Neiva
      </span>
      <div className="flex items-center gap-4">
        <button className="text-slate-400 hover:text-white transition-colors">
          <Bell size={18} />
        </button>
        <div className="flex items-center gap-2 text-slate-300 text-sm">
          <User size={18} />
          <span>Usuario</span>
        </div>
      </div>
    </header>
  );
}
