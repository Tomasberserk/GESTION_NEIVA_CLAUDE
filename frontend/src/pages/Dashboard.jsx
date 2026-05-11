import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const { usuario } = useAuth()

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-2">Dashboard</h1>
      <p className="text-gray-500 text-sm">
        Bienvenido{usuario?.email ? `, ${usuario.email}` : ''} — Gestión Neiva
      </p>
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Ventas hoy</p>
          <p className="text-3xl font-bold text-slate-800">—</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Productos</p>
          <p className="text-3xl font-bold text-slate-800">—</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Ingresos</p>
          <p className="text-3xl font-bold text-slate-800">—</p>
        </div>
      </div>
    </div>
  )
}