import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Inventario from './pages/Inventario'
import Ventas from './pages/Ventas'
import Reportes from './pages/Reportes'
import Soporte from './pages/Soporte'
import Planes from './pages/Planes'
import Configuracion from './pages/Configuracion'
import SuperAdmin from './pages/SuperAdmin'
import { useAuth } from './context/AuthContext'
import { isAdmin } from './utils/permissions'

function RootRedirect() {
  const { usuario } = useAuth()
  return <Navigate to={isAdmin(usuario) ? "/dashboard" : "/ventas"} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Rutas protegidas bajo el layout principal */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<RootRedirect />} />
          <Route path="/inventario" element={<Inventario />} />
          <Route path="/ventas" element={<Ventas />} />
          <Route path="/soporte" element={<Soporte />} />

          {/* Módulos exclusivos del Administrador / Dueño */}
          <Route element={<ProtectedRoute adminOnly />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/reportes" element={<Reportes />} />
            <Route path="/planes" element={<Planes />} />
            <Route path="/configuracion" element={<Configuracion />} />
            <Route path="/fabrica-apps" element={<Navigate to="/planes" replace />} />
          </Route>
        </Route>
      </Route>

      <Route path="/superadmin" element={<SuperAdmin />} />

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

