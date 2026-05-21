# Componentes React — Tier Medium

> Inventario de componentes y vistas React 19 JSX para sistemas ERP Ligeros.  
> Diseñado bajo arquitectura modular multi-tenant, Shadcn/UI y TailwindCSS v4.

---

## Estructura de Navegación del Layout (Ampliación)

El `Sidebar` se amplía agregando las rutas comerciales y financieras obligatorias para la administración del ERP:

- 📊 **Dashboard** (Dashboard financiero básico + deudas consolidadas)
- 📦 **Inventario** (POS + CRUD de productos)
- 🛒 **Ventas** (Historial y cuadre de caja)
- 🤝 **Proveedores** (Directorio de abastecedores)
- 📥 **Compras** (Historial y registro de mercancías recibidas)
- 💸 **Cuentas por Pagar** (Gestión financiera de obligaciones a crédito)
- 📈 **Reportes** (Exportación de caja y compras a Excel)

---

## Nuevas Páginas de Dominio

### 🤝 Proveedores (`pages/Proveedores.jsx`)
Vista principal para el manejo de contactos comerciales y fiscales.
- **Grilla/Tabla de Proveedores:** Muestra Razón Social, NIT, Contacto, Teléfono, Correo e Indicador de compras realizadas.
- **Buscador Integrado:** Filtrado instantáneo por nombre y NIT en tiempo real.
- **Modal CRUD:** Acceso rápido a creación y edición.

### 📥 Compras (`pages/Compras.jsx` & `pages/RegistrarCompra.jsx`)
Historial y registro de transacciones de ingreso de mercancías.

*   `pages/Compras.jsx` (Listado Histórico):
    *   Filtros por rango de fecha, proveedor y método de pago (Efectivo/Crédito).
    *   Tabla con Número de Factura, Proveedor, Fecha, Método de Pago, Estado (`PAGADA`, `PENDIENTE`, `ANULADA`), Total y botón de "Ver Detalle".
    *   Botón destacado "Registrar Nueva Compra" redirige a la vista del formulario.
*   `pages/RegistrarCompra.jsx` (Formulario Maestro-Detalle):
    *   **Cabecera:** Selector de Proveedor (con buscador), Número de Factura del proveedor, Selector de Método de Pago (`EFECTIVO`, `CREDITO`), y Fecha de Vencimiento del crédito (habilitado condicionalmente).
    *   **Buscador e Inserción de Productos:** Buscador inteligente por nombre o código de barras para seleccionar productos del inventario y cargarlos a la lista de compra.
    *   **Grilla Detalle de Compra:** Fila por producto seleccionado con:
        *   Nombre del producto.
        *   Input de `Cantidad` (soporta decimales para granel).
        *   Input de `Costo Unitario` (precio de costo pactado en esta transacción, auto-rellenado con el `precio_costo` actual del producto pero editable).
        *   Subtotal calculado automáticamente.
        *   Botón para remover item.
    *   **Panel de Resumen:** Visualización del total consolidado y botón "Confirmar y Registrar Compra" (dispara la lógica del Backend de actualización de stock y costos).

### 💸 Cuentas por Pagar (`pages/CuentasPorPagar.jsx`)
Panel financiero de control de deudas con proveedores.
- **KPI Banners superiores:**
  - `Total Deuda Activa`: Suma de todos los saldos pendientes de cuentas en estado PENDIENTE y VENCIDA.
  - `Obligaciones Próximas a Vencer`: Deudas con vencimiento menor a 7 días.
  - `Deudas Vencidas`: Suma de saldos pendientes cuyo plazo ya expiró (alerta visual roja).
- **Tabla de Obligaciones por Pagar:**
  - Columnas: Proveedor, Factura Compra, Fecha Emisión, Fecha Vencimiento, Monto Original, Saldo Pendiente, Estado (Verde = PAGADA, Amarillo = PENDIENTE, Rojo = VENCIDA).
  - Acciones: Botón "Registrar Abono" y "Ver Historial de Abonos".

---

## Nuevos Componentes de Dominio (UI Modals)

### 1. `components/ModalProveedor.jsx`
Modal de creación y edición de proveedores.
- Formulario limpio con validaciones en inputs: Razón Social, NIT (requerido), Nombre de Contacto, Teléfono, Correo y Dirección.

### 2. `components/DetalleCompraModal.jsx`
Modal emergente para visualizar el detalle de una compra pasada.
- Muestra datos generales del proveedor, factura y total.
- Tabla detallada de items comprados: Producto, Cantidad, Costo Unitario, Subtotal.
- Información del estado de pago asociado (si fue a crédito, muestra enlace rápido a la Cuenta por Pagar correspondiente).

### 3. `components/ModalAbono.jsx`
Modal de doble función para abonos financieros.
- **Formulario de Registro:** Input numérico para ingresar el monto a abonar (con validación de no exceder el saldo pendiente), selector de método de pago de abono (`TRANSFERENCIA`, `EFECTIVO`, `CHEQUE`), e input de texto para notas o referencias bancarias.
- **Historial de Abonos Recientes:** Sección en el mismo modal que renderiza la lista cronológica de abonos realizados a esta obligación, mostrando fecha, monto, medio de pago, notas y un botón de "Reversar Abono" (DELETE abono) para administradores.

---

## Nuevos Hooks de Datos (API Fetchers)

### 1. `hooks/useProveedores.js`
Maneja el estado y operaciones CRUD de proveedores.
```javascript
const { proveedores, cargando, crearProveedor, actualizarProveedor, eliminarProveedor } = useProveedores();
```

### 2. `hooks/useCompras.js`
Maneja el registro y consulta de facturas de compra.
```javascript
const { compras, cargando, registrarCompra, anularCompra } = useCompras();
```

### 3. `hooks/useCuentasPorPagar.js`
Maneja las deudas con proveedores y las operaciones de abonos.
```javascript
const { cuentas, KPIs, registrarAbono, reversarAbono } = useCuentasPorPagar();
```

---

## Configuración de Rutas React Router v6

Integración en el flujo del layout principal:

```jsx
<BrowserRouter>
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/registro" element={<Registro />} />

    <Route element={<ProtectedRoute />}>
      <Route element={<Layout />}>
        {/* Rutas POS Core (Basic) */}
        <Route path="/" element={<Navigate to="/inventario" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/inventario" element={<Inventario />} />
        <Route path="/ventas" element={<Ventas />} />
        <Route path="/reportes" element={<Reportes />} />
        
        {/* Nuevas Rutas ERP (Medium) */}
        <Route path="/proveedores" element={<Proveedores />} />
        <Route path="/compras" element={<Compras />} />
        <Route path="/compras/registrar" element={<RegistrarCompra />} />
        <Route path="/cuentas-por-pagar" element={<CuentasPorPagar />} />
      </Route>
    </Route>
  </Routes>
</BrowserRouter>
```
