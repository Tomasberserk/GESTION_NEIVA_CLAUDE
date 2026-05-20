# API Contracts — POS Papelería Neiva

> Adaptado del template `factory/templates/basic/api-contracts.md`  
> Base URL: `http://localhost:8000` (dev) / `https://api.papeleria.{dominio}` (prod)  
> Autenticación: `Authorization: Bearer {token}` en todos los endpoints salvo `/auth/login` y `/auth/registro`

---

## Auth

### POST /auth/registro
Crea empresa + usuario admin en una sola transacción atómica.

**Request:**
```json
{
  "nombre_comercial": "Papelería El Estudiante",
  "nit_o_cedula": "12345678",
  "email": "admin@papeleria.com",
  "password": "min8chars"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "email": "admin@papeleria.com",
  "empresa_id": "uuid",
  "rol": "admin"
}
```

**Errores:** 409 si email o NIT ya existen · 422 si validación falla.

---

### POST /auth/login
Obtiene JWT. Formato OAuth2 form data.

**Request:** `application/x-www-form-urlencoded`
```
username=admin@papeleria.com&password=min8chars
```

**Response 200:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errores:** 401 si credenciales inválidas.

---

### GET /auth/me
Devuelve el usuario autenticado.

**Response 200:**
```json
{
  "id": "uuid",
  "email": "admin@papeleria.com",
  "empresa_id": "uuid",
  "rol": "admin"
}
```

---

## Usuarios

> Solo admin puede gestionar usuarios.

### GET /usuarios/{empresa_id}
Lista usuarios de la empresa. Requiere rol admin.

**Response 200:**
```json
[
  {
    "id": "uuid",
    "email": "tendero1@papeleria.com",
    "rol": "tendero",
    "is_active": true
  }
]
```

---

### POST /usuarios/{empresa_id}
Crea un usuario (tendero). Requiere rol admin.

**Request:**
```json
{
  "email": "tendero1@papeleria.com",
  "password": "min8chars",
  "rol": "tendero"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "email": "tendero1@papeleria.com",
  "rol": "tendero"
}
```

**Errores:** 409 si email ya existe · 403 si no es admin.

---

### DELETE /usuarios/{empresa_id}/{usuario_id}
Soft delete de usuario. Requiere rol admin.

**Response 200:** `{"ok": true}`

**Errores:** 403 si intenta desactivar su propia cuenta.

---

## Productos

> Todos los endpoints filtran por `empresa_id` del usuario autenticado.

### GET /productos/{empresa_id}
Lista productos activos. Requiere JWT.

**Query params:**
- `q` — búsqueda por nombre o código de barras (opcional)
- `categoria` — filtra por categoría (opcional, ver enum)
- `stock_bajo` — `true` para mostrar solo productos con `cantidad_actual <= stock_minimo` (opcional)
- `skip` — paginación offset (default 0)
- `limit` — paginación tamaño (default 50)

**Response 200:**
```json
[
  {
    "id": "uuid",
    "nombre": "Cuaderno cuadriculado 100h",
    "codigo_barras": "7702057000016",
    "precio_venta": 4500,
    "cantidad_actual": 30,
    "unidad_medida": "unidad",
    "categoria": "Utiles escolares",
    "stock_minimo": 5,
    "foto_url": "/media/uuid.jpg",
    "is_active": true
  }
]
```

---

### POST /productos/{empresa_id}
Crea producto. Requiere rol admin.

**Request:** `multipart/form-data`
```
nombre: Cuaderno cuadriculado 100h
codigo_barras: 7702057000016
precio_costo: 3200
precio_venta: 4500
cantidad_actual: 30
unidad_medida: unidad
categoria: Utiles escolares
stock_minimo: 5
foto: [archivo opcional — jpg/png/webp, max 2MB]
```

**Response 201:**
```json
{
  "id": "uuid",
  "nombre": "Cuaderno cuadriculado 100h",
  "codigo_barras": "7702057000016",
  "precio_costo": 3200,
  "precio_venta": 4500,
  "cantidad_actual": 30,
  "unidad_medida": "unidad",
  "categoria": "Utiles escolares",
  "stock_minimo": 5,
  "foto_url": "/media/uuid.jpg"
}
```

**Errores:** 409 si barcode ya existe en la empresa · 403 si no es admin · 422 si validación falla.

---

### PUT /productos/{empresa_id}/{producto_id}
Actualiza producto. Requiere rol admin.

**Request:** `multipart/form-data` — todos los campos son opcionales.

**Response 200:** producto completo actualizado.

**Errores:** 404 si no existe · 409 si barcode nuevo ya está en uso.

---

### DELETE /productos/{empresa_id}/{producto_id}
Soft delete (`is_active = false`). Requiere rol admin.

**Response 200:** `{"ok": true}`

**Errores:** 404 si no existe.

---

## Ventas

### POST /ventas/{empresa_id}
Registra venta. Descuenta stock con SELECT FOR UPDATE (lock de fila). Requiere JWT.

El `usuario_id` se toma automáticamente del JWT — el cajero autenticado queda registrado.

**Request:**
```json
{
  "items": [
    {"producto_id": "uuid", "cantidad": 3},
    {"producto_id": "uuid", "cantidad": 1}
  ]
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "empresa_id": "uuid",
  "usuario_id": "uuid",
  "fecha_venta": "2026-05-17T10:30:00Z",
  "total": 18000,
  "detalles": [
    {
      "producto_id": "uuid",
      "nombre": "Cuaderno cuadriculado 100h",
      "cantidad": 3,
      "precio_unitario": 4500,
      "subtotal": 13500
    },
    {
      "producto_id": "uuid",
      "nombre": "Lapicero BIC azul",
      "cantidad": 1,
      "precio_unitario": 4500,
      "subtotal": 4500
    }
  ]
}
```

**Errores:** 400 si stock insuficiente (incluye nombre del producto afectado) · 404 si producto no existe · 422 si items vacíos.

---

### GET /ventas/{empresa_id}
Lista ventas con detalles. Requiere JWT.

**Query params:**
- `desde` — ISO date (ej. `2026-05-01`)
- `hasta` — ISO date (ej. `2026-05-17`)
- `usuario_id` — filtra por cajero (solo admin puede filtrar por otro usuario)
- `skip` — default 0
- `limit` — default 50

**Response 200:**
```json
[
  {
    "id": "uuid",
    "fecha_venta": "2026-05-17T10:30:00Z",
    "usuario_id": "uuid",
    "usuario_email": "tendero1@papeleria.com",
    "total": 18000,
    "detalles": [
      {
        "producto_id": "uuid",
        "nombre": "Cuaderno cuadriculado 100h",
        "cantidad": 3,
        "precio_unitario": 4500,
        "subtotal": 13500
      }
    ]
  }
]
```

---

## Dashboard

### GET /dashboard/{empresa_id}
KPIs del día + alertas de stock bajo. Requiere JWT.

`stock_bajo` lista productos donde `cantidad_actual <= stock_minimo`.

**Response 200:**
```json
{
  "ventas_hoy": 8,
  "ingresos_hoy": 87500.00,
  "total_productos_activos": 142,
  "stock_bajo": [
    {
      "id": "uuid",
      "nombre": "Pegante Colbón pequeño",
      "categoria": "Utiles escolares",
      "cantidad_actual": 3,
      "stock_minimo": 5
    }
  ]
}
```

---

## Reportes

### GET /reportes/{empresa_id}/excel
Exporta ventas a Excel por rango de fechas. Requiere rol admin.

**Query params:**
- `desde` — ISO date requerido (ej. `2026-05-01`)
- `hasta` — ISO date requerido (ej. `2026-05-17`)

**Response 200:** archivo `.xlsx`

Columnas del Excel:
```
Fecha | Cajero | Producto | Categoría | Cantidad | Precio Unitario | Subtotal | Total Venta
```

**Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`  
**Content-Disposition:** `attachment; filename="ventas_{desde}_{hasta}.xlsx"`

**Errores:** 400 si `desde` > `hasta` · 403 si no es admin.

---

## Convenciones generales

| Convención | Detalle |
|-----------|---------|
| IDs | UUIDs (strings) en todas las tablas |
| Fechas | ISO 8601 con timezone UTC (`2026-05-17T10:30:00Z`) |
| Moneda | `NUMERIC(10,2)` en BD; pesos colombianos sin símbolo en respuestas |
| Paginación | `skip` + `limit` en endpoints de lista |
| 401 | Token ausente o inválido |
| 403 | Token válido pero rol insuficiente o empresa incorrecta |
| 404 | Recurso no existe o está soft-deleted |
| 409 | Conflicto de unicidad (email, NIT, barcode) |
| 422 | Validación de schema fallida — detalle en `response.detail` |

### Permisos por rol

| Endpoint | admin | tendero |
|----------|-------|---------|
| GET /productos | ✓ | ✓ |
| POST/PUT/DELETE /productos | ✓ | ✗ |
| POST /ventas | ✓ | ✓ |
| GET /ventas (propias) | ✓ | ✓ |
| GET /ventas (filtro usuario_id otro) | ✓ | ✗ |
| GET /dashboard | ✓ | ✓ |
| GET /reportes/excel | ✓ | ✗ |
| POST/DELETE /usuarios | ✓ | ✗ |
