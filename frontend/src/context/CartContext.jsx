import { createContext, useContext, useState } from 'react'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [carrito, setCarrito] = useState([])
  const [carritoAbierto, setCarritoAbierto] = useState(false)

  const agregar = (producto) => {
    setCarrito(prev => {
      const existe = prev.find(i => i.id === producto.id)
      if (existe) {
        return prev.map(i =>
          i.id === producto.id ? { ...i, cantidad: i.cantidad + 1 } : i
        )
      }
      return [...prev, { ...producto, cantidad: 1 }]
    })
    setCarritoAbierto(true)
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

  return (
    <CartContext.Provider
      value={{ carrito, carritoAbierto, setCarritoAbierto, agregar, restar, eliminar, vaciar, total }}
    >
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart fuera de CartProvider')
  return ctx
}
