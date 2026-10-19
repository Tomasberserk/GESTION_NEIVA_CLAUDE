import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/layout/Layout'
import Registro from './pages/Registro'
import Login from './pages/Login'
import { useAuth } from './context/AuthContext'
import { isAdmin } from './utils/permissions'

// Code-splitting: cada ruta carga su chunk solo cuando se navega a ella.
// El visitante del landing NO descarga recharts/zxing (brecha B6 — Sprint 9).
const LandingPage = lazy(() => import('./pages/LandingPage'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Inventario = lazy(() => import('./pages/Inventario'))
const Ventas = lazy(() => import('./pages/Ventas'))
const Reportes = lazy(() => import('./pages/Reportes'))
const Soporte = lazy(() => import('./pages/Soporte'))
const Planes = lazy(() => import('./pages/Planes'))
const Configuracion = lazy(() => import('./pages/Configuracion'))
const SuperAdmin = lazy(() => import('./pages/SuperAdmin'))

const CargandoPantalla = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#fafaf9]">
    <div className="w-8 h-8 rounded-full border-2 border-emerald-200 border-t-emerald-600 animate-spin" />
  </div>
)

function RootRedirect() {
  const { usuario } = useAuth()
  return <Navigate to={isAdmin(usuario) ? "/dashboard" : "/ventas"} replace />
}

export default function App() {
  return (
    <Suspense fallback={<CargandoPantalla />}>
      <Routes>
      {/* 🌐 Experiencia WEB: Conoce, Comprende y Confía */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/registro" element={<Registro />} />
      <Route path="/login" element={<Login />} />

      {/* 📱 Experiencia APP: Gestiona tu Negocio (Protegida) */}
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/app" element={<RootRedirect />} />
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

      <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}


