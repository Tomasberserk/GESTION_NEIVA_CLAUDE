# Schema — Tier Basic (patrón Gestión Neiva)

> Template de modelo de datos para sistemas POS simples.  
> Customizar los campos opcionales y las reglas de negocio para cada cliente.

---

## Entidades core

### Empresa (raíz multi-tenant)

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | Generado automáticamente |
| nombre_comercial | VARCHAR(150) | NOT NULL | Nombre del negocio |
| nit_o_cedula | VARCHAR(50) | UNIQUE NOT NULL | Identificación fiscal |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

**Notas de customización:** agregar `ciudad`, `telefono`, `plan_suscripcion` si el sistema necesita facturación o multi-plan.

---

### Usuario

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| email | VARCHAR(255) | UNIQUE NOT NULL | Login |
| hashed_password | VARCHAR | NOT NULL | bcrypt |
| rol | ENUM('admin', 'tendero') | NOT NULL | Control de acceso |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | Soft delete |

**Índices:** `idx_usuarios_email` en `email`

**Notas de customización:** agregar roles según el negocio (`supervisor`, `cajero`, `bodega`).

---

### Producto

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| nombre | VARCHAR | NOT NULL | |
| codigo_barras | VARCHAR(50) | NOT NULL | EAN-13, EAN-128, código interno |
| precio_costo | NUMERIC(10,2) | NOT NULL, default 0 | Costo de adquisición |
| precio_venta | NUMERIC(10,2) | NOT NULL, default 0 | Precio al público |
| cantidad_actual | INTEGER | NOT NULL, default 0 | Stock actual |
| foto_url | VARCHAR | NULL | Path en /media/ |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | Soft delete |

**Constraints:** `UNIQUE(empresa_id, codigo_barras)` — dos empresas pueden tener el mismo barcode  
**Índices:** `idx_productos_empresa` en `empresa_id`

**Notas de customización:** agregar `categoria`, `proveedor_id`, `stock_minimo` para alertas de reposición.

---

### Venta (documento maestro)

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| fecha_venta | TIMESTAMPTZ | NOT NULL, default now() | Momento de la venta |
| total | NUMERIC(10,2) | NOT NULL, default 0 | Total de la transacción |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | Soft delete (anulación) |

**Índices:** `idx_ventas_empresa_fecha` en `(empresa_id, fecha_venta)`

**Notas de customización:** agregar `cajero_id`, `metodo_pago`, `descuento`, `cliente_id` para sistemas más completos.

---

### DetalleVenta (línea de producto)

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| venta_id | UUID | FK ventas(id) CASCADE | |
| producto_id | UUID | FK productos(id) RESTRICT | No borrar producto con ventas |
| cantidad | INTEGER | NOT NULL | Unidades vendidas |
| precio_unitario | NUMERIC(10,2) | NOT NULL | **Snapshot** — no cambia si el precio cambia |
| subtotal | NUMERIC(10,2) | NOT NULL | cantidad × precio_unitario |
| created_at | TIMESTAMPTZ | | |
| updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | default true | |

**Índices:** `idx_detalles_venta_venta_id` en `venta_id`

---

## Relaciones

```
Empresa 1 ──< Usuario (cascade delete)
Empresa 1 ──< Producto (cascade delete)
Empresa 1 ──< Venta (cascade delete)
Venta 1 ──< DetalleVenta (cascade delete)
Producto 1 ──< DetalleVenta (RESTRICT delete)
```

---

## Enums

```python
class RolUsuario(str, enum.Enum):
    ADMIN = "admin"      # gestión completa
    TENDERO = "tendero"  # solo ventas e inventario
```

---

## Implementación de referencia

Ver `app/models.py` en el repo de Gestión Neiva para la implementación completa en SQLAlchemy.
