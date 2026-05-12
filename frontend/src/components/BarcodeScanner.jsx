import { useEffect, useRef, useState } from 'react'
import { BrowserMultiFormatReader } from '@zxing/browser'
import { NotFoundException } from '@zxing/library'

/**
 * Abre la cámara y escanea continuamente hasta detectar un código.
 * Props:
 *   onScan(texto)  — se llama una vez con el código detectado
 *   onClose()      — se llama al cancelar o cuando hay error irrecuperable
 */
export default function BarcodeScanner({ onScan, onClose }) {
  const videoRef   = useRef(null)
  const controlRef = useRef(null)
  const onScanRef  = useRef(onScan)   // ref para evitar re-mount al cambiar el callback
  const [estado, setEstado] = useState('iniciando') // 'iniciando' | 'activo' | 'error'
  const [mensajeError, setMensajeError] = useState('')

  // Mantener la ref actualizada sin re-ejecutar el effect
  useEffect(() => { onScanRef.current = onScan }, [onScan])

  useEffect(() => {
    if (!videoRef.current) return

    const reader = new BrowserMultiFormatReader()
    let montado = true

    reader
      .decodeFromVideoDevice(undefined, videoRef.current, (result, err) => {
        if (!montado) return
        if (result) {
          const texto = result.getText()
          onScanRef.current(texto)  // completa el campo
        }
        // NotFoundException es el estado normal "no hay código en el frame" — ignorar
        if (err && !(err instanceof NotFoundException)) {
          console.warn('ZXing warning:', err)
        }
      })
      .then(controls => {
        if (!montado) { controls.stop(); return }
        controlRef.current = controls
        setEstado('activo')
      })
      .catch(err => {
        if (!montado) return
        if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
          setMensajeError('Permiso de cámara denegado. Escribe el código manualmente.')
        } else if (err?.name === 'NotFoundError') {
          setMensajeError('No se encontró cámara en este dispositivo.')
        } else {
          setMensajeError('No se pudo acceder a la cámara.')
        }
        setEstado('error')
      })

    return () => {
      montado = false
      controlRef.current?.stop()
    }
  }, []) // solo al montar — el callback vive en la ref

  return (
    <div className="mt-2 rounded-xl overflow-hidden border border-violet-300 bg-black relative">

      {/* Video siempre en el DOM para que ZXing tenga el elemento listo */}
      <video
        ref={videoRef}
        className={`w-full ${estado === 'error' ? 'hidden' : 'block'}`}
        style={{ maxHeight: '200px', objectFit: 'cover' }}
        muted
        playsInline
      />

      {/* Overlay spinner mientras inicia */}
      {estado === 'iniciando' && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-10 gap-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-400" />
          <p className="text-xs text-white/60">Iniciando cámara…</p>
        </div>
      )}

      {/* Mira / crosshair cuando está activo */}
      {estado === 'activo' && (
        <>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
            {/* Esquinas de la mira */}
            <div className="relative w-52 h-20">
              <span className="absolute top-0 left-0 w-5 h-5 border-t-2 border-l-2 border-violet-400 rounded-tl" />
              <span className="absolute top-0 right-0 w-5 h-5 border-t-2 border-r-2 border-violet-400 rounded-tr" />
              <span className="absolute bottom-0 left-0 w-5 h-5 border-b-2 border-l-2 border-violet-400 rounded-bl" />
              <span className="absolute bottom-0 right-0 w-5 h-5 border-b-2 border-r-2 border-violet-400 rounded-br" />
            </div>
          </div>
          <div className="absolute bottom-2 left-0 right-0 text-center z-10">
            <p className="text-xs text-white/60 bg-black/40 inline-block px-2 py-0.5 rounded">
              Apunta el código de barras al recuadro
            </p>
          </div>
        </>
      )}

      {/* Estado de error */}
      {estado === 'error' && (
        <div className="p-5 text-center">
          <p className="text-2xl mb-2">📷</p>
          <p className="text-sm text-red-400 mb-3">{mensajeError}</p>
          <button
            type="button"
            onClick={onClose}
            className="text-sm text-violet-400 hover:text-violet-300 underline"
          >
            Escribir manualmente
          </button>
        </div>
      )}

      {/* Botón cerrar */}
      {estado !== 'error' && (
        <button
          type="button"
          onClick={onClose}
          className="absolute top-2 right-2 z-20 bg-black/50 hover:bg-black/70 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm transition-colors"
          aria-label="Cerrar escáner"
        >
          ✕
        </button>
      )}
    </div>
  )
}
