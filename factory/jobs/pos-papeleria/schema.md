# Schema — POS Papelería Neiva

> Modelo de datos adaptado del tier basic.  
> Referencia base: `factory/templates/basic/schema.md`  
> Diferencias aplicadas: `requirements.json > diferencias_vs_gestion_neiva`

---

## Entidades

### Empresa (raíz multi-tenant)

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | Generado automáticamente |
| nombre_comercial | VARCHAR(150) | NOT NULL | Nombre de la papelería |
| nit_o_cedula | VARCHAR(50) | UNIQUE NOT NULL | Identificación fiscal |
| plan | VARCHAR(50) | NOT NULL, default 'basic' | Plan de suscripción |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | Auditoría |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

---

### Usuario

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| email | VARCHAR(255) | UNIQUE NOT NULL | Login |
| hashed_password | VARCHAR | NOT NULL | bcrypt |
| rol | ENUM('admin', 'tendero') | NOT NULL | Control de acceso |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

**Índices:** `idx_usuarios_email` en `email`, `idx_usuarios_empresa` en `empresa_id`

**Capacidad:** 1 admin (dueño) + 2 tenderos (empleados) = 3 usuarios total en plan basic.

---

### Producto

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| nombre | VARCHAR(255) | NOT NULL | Nombre del artículo |
| codigo_barras | VARCHAR(50) | NOT NULL | EAN-13 o código interno |
| precio_costo | NUMERIC(10,2) | NOT NULL, default 0 | Costo de adquisición |
| precio_venta | NUMERIC(10,2) | NOT NULL, default 0 | Precio al público |
| cantidad_actual | INTEGER | NOT NULL, default 0 | Stock actual |
| unidad_medida | ENUM('unidad', 'paquete') | NOT NULL, default 'unidad' | Unidad de manejo |
| categoria | ENUM(...) | NOT NULL | Ver enums abajo |
| stock_minimo | INTEGER | NOT NULL, default 5 | Umbral de alerta de stock bajo |
| foto_url | VARCHAR | NULL | Path en /media/ |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete |

**Constraints:** `UNIQUE(empresa_id, codigo_barras)` — dos empresas pueden tener el mismo barcode  
**Índices:** `idx_productos_empresa` en `empresa_id`, `idx_productos_stock_bajo` en `(empresa_id, cantidad_actual, stock_minimo)`

**Diferencias vs Gestión Neiva:**
- `stock_minimo` es configurable por producto (default 5, no hardcodeado en 10)
- `unidad_medida` solo acepta `unidad` y `paquete` (sin gramo, libra, kilo)
- `categoria` usa categorías de papelería
- Sin `fecha_vencimiento`

---

### Venta (documento maestro)

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| empresa_id | UUID | FK empresas(id) CASCADE | Multi-tenant |
| usuario_id | UUID | FK usuarios(id) RESTRICT | Cajero que realizó la venta |
| fecha_venta | TIMESTAMPTZ | NOT NULL, default now() | Momento de la transacción |
| total | NUMERIC(10,2) | NOT NULL, default 0 | Total de la transacción |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | Soft delete (anulación) |

**Índices:** `idx_ventas_empresa_fecha` en `(empresa_id, fecha_venta)`, `idx_ventas_usuario` en `usuario_id`

**Diferencia vs Gestión Neiva:** `usuario_id` es requerido — registra qué empleado hizo cada venta.

---

### DetalleVenta (línea de producto)

| Columna | Tipo | Constraint | Descripción |
|---------|------|-----------|-------------|
| id | UUID | PK | |
| venta_id | UUID | FK ventas(id) CASCADE | |
| producto_id | UUID | FK productos(id) RESTRICT | No borrar producto con ventas |
| cantidad | INTEGER | NOT NULL | Unidades vendidas |
| precio_unitario | NUMERIC(10,2) | NOT NULL | Snapshot — no cambia si el precio cambia |
| subtotal | NUMERIC(10,2) | NOT NULL | cantidad × precio_unitario |
| created_at | TIMESTAMPTZ | NOT NULL, default now() | |
| updated_at | TIMESTAMPTZ | NOT NULL, default now() | |
| is_active | BOOLEAN | NOT NULL, default true | |

**Índices:** `idx_detalles_venta_venta_id` en `venta_id`

---

## Relaciones

```
Empresa  1 ──< Usuario      (cascade delete)
Empresa  1 ──< Producto     (cascade delete)
Empresa  1 ──< Venta        (cascade delete)
Usuario  1 ──< Venta        (RESTRICT delete — no borrar cajero con ventas)
Venta    1 ──< DetalleVenta (cascade delete)
Producto 1 ──< DetalleVenta (RESTRICT delete — no borrar producto con ventas)
```

---

## Enums

```python
class RolUsuario(str, enum.Enum):
    ADMIN   = "admin"    # gestión completa: CRUD productos, ver reportes, exportar
    TENDERO = "tendero"  # solo ventas e inventario (lectura)

class UnidadMedida(str, enum.Enum):
    UNIDAD  = "unidad"
    PAQUETE = "paquete"

class CategoriaProducto(str, enum.Enum):
    UTILES_ESCOLARES = "Utiles escolares"
    PAPEL_Y_RESMAS   = "Papel y resmas"
    TECNOLOGIA       = "Tecnologia"
    SERVICIOS        = "Servicios"
    MISCELANEA       = "Miscelanea"
```

---

## Reglas de negocio aplicadas al schema

| Regla | Implementación |
|-------|---------------|
| Stock bajo = `cantidad_actual <= stock_minimo` | Comparación en query del dashboard, `stock_minimo` almacenado en tabla |
| Snapshot de precio | `precio_unitario` en `DetalleVenta`, no FK a tabla de precios |
| Soft delete | `is_active = false` en todas las tablas, nunca DELETE |
| Multi-tenant | `empresa_id` en Producto, Venta (DetalleVenta hereda vía JOIN) |
| Trazabilidad de cajero | `usuario_id` NOT NULL en Venta |
| Barcode único por empresa | `UNIQUE(empresa_id, codigo_barras)` en Producto |

---

## Checklist de validación

- [x] Todas las tablas tienen `empresa_id` (directo o heredado por FK)
- [x] Todas las tablas tienen `is_active` (soft delete)
- [x] `Venta` registra `usuario_id` (qué cajero vendió)
- [x] `Producto` tiene `stock_minimo` como campo configurable (default 5)
- [x] Sin `fecha_vencimiento` (no aplica a papelería)
- [x] Sin unidades de peso (`unidad_medida` solo acepta `unidad` y `paquete`)
- [x] Categorías específicas de papelería
