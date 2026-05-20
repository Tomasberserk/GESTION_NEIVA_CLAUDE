import { createContext, useContext, useState } from 'react'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [carrito, setCarrito] = useState([])

  const agregar = (producto) => {
    setCarrito(prev => {
      const existe = prev.find(i => i.id === producto.id)
      if (existe) {
        if (existe.cantidad >= producto.cantidad_actual) return prev
        return prev.map(i =>
          i.id === producto.id ? { ...i, cantidad: i.cantidad + 1 } : i
        )
      }
      if (producto.cantidad_actual <= 0) return prev
      return [...prev, { ...producto, cantidad: 1 }]
    })
  }

  const restar = (productoId) => {
    setCarrito(prev =>
      prev
        .map(i => (i.id === productoId ? { ...i, cantidad: i.cantidad - 1 } : i))
        .filter(i => i.cantidad > 0)
    )
  }

  const eliminar = (productoId) => {
    setCarrito(prev => prev.filter(i => i.id !== productoId))
  }

  const vaciar = () => setCarrito([])

  const total = carrito.reduce((acc, i) => acc + i.precio_venta * i.cantidad, 0)
  const totalItems = carrito.reduce((acc, i) => acc + i.cantidad, 0)

  return (
    <CartContext.Provider value={{ carrito, agregar, restar, eliminar, vaciar, total, totalItems }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart fuera de CartProvider')
  return ctx
}
