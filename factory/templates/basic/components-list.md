# Componentes React — Tier Basic

> Lista de componentes UI que todo sistema tier basic incluye.  
> Implementación de referencia en `frontend/src/` de Gestión Neiva.

---

## Context providers (estado global)

| Componente | Archivo | Qué maneja |
|-----------|---------|-----------|
| `AuthProvider` | `context/AuthContext.jsx` | JWT, usuario actual, login/logout |
| `CartProvider` | `context/CartContext.jsx` | Items del carrito, totales, checkout |

**Uso:**
```jsx
<AuthProvider>
  <CartProvider>
    <App />
  </CartProvider>
</AuthProvider>
```

---

## Layout

| Componente | Archivo | Descripción |
|-----------|---------|-------------|
| `Layout` | `components/layout/Layout.jsx` | Wrapper con Sidebar + Header + `<Outlet />` + CartSidebar |
| `Sidebar` | `components/layout/Sidebar.jsx` | Navegación lateral: Dashboard, Inventario, Ventas, Reportes |
| `Header` | `components/layout/Header.jsx` | Barra superior: nombre usuario, botón logout |
| `ProtectedRoute` | `components/ProtectedRoute.jsx` | Redirige a /login si no hay JWT válido |

---

## Páginas

| Página | Ruta | Descripción |
|--------|------|-------------|
| `Login` | `/login` | Form de login + enlace a registro |
| `Registro` | `/registro` | Form de registro empresa + admin |
| `Dashboard` | `/dashboard` | KPIs del día: ventas, ingresos, stock bajo |
| `Inventario` | `/inventario` | Grid de productos + búsqueda + CRUD |
| `Ventas` | `/ventas` | Historial de ventas (el carrito está en CartSidebar) |
| `Reportes` | `/reportes` | Filtro de fecha + botón exportar Excel |

---

## Componentes de dominio

| Componente | Archivo | Descripción |
|-----------|---------|-------------|
| `ProductoCard` | `components/ProductoCard.jsx` | Tarjeta de producto en grilla con botón "Agregar al carrito" |
| `ModalProducto` | `components/ModalProducto.jsx` | Modal CRUD: crear/editar producto con foto |
| `CartSidebar` | `components/CartSidebar.jsx` | Panel lateral deslizante: items, subtotales, checkout |

---

## Hooks de datos

| Hook | Archivo | Descripción |
|------|---------|-------------|
| `useProductos` | `hooks/useProductos.js` | Fetch y mutaciones de productos |
| `useVentas` | `hooks/useVentas.js` | Fetch de ventas e historial |

---

## Servicios

| Servicio | Archivo | Descripción |
|---------|---------|-------------|
| `authService` | `services/authService.js` | `fetchAuth()` con token automático, logout en 401 |

---

## Routing (App.jsx)

```jsx
<BrowserRouter>
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/registro" element={<Registro />} />

    <Route element={<ProtectedRoute />}>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/inventario" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/inventario" element={<Inventario />} />
        <Route path="/ventas" element={<Ventas />} />
        <Route path="/reportes" element={<Reportes />} />
      </Route>
    </Route>
  </Routes>
</BrowserRouter>
```

---

## Customización por cliente

Para cada sistema nuevo del tier basic:
1. Cambiar el nombre de la app en `Sidebar.jsx` (logo + nombre)
2. Adaptar los campos del `ModalProducto` a las entidades del cliente
3. Ajustar los KPIs del `Dashboard` a las métricas relevantes
4. Agregar o quitar páginas según módulos contratados

Ver `customization-checklist.md` para la lista completa.
