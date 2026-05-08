import { useVentas } from '../hooks/useVentas'

export default function Ventas() {
  const { ventas, cargando, error } = useVentas()

  const formatFecha = (fecha) =>
    new Date(fecha).toLocaleDateString('es-CO', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })

  if (cargando) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-violet-500" />
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Historial de Ventas</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4 text-sm">{error}</div>
      )}

      {ventas.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <div className="text-5xl mb-3">📊</div>
          <p>Aún no hay ventas registradas</p>
        </div>
      ) : (
        <div className="space-y-4">
          {ventas.map(venta => (
            <div key={venta.id} className="bg-white rounded-xl shadow-sm border p-5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="font-semibold text-gray-800">{formatFecha(venta.fecha_venta)}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    ID: {venta.id.split('-')[0]}…
                  </p>
                </div>
                <span className="font-bold text-xl text-violet-600">
                  ${venta.total.toLocaleString('es-CO')}
                </span>
              </div>
              <div className="border-t pt-3 space-y-1">
                {venta.detalles.map(d => (
                  <div key={d.id} className="flex justify-between text-sm text-gray-600">
                    <span>
                      {d.producto_nombre} × {d.cantidad}
                    </span>
                    <span>${d.subtotal.toLocaleString('es-CO')}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
