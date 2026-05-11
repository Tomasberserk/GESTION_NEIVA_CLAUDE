# API Contracts — Tier Basic

> Endpoints estándar para sistemas POS básicos.  
> Base URL: `http://localhost:8000` (dev) / `https://api.{dominio}` (prod)  
> Autenticación: Bearer JWT en header `Authorization: Bearer {token}`

---

## Auth

### POST /auth/registro
Crea empresa + usuario admin en una sola transacción.

**Request:**
```json
{
  "nombre_comercial": "Tienda Don Pedro",
  "nit_o_cedula": "12345678",
  "email": "admin@tienda.com",
  "password": "min8chars"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "email": "admin@tienda.com",
  "empresa_id": "uuid",
  "rol": "admin"
}
```

**Errores:** 409 si email o NIT ya existen, 422 si validación falla.

---

### POST /auth/login
Obtiene JWT. Formato OAuth2 form data.

**Request:** `application/x-www-form-urlencoded`
```
username=admin@tienda.com&password=min8chars
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
Devuelve usuario autenticado. Requiere JWT.

**Response 200:**
```json
{
  "id": "uuid",
  "email": "admin@tienda.com",
  "empresa_id": "uuid",
  "rol": "admin"
}
```

---

## Productos

Todos los endpoints filtran automáticamente por `empresa_id` del usuario autenticado.

### GET /productos/{empresa_id}
Lista productos activos. Requiere JWT.

**Query params:** `q` (búsqueda por nombre o barcode, opcional)

**Response 200:**
```json
[
  {
    "id": "uuid",
    "nombre": "Arroz Diana 500g",
    "codigo_barras": "7702057000016",
    "precio_venta": 3200,
    "cantidad_actual": 48,
    "foto_url": "/media/uuid.jpg"
  }
]
```

---

### POST /productos/{empresa_id}
Crea producto. Requiere rol admin.

**Request:** `multipart/form-data`
```
nombre: Arroz Diana 500g
codigo_barras: 7702057000016
precio_costo: 2800
precio_venta: 3200
cantidad_actual: 48
foto: [archivo opcional]
```

**Response 201:**
```json
{ "id": "uuid", "nombre": "...", ... }
```

**Errores:** 409 si barcode ya existe en la empresa.

---

### PUT /productos/{empresa_id}/{producto_id}
Actualiza producto. Requiere rol admin.

**Request:** mismos campos que POST (todos opcionales)

**Response 200:** producto actualizado completo.

---

### DELETE /productos/{empresa_id}/{producto_id}
Soft delete. Requiere rol admin.

**Response 200:** `{"ok": true}`

---

## Ventas

### POST /ventas/{empresa_id}
Registra venta. Descuenta stock con lock de fila. Requiere JWT.

**Request:**
```json
{
  "items": [
    {"producto_id": "uuid", "cantidad": 2}
  ]
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "total": 6400,
  "detalles": [
    {
      "producto_id": "uuid",
      "nombre": "Arroz Diana 500g",
      "cantidad": 2,
      "precio_unitario": 3200,
      "subtotal": 6400
    }
  ]
}
```

**Errores:** 400 si stock insuficiente, 404 si producto no existe.

---

### GET /ventas/{empresa_id}
Lista ventas con detalles. Requiere JWT.

**Query params:** `desde` (ISO date), `hasta` (ISO date), `skip`, `limit`

**Response 200:**
```json
[
  {
    "id": "uuid",
    "fecha_venta": "2026-05-11T14:30:00Z",
    "total": 6400,
    "detalles": [...]
  }
]
```

---

## Dashboard

### GET /dashboard/{empresa_id}
Métricas del día. Requiere JWT.

**Response 200:**
```json
{
  "ventas_hoy": 12,
  "ingresos_hoy": 145600.00,
  "total_productos": 87,
  "stock_bajo": [
    {"id": "uuid", "nombre": "Sal x 500g", "cantidad": 3}
  ]
}
```

---

## Reportes

### GET /reportes/{empresa_id}/excel
Exporta ventas a Excel. Requiere rol admin.

**Query params:** `desde` (ISO date requerido), `hasta` (ISO date requerido)

**Response 200:** archivo `.xlsx` con headers:
```
Fecha | Productos | Unidades | Total
```

**Content-Type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

---

## Convenciones generales

- Todos los IDs son UUIDs (strings)
- Fechas en ISO 8601 con timezone (UTC)
- Moneda en enteros (pesos colombianos, sin decimales en display)
- 401 = token ausente o inválido
- 403 = token válido pero sin permiso (rol insuficiente o empresa incorrecta)
- 422 = validación de schema fallida (detalle en `response.detail`)
