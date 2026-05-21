# Schema — ERP Distribuidora (Tier Medium)

> Modelo de datos específico para **Distribuidora Mayorista de Abarrotes y Papelería**.  
> Extiende el patrón POS básico (Gestión Neiva) con gestión de proveedores, compras de abastecimiento,   > y control financiero de cuentas por pagar (crédito a proveedores).
>
> **Cliente:** Distribuidora de mayoreo con múltiples productos, proveedores y flujos de crédito.  
> **Tier:** Medium  
> **Multi-tenant:** Sí  
> **Soft Delete:** Sí (todos los datos con `is_active` boolean)

---

## 📊 Modelo de Entidades

### Raíz Multi-Tenant

#### Empresa

Representa a la distribuidora mayorista o filial bajo la cual se organizan todos los datos.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | Identificador único |
| nombre_comercial | VARCHAR(150) | NOT NULL | Razón social de la distribuidora |
| nit_o_cedula | VARCHAR(50) | NOT NULL, UNIQUE | NIT o cédula del contribuyente |
| plan | VARCHAR(50) | default 'trial' | trial, basic, medium, professional |
| trial_expires_at | TIMESTAMPTZ | NULL | Fecha de vencimiento del período de prueba |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete / Suspensión |

**Índices:** `idx_empresas_nit` en `nit_o_cedula` (único)

---

### Usuarios

#### Usuario

Empleados de la distribuidora con roles y permisos diferenciados.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| email | VARCHAR(255) | NOT NULL, UNIQUE per empresa | Email de login único en empresa |
| hashed_password | VARCHAR | NOT NULL | Contraseña hasheada con bcrypt |
| rol | VARCHAR(50) | NOT NULL, enum: admin, asistente | Rol de acceso |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | |

**Enums:**
- `RolUsuario`: `admin` (dueño/gerente), `asistente` (auxiliar de compras/inventario)

**Índices:** `idx_usuarios_empresa` en `empresa_id`, `idx_usuarios_email` en `email`

**Constraint:** `UNIQUE(empresa_id, email)`

**Notas sobre Roles:**
- `admin`: Acceso total (Inventario, Proveedores, Compras, Cuentas por Pagar, Reportes).
- `asistente`: Solo Inventario, Proveedores y Compras. Prohibido acceder a Cuentas por Pagar y Reportes Financieros.

---

### Inventario

#### Producto

Catálogo de artículos que la distribuidora maneja (abarrotes, papelería, etc.).

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| nombre | VARCHAR(200) | NOT NULL | Descripción del producto |
| codigo_barras | VARCHAR(50) | NOT NULL, UNIQUE per empresa | EAN13 o código interno |
| categoria | VARCHAR(100) | NULL | Familia del producto (ej. "Papelería", "Abarrotes") |
| precio_costo | NUMERIC(12,2) | NOT NULL, default 0 | Último costo de adquisición (actualiza con compras) |
| precio_venta | NUMERIC(12,2) | NOT NULL | PVP o margen mayorista |
| cantidad_actual | NUMERIC(10,3) | NOT NULL, default 0 | Stock disponible |
| unidad_medida | VARCHAR(50) | default 'UNIDAD' | Unidad de venta (UNIDAD, CAJA, BULTO, KG, etc.) |
| foto_url | VARCHAR(500) | NULL | URL de miniatura del producto |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

**Enums:**
- `UnidadMedida`: `UNIDAD`, `CAJA`, `BULTO`, `KG`, `LITRO`, `METRO`

**Índices:**
- `idx_productos_empresa` en `empresa_id`
- `idx_productos_codigo_barras` en (`empresa_id`, `codigo_barras`)
- `idx_productos_categoria` en `categoria`

**Constraint:** `UNIQUE(empresa_id, codigo_barras)`

**Regla de Negocio Crítica:**
- Al registrar una compra exitosa, `precio_costo` se actualiza automáticamente al costo unitario del detalle de compra más reciente.
- Al anular una compra, se reversa la cantidad del stock.

---

### Proveedores

#### Proveedor

Contactos comerciales de proveedores de mercancía para la distribuidora.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| nit_o_cedula | VARCHAR(50) | NOT NULL | Identificación fiscal del proveedor |
| razon_social | VARCHAR(150) | NOT NULL | Nombre comercial o fiscal del proveedor |
| contacto_nombre | VARCHAR(100) | NULL | Nombre de la persona de contacto |
| telefono | VARCHAR(50) | NULL | Teléfono de contacto (ej. +57 300 123 4567) |
| email | VARCHAR(255) | NULL | Correo electrónico |
| direccion | VARCHAR(255) | NULL | Dirección física de la proveeduría |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

**Índices:**
- `idx_proveedores_empresa` en `empresa_id`
- `idx_proveedores_razon_social` en `razon_social`

**Constraint:** `UNIQUE(empresa_id, nit_o_cedula)`

**Notas:**
- El mismo NIT puede ser proveedor en diferentes empresas.
- Búsquedas rápidas por `razon_social`, `nit_o_cedula` o `contacto_nombre`.

---

### Compras y Abastecimiento

#### Compra (Maestro)

Registro de facturas o recibos de adquisición de mercancía para reabastecer inventario.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| proveedor_id | UUID | FK proveedores(id) RESTRICT | No borrar proveedor con compras activas |
| usuario_id | UUID | FK usuarios(id) SET NULL | Usuario que registró la compra |
| numero_factura | VARCHAR(100) | NULL | Número de documento del proveedor (ej. FAC-8973) |
| fecha_compra | TIMESTAMPTZ | NOT NULL, default now() | Fecha de adquisición |
| metodo_pago | VARCHAR(50) | NOT NULL, enum | EFECTIVO, CREDITO, TRANSFERENCIA |
| fecha_vencimiento | TIMESTAMPTZ | NULL | Vencimiento (obligatorio si metodo_pago = CREDITO) |
| estado | VARCHAR(50) | NOT NULL, enum | PAGADA, PENDIENTE, ANULADA |
| total | NUMERIC(12,2) | NOT NULL, default 0 | Monto total de la compra |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete (marca como ANULADA) |

**Enums:**
- `MetodoPagoCompra`: `EFECTIVO`, `CREDITO`, `TRANSFERENCIA`
- `EstadoCompra`: `PAGADA` (pagada en efectivo/transferencia o crédito totalmente saldado)
  , `PENDIENTE` (compra a crédito con saldo abierto), `ANULADA` (compra reversada)

**Índices:**
- `idx_compras_empresa` en `empresa_id`
- `idx_compras_proveedor` en `proveedor_id`
- `idx_compras_estado` en `estado`
- `idx_compras_fecha` en `fecha_compra`

**Regla de Negocio:**
- Si `metodo_pago = 'EFECTIVO'` o `'TRANSFERENCIA'`, `estado = 'PAGADA'` al crear.
- Si `metodo_pago = 'CREDITO'`, `estado = 'PENDIENTE'` y crea automáticamente un registro en `CuentaPorPagar`.
- Anular una compra (soft delete) debe reversar el stock de todos sus detalles.

---

#### DetalleCompra (Líneas de Compra)

Ítems individuales de productos reabastecidos en una compra.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | |
| compra_id | UUID | FK compras(id) CASCADE | Relación con la compra maestro |
| producto_id | UUID | FK productos(id) RESTRICT | No borrar producto con compras registradas |
| cantidad | NUMERIC(10,3) | NOT NULL | Unidades compradas (soporta decimales para granel) |
| precio_costo | NUMERIC(12,2) | NOT NULL | **Snapshot** — Costo unitario pactado con proveedor |
| subtotal | NUMERIC(12,2) | NOT NULL | Calculado: `cantidad × precio_costo` |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | |

**Índices:**
- `idx_detalle_compra_compra` en `compra_id`
- `idx_detalle_compra_producto` en `producto_id`

**Regla de Negocio Crítica (Trigger/Servicio):**

Cuando una compra se registra exitosamente (POST /api/compras):
1. **Incrementar stock:** `Producto.cantidad_actual += DetalleCompra.cantidad`
2. **Actualizar costo:** `Producto.precio_costo = DetalleCompra.precio_costo` (última compra)
3. **Calcular total:** `Compra.total = SUM(DetalleCompra.subtotal)`
4. **Si es crédito:** Crear `CuentaPorPagar` automáticamente

Cuando se anula una compra (DELETE /api/compras/{id}):
1. **Revertir stock:** `Producto.cantidad_actual -= DetalleCompra.cantidad`
2. **Validar:** Si `Producto.cantidad_actual < 0`, rechazar anulación (stock insuficiente, mercancía ya vendida)
3. **Anular deuda:** Si existe `CuentaPorPagar`, marcar como inactiva

---

### Finanzas: Cuentas por Pagar

#### CuentaPorPagar

Obligación financiera generada automáticamente al comprar a crédito.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| compra_id | UUID | FK compras(id) RESTRICT | Compra origen del crédito |
| proveedor_id | UUID | FK proveedores(id) RESTRICT | Proveedor acreedor |
| monto_total | NUMERIC(12,2) | NOT NULL | Valor original de la deuda (= Compra.total) |
| saldo_pendiente | NUMERIC(12,2) | NOT NULL | Monto restante por pagar |
| fecha_vencimiento | TIMESTAMPTZ | NOT NULL | Fecha límite para saldar |
| estado | VARCHAR(50) | NOT NULL, enum | PENDIENTE, PAGADA, VENCIDA |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

**Enums:**
- `EstadoCuentaPorPagar`: `PENDIENTE` (deuda abierta), `PAGADA` (100% saldada), `VENCIDA` (pasó la fecha sin pagar)

**Índices:**
- `idx_cuentas_pagar_empresa` en `empresa_id`
- `idx_cuentas_pagar_proveedor` en `proveedor_id`
- `idx_cuentas_pagar_estado` en `estado`
- `idx_cuentas_pagar_vencimiento` en `fecha_vencimiento` (alertas de vencimiento)

**Regla de Negocio:**
- Se crea automáticamente cuando se registra una compra con `metodo_pago = 'CREDITO'`.
- `monto_total` y `saldo_pendiente` comienzan iguales.
- `estado = 'VENCIDA'` cuando `fecha_vencimiento < NOW()` y `saldo_pendiente > 0` (computado o por trigger).
- Al crear, `estado = 'PENDIENTE'`.

---

#### AbonoCuentaPorPagar

Movimiento contable de pago que amortiza una deuda con un proveedor.

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK, default uuid() | |
| cuenta_por_pagar_id | UUID | FK cuentas_por_pagar(id) RESTRICT | Deuda siendo amortizada |
| monto | NUMERIC(12,2) | NOT NULL | Monto del abono |
| fecha_abono | TIMESTAMPTZ | NOT NULL, default now() | Fecha del pago |
| metodo_pago | VARCHAR(50) | NOT NULL, enum | EFECTIVO, TRANSFERENCIA, CHEQUE |
| nota | VARCHAR(500) | NULL | Referencia o nota (ej. "Transfer Ref: #48109") |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete (reversión) |

**Enums:**
- `MetodoPagoAbono`: `EFECTIVO`, `TRANSFERENCIA`, `CHEQUE`

**Índices:**
- `idx_abonos_cxp` en `cuenta_por_pagar_id`
- `idx_abonos_fecha` en `fecha_abono`

**Regla de Negocio (Trigger/Servicio):**

Al registrar un abono (POST /api/cuentas-por-pagar/{cxp_id}/abonos):
1. **Validar:** Monto ≤ `CuentaPorPagar.saldo_pendiente`
2. **Amortizar:** `CuentaPorPagar.saldo_pendiente -= Abono.monto`
3. **Actualizar estado:**
   - Si `saldo_pendiente == 0`: `CuentaPorPagar.estado = 'PAGADA'` y `Compra.estado = 'PAGADA'`
   - Si `saldo_pendiente > 0` y aún no vencida: mantener `'PENDIENTE'`
   - Si `saldo_pendiente > 0` y vencida: mantener `'VENCIDA'`

Al reversar un abono (DELETE /api/cuentas-por-pagar/abonos/{abono_id}):
1. **Restaurar saldo:** `CuentaPorPagar.saldo_pendiente += Abono.monto`
2. **Degradar estado:** Si la deuda pasaba a `'PAGADA'`, vuelve a `'PENDIENTE'`
3. **Marcar abono inactivo:** `Abono.is_active = False`

---

## 🗺️ Diagrama Relacional Simplificado

```
Empresa (raíz multi-tenant)
  ├── Usuario
  ├── Producto
  ├── Proveedor
  └── Compra (maestro)
      ├── DetalleCompra (detalle → Producto)
      └── CuentaPorPagar (si metodo_pago = CREDITO)
          └── AbonoCuentaPorPagar
```

---

## 🔑 Constraints de Integridad

### Foreign Keys
| Tabla | Columna | Referencia | Acción |
|-------|---------|-----------|--------|
| Usuario | empresa_id | Empresa.id | CASCADE |
| Producto | empresa_id | Empresa.id | CASCADE |
| Proveedor | empresa_id | Empresa.id | CASCADE |
| Compra | empresa_id | Empresa.id | CASCADE |
| Compra | proveedor_id | Proveedor.id | RESTRICT |
| Compra | usuario_id | Usuario.id | SET NULL |
| DetalleCompra | compra_id | Compra.id | CASCADE |
| DetalleCompra | producto_id | Producto.id | RESTRICT |
| CuentaPorPagar | empresa_id | Empresa.id | CASCADE |
| CuentaPorPagar | compra_id | Compra.id | RESTRICT |
| CuentaPorPagar | proveedor_id | Proveedor.id | RESTRICT |
| AbonoCuentaPorPagar | cuenta_por_pagar_id | CuentaPorPagar.id | RESTRICT |

---

## 🛡️ Seguridad Multi-Tenant

**Regla Principal:** Toda query debe filtrar por `empresa_id` del usuario autenticado.

```sql
-- ❌ INCORRECTO
SELECT * FROM productos WHERE is_active = true;

-- ✅ CORRECTO
SELECT * FROM productos 
WHERE empresa_id = $1 AND is_active = true;
```

---

## 📝 Notas sobre Actualizaciones

- `updated_at` se actualiza automáticamente con trigger `ON UPDATE`.
- Cambios en `precio_costo` se registran en auditoría para trazabilidad.
- Los triggers deben ejecutarse en transacción ACID completa para garantizar consistencia stock/deuda.
