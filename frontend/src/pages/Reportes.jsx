import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import authService from '../services/authService'

const BASE = 'http://localhost:8000'

export default function Reportes() {
  const { usuario } = useAuth()
  const [descargando, setDescargando] = useState(false)
  const [error, setError] = useState(null)
  const [exito, setExito] = useState(false)

  const descargarExcel = async () => {
    setDescargando(true)
    setError(null)
    setExito(false)
    try {
      const token = authService.getToken()
      const res = await fetch(`${BASE}/reportes/ventas/excel/${usuario.empresa_id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Error generando el reporte')

      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `ventas_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      setExito(true)
      setTimeout(() => setExito(false), 4000)
    } catch (e) {
      setError(e.message)
    } finally {
      setDescargando(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Reportes</h1>

      <div className="bg-white rounded-xl shadow-sm border p-8 max-w-sm">
        <div className="text-center">
          <div className="text-5xl mb-4">📊</div>
          <h2 className="font-semibold text-lg text-gray-800 mb-2">Reporte de Ventas</h2>
          <p className="text-sm text-gray-500 mb-6">
            Descarga el historial completo de ventas en formato Excel (.xlsx)
          </p>

          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4">{error}</div>
          )}
          {exito && (
            <div className="bg-green-50 text-green-700 p-3 rounded-lg text-sm mb-4">
              ✅ Archivo descargado
            </div>
          )}

          <button
            onClick={descargarExcel}
            disabled={descargando}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-200 disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-lg transition-colors w-full"
          >
            {descargando ? '⏳ Generando...' : '⬇️ Descargar Excel'}
          </button>
        </div>
      </div>
    </div>
  )
}
