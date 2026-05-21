# Schema — Tier Medium (ERP Ligero)

> Template de modelo de datos para sistemas ERP Ligeros que expanden el POS básico.  
> Incluye gestión de proveedores, compras de abastecimiento, y control financiero de Cuentas por Pagar (compras a crédito).

---

## Nuevas Entidades (Módulo ERP)

### Proveedor

Representa a los proveedores de productos de la empresa.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | Generado automáticamente |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| nit_o_cedula | VARCHAR(50) | NOT NULL | Identificación fiscal del proveedor |
| razon_social | VARCHAR(150) | NOT NULL | Nombre comercial o fiscal |
| contacto_nombre | VARCHAR(100) | NULL | Nombre de la persona de contacto |
| telefono | VARCHAR(50) | NULL | Teléfono de contacto |
| email | VARCHAR(255) | NULL | Correo electrónico |
| direccion | VARCHAR(255) | NULL | Dirección física |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

**Constraints:** `UNIQUE(empresa_id, nit_o_cedula)` — dos empresas diferentes pueden tener el mismo proveedor.  
**Índices:** `idx_proveedores_empresa` en `empresa_id`

---

### Compra (Maestro de Abastecimiento)

Registra las facturas o recibos de compra de mercancías de proveedores para aumentar stock.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| proveedor_id | UUID | FK proveedores(id) RESTRICT | No borrar proveedor con compras activas |
| usuario_id | UUID | FK usuarios(id) SET NULL | Usuario que registra la compra |
| numero_factura | VARCHAR(100) | NULL | Número de documento físico/electrónico del proveedor |
| fecha_compra | TIMESTAMPTZ | NOT NULL, default now() | Fecha de adquisición |
| metodo_pago | ENUM | NOT NULL | EFECTIVO, CREDITO, TRANSFERENCIA |
| estado | ENUM | NOT NULL | PAGADA, PENDIENTE, ANULADA |
| total | NUMERIC(12,2) | NOT NULL, default 0 | Monto total de la compra |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | Soft delete (anulación de compra) |

**Enums asociados:**
- `MetodoPagoCompra`: `EFECTIVO`, `CREDITO`, `TRANSFERENCIA`
- `EstadoCompra`: `PAGADA`, `PENDIENTE` (usado para compras a crédito no saldadas), `ANULADA`

**Índices:** `idx_compras_empresa` en `empresa_id`, `idx_compras_proveedor` en `proveedor_id`

---

### DetalleCompra (Líneas de Compra)

Detalle de ítems y costo de adquisición de productos reabastecidos.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| compra_id | UUID | FK compras(id) CASCADE | Relación con la compra |
| producto_id | UUID | FK productos(id) RESTRICT | No borrar producto con compras registradas |
| cantidad | NUMERIC(10,2) | NOT NULL | Unidades compradas (permite decimales para granel) |
| precio_costo | NUMERIC(12,2) | NOT NULL | **Snapshot** — Costo unitario acordado con proveedor |
| subtotal | NUMERIC(12,2) | NOT NULL | cantidad × precio_costo |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | |

**Regla de Negocio Crítica:**
Al completarse una compra exitosa, se debe ejecutar un trigger/servicio que:
1. **Incremente el stock** del producto correspondiente: `cantidad_actual = cantidad_actual + detalle.cantidad`
2. **Actualice el costo base** del producto: `precio_costo` del producto pasa a ser el `precio_costo` unitario de esta línea de compra (precio más reciente).

---

### CuentaPorPagar (Obligación Financiera)

Nace automáticamente si una compra se registra con `metodo_pago = 'CREDITO'`.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| compra_id | UUID | FK compras(id) RESTRICT | Compra origen del crédito |
| proveedor_id | UUID | FK proveedores(id) RESTRICT | Proveedor acreedor |
| monto_total | NUMERIC(12,2) | NOT NULL | Valor original de la deuda |
| saldo_pendiente | NUMERIC(12,2) | NOT NULL | Monto que resta por pagar |
| fecha_vencimiento | TIMESTAMPTZ | NOT NULL | Límite pactado para saldar la deuda |
| estado | ENUM | NOT NULL | PENDIENTE, PAGADA, VENCIDA |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | Soft delete |

**Enums asociados:**
- `EstadoCuentaPorPagar`: `PENDIENTE` (con saldo pendiente dentro del plazo), `PAGADA` (saldada), `VENCIDA` (plazo superado y saldo > 0)

---

### AbonoCuentaPorPagar (Historial de Pagos)

Registra los pagos parciales o totales que amortizan la deuda de una compra a crédito.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| cuenta_por_pagar_id | UUID | FK cuentas_por_pagar(id) CASCADE | Obligación a la que abona |
| monto | NUMERIC(12,2) | NOT NULL | Valor pagado en esta transacción |
| fecha_abono | TIMESTAMPTZ | NOT NULL, default now() | Fecha de ejecución del pago |
| metodo_pago | VARCHAR(50) | NOT NULL | EFECTIVO, TRANSFERENCIA, CHEQUE, etc. |
| nota | VARCHAR(255) | NULL | Comentario o número de comprobante |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | Soft delete (permite reversar abonos) |

---

## Relaciones Extendidas

```
Empresa 1 ──< Proveedor (cascade delete)
Empresa 1 ──< Compra (cascade delete)
Empresa 1 ──< CuentaPorPagar (cascade delete)

Proveedor 1 ──< Compra (RESTRICT delete)
Proveedor 1 ──< CuentaPorPagar (RESTRICT delete)

Compra 1 ──< DetalleCompra (cascade delete)
Compra 1 ──1 CuentaPorPagar (RESTRICT delete, condicional)

CuentaPorPagar 1 ──< AbonoCuentaPorPagar (cascade delete)
Producto 1 ──< DetalleCompra (RESTRICT delete)
```

---

## Reglas de Negocio a Nivel de Código (Services)

### 1. Registro de Compras (`CompraService.crear`)
1. Iniciar transacción de base de datos.
2. Calcular el `total` sumando los subtotales (`cantidad * precio_costo`) de cada item en `detalles`.
3. Crear el registro en `compras` con `estado = 'PAGADA'` si `metodo_pago` es `EFECTIVO` o `TRANSFERENCIA`. Si es `CREDITO`, el estado inicial es `PENDIENTE`.
4. Para cada línea en `detalles`:
   - Insertar en `detalle_compras`.
   - Incrementar `cantidad_actual` del producto en la cantidad comprada.
   - Actualizar el `precio_costo` del producto con el valor unitario de la compra.
5. Si el `metodo_pago` es `CREDITO`:
   - Crear el registro en `cuentas_por_pagar` con `monto_total = total`, `saldo_pendiente = total`, `estado = 'PENDIENTE'` y la `fecha_vencimiento` especificada.
6. Confirmar transacción.

### 2. Registro de Abonos (`CuentasPorPagarService.registrar_abono`)
1. Iniciar transacción de base de datos.
2. Cargar `CuentaPorPagar` con lock para evitar condiciones de carrera.
3. Verificar que `abono.monto <= saldo_pendiente`. Si es mayor, lanzar error 400.
4. Insertar el abono en `abonos_cuentas_por_pagar`.
5. Actualizar el `saldo_pendiente`: `saldo_pendiente = saldo_pendiente - abono.monto`.
6. Si `saldo_pendiente == 0`:
   - Cambiar estado de `CuentaPorPagar` a `'PAGADA'`.
   - Cargar la `Compra` origen asociada y actualizar su estado a `'PAGADA'`.
7. Confirmar transacción.

### 3. Reversión de Compras (Anulación / Soft Delete)
Al marcar `is_active = False` en una compra:
1. Reversar el incremento de stock en todos los productos asociados.
2. Si tenía una `CuentaPorPagar`, marcarla como inactiva/anulada.
3. El costo base del producto no se reversa automáticamente para evitar inconsistencias históricas, queda con el último valor válido anterior o el actual.
