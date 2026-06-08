import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import PlanProtectedRoute from './components/PlanProtectedRoute'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Inventario from './pages/Inventario'
import Ventas from './pages/Ventas'
import Reportes from './pages/Reportes'
import Soporte from './pages/Soporte'
import FabricaApps from './pages/FabricaApps'
import SuperAdmin from './pages/SuperAdmin'
import Proveedores from './pages/Proveedores'
import Compras from './pages/Compras'
import RegistrarCompra from './pages/RegistrarCompra'
import CuentasPorPagar from './pages/CuentasPorPagar'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/inventario" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/inventario" element={<Inventario />} />
          <Route path="/ventas" element={<Ventas />} />
          <Route path="/reportes" element={<Reportes />} />
          <Route path="/soporte" element={<Soporte />} />
          <Route path="/fabrica-apps" element={<FabricaApps />} />

          {/* Módulos ERP del Plan Medium/Premium */}
          <Route element={<PlanProtectedRoute planesPermitidos={['medium', 'premium']} />}>
            <Route path="/proveedores" element={<Proveedores />} />
            <Route path="/compras" element={<Compras />} />
            <Route path="/compras/nueva" element={<RegistrarCompra />} />
            <Route path="/cuentas-por-pagar" element={<CuentasPorPagar />} />
          </Route>
        </Route>
      </Route>

      <Route path="/superadmin" element={<SuperAdmin />} />

      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}
