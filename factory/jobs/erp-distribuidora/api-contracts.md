# API Contracts — ERP Distribuidora (Tier Medium)

> Especificación de endpoints REST para **Distribuidora Mayorista de Abarrotes y Papelería**.  
> Extiende la API básica (Gestión Neiva) con endpoints de Proveedores, Compras y Cuentas por Pagar.
>
> **Autenticación:** Bearer JWT en header `Authorization: Bearer {token}`  
> **Base URL:** `http://localhost:8000` (desarrollo) | `https://api.erp-distribuidora.com` (producción)  
> **Multi-tenant:** Todos los endpoints filtran implícitamente por `empresa_id` del usuario autenticado.

---

## 📋 Convenciones

- **Status Codes:** 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 409 (Conflict), 422 (Unprocessable Entity), 500 (Internal Server Error)
- **Timestamps:** ISO 8601 formato UTC (ej. `2026-05-21T14:30:00Z`)
- **Decimales:** NUMERIC(12,2) para dinero, NUMERIC(10,3) para cantidades con decimales
- **Paginación:** Query params `skip` (default 0) y `limit` (default 100, máximo 1000)

---

## 🔐 Autenticación (Heredada de Gestión Neiva)

### POST /auth/registro-completo
Registra una nueva distribuidora y administrador.

**Request:**
```json
{
  "nombre_comercial": "Distribuidora Mayorista de Abarrotes y Papelería",
  "nit_o_cedula": "860123456-7",
  "email": "admin@distrimayorista.com",
  "password": "SecurePass123!",
  "rol": "admin"
}
```

**Response 201:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@distrimayorista.com",
    "empresa_id": "665e8400-e29b-41d4-a716-446655440111",
    "rol": "admin"
  }
}
```

---

### POST /token
Login de usuario existente.

**Request:**
```json
{
  "email": "admin@distrimayorista.com",
  "password": "SecurePass123!"
}
```

**Response 200:** (Idéntica a registro-completo)

---

### GET /me
Obtiene el perfil del usuario autenticado.

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@distrimayorista.com",
  "empresa_id": "665e8400-e29b-41d4-a716-446655440111",
  "rol": "admin"
}
```

---

## 👥 Proveedores

Todos los endpoints filtran por `empresa_id` del usuario autenticado (multi-tenant implícito).

### GET /api/proveedores
Lista proveedores activos de la distribuidora.

**Query Params:**
- `q` (opcional): Búsqueda por razón social, NIT o contacto (búsqueda fuzzy)
- `skip` (opcional, default 0): Paginación
- `limit` (opcional, default 100): Tamaño de página

**Response 200:**
```json
{
  "total": 45,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "nit_o_cedula": "890102030-9",
      "razon_social": "Distribuidora Nacional de Papelería S.A.S.",
      "contacto_nombre": "Carlos Mendoza",
      "telefono": "+57 315 123 4567",
      "email": "ventas@distrinacional.com",
      "direccion": "Calle 10 # 4-50, Bogotá",
      "is_active": true
    },
    {
      "id": "4gb96f75-6828-4673-c4gd-3d074g77bfg7",
      "nit_o_cedula": "800123456-1",
      "razon_social": "Abarrotes y Víveres La Nacional",
      "contacto_nombre": "María García",
      "telefono": "+57 310 654 3210",
      "email": "compras@abarrotesnacional.com",
      "direccion": "Carrera 7 # 50-10, Medellín",
      "is_active": true
    }
  ]
}
```

---

### POST /api/proveedores
Registra un nuevo proveedor.

**Request:**
```json
{
  "nit_o_cedula": "890102030-9",
  "razon_social": "Distribuidora Nacional de Papelería S.A.S.",
  "contacto_nombre": "Carlos Mendoza",
  "telefono": "+57 315 123 4567",
  "email": "ventas@distrinacional.com",
  "direccion": "Calle 10 # 4-50, Bogotá"
}
```

**Response 201:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "nit_o_cedula": "890102030-9",
  "razon_social": "Distribuidora Nacional de Papelería S.A.S.",
  "contacto_nombre": "Carlos Mendoza",
  "telefono": "+57 315 123 4567",
  "email": "ventas@distrinacional.com",
  "direccion": "Calle 10 # 4-50, Bogotá",
  "is_active": true
}
```

**Errores:**
- `409 Conflict`: Proveedor con ese NIT ya existe para esta empresa.
- `422 Unprocessable Entity`: Error de validación (email inválido, formato teléfono, etc.).

---

### PUT /api/proveedores/{proveedor_id}
Actualiza datos de un proveedor.

**Request:** (Campos opcionales)
```json
{
  "contacto_nombre": "Carlos Alberto Mendoza",
  "telefono": "+57 315 765 4321",
  "email": "carlos@distrinacional.com"
}
```

**Response 200:** Proveedor actualizado

**Errores:**
- `404 Not Found`: Proveedor no existe o no pertenece a tu empresa.
- `409 Conflict`: El nuevo NIT ya existe en otra empresa.

---

### DELETE /api/proveedores/{proveedor_id}
Soft delete de un proveedor.

**Response 200:**
```json
{
  "ok": true,
  "message": "Proveedor desactivado correctamente"
}
```

**Errores:**
- `400 Bad Request`: Proveedor tiene compras o deudas activas registradas.
- `404 Not Found`: Proveedor no existe.

---

## 📦 Compras (Abastecimiento)

### GET /api/compras
Historial de facturas/compras a proveedores.

**Query Params:**
- `desde` (opcional): ISO date (ej. `2026-05-01T00:00:00Z`)
- `hasta` (opcional): ISO date (ej. `2026-05-31T23:59:59Z`)
- `proveedor_id` (opcional): UUID del proveedor
- `estado` (opcional): PAGADA | PENDIENTE | ANULADA
- `skip` (opcional, default 0)
- `limit` (opcional, default 100)

**Response 200:**
```json
{
  "total": 23,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "numero_factura": "FAC-8973",
      "fecha_compra": "2026-05-21T18:00:00Z",
      "metodo_pago": "CREDITO",
      "fecha_vencimiento": "2026-06-21T18:00:00Z",
      "estado": "PENDIENTE",
      "total": 1250000.00,
      "proveedor": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "razon_social": "Distribuidora Nacional de Papelería S.A.S."
      },
      "usuario": {
        "id": "871b56a4-6512-42da-9fca-3269b2d87e1a",
        "email": "admin@distrimayorista.com"
      }
    }
  ]
}
```

---

### POST /api/compras
Registra una compra e incrementa stock automáticamente.

**Request:**
```json
{
  "proveedor_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "numero_factura": "FAC-8973",
  "metodo_pago": "CREDITO",
  "fecha_vencimiento": "2026-06-21T18:00:00Z",
  "items": [
    {
      "producto_id": "550b8400-e29b-41d4-a716-446655440000",
      "cantidad": 100.00,
      "precio_costo": 12500.00
    },
    {
      "producto_id": "660c9511-f39c-52e5-b827-557766551111",
      "cantidad": 50.00,
      "precio_costo": 8500.00
    }
  ]
}
```

**Notas:**
- `numero_factura` es el número de factura del proveedor (puede repetirse si es de diferente proveedor).
- `fecha_vencimiento` es **obligatoria** si `metodo_pago = 'CREDITO'`.
- `items` es un array no vacío de productos con cantidad y costo pactado.

**Response 201:**
```json
{
  "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "numero_factura": "FAC-8973",
  "fecha_compra": "2026-05-21T18:00:00Z",
  "metodo_pago": "CREDITO",
  "fecha_vencimiento": "2026-06-21T18:00:00Z",
  "estado": "PENDIENTE",
  "total": 1700000.00,
  "detalles": [
    {
      "id": "aa1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "producto_id": "550b8400-e29b-41d4-a716-446655440000",
      "nombre": "Cuaderno Espiral Norma 100h",
      "cantidad": 100.00,
      "precio_costo": 12500.00,
      "subtotal": 1250000.00
    },
    {
      "id": "bb2efc5e-4c8e-5cbe-0a8e-3c0e8e4ecd7e",
      "producto_id": "660c9511-f39c-52e5-b827-557766551111",
      "nombre": "Papel Bond A4 Resma 500h",
      "cantidad": 50.00,
      "precio_costo": 8500.00,
      "subtotal": 425000.00
    }
  ],
  "cuenta_por_pagar_id": "aa7b822d-bb4b-4b11-9a7c-3f92a106f366"
}
```

**Efectos Colaterales (Transacción ACID):**
1. Crea registro `Compra` en estado `PENDIENTE` (si es crédito) o `PAGADA` (si es efectivo/transferencia).
2. Crea registros `DetalleCompra` para cada item.
3. **Incrementa stock:** `Producto.cantidad_actual += DetalleCompra.cantidad`
4. **Actualiza costo:** `Producto.precio_costo = DetalleCompra.precio_costo` (último comprado)
5. **Si es crédito:** Crea `CuentaPorPagar` automáticamente.
6. Responde con `cuenta_por_pagar_id` para que el cliente lo pueda usar después.

**Errores:**
- `400 Bad Request`: Proveedor no existe, producto no existe, items vacío, fecha_vencimiento faltante en crédito.
- `404 Not Found`: Proveedor o producto no pertenecen a la empresa.
- `422 Unprocessable Entity`: Cantidad o precio inválidos.

---

### GET /api/compras/{compra_id}
Obtiene detalle completo de una compra.

**Response 200:**
```json
{
  "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "numero_factura": "FAC-8973",
  "fecha_compra": "2026-05-21T18:00:00Z",
  "metodo_pago": "CREDITO",
  "fecha_vencimiento": "2026-06-21T18:00:00Z",
  "estado": "PENDIENTE",
  "total": 1700000.00,
  "detalles": [
    {
      "id": "aa1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "producto_id": "550b8400-e29b-41d4-a716-446655440000",
      "nombre": "Cuaderno Espiral Norma 100h",
      "cantidad": 100.00,
      "precio_costo": 12500.00,
      "subtotal": 1250000.00
    }
  ],
  "proveedor": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "razon_social": "Distribuidora Nacional de Papelería S.A.S."
  },
  "usuario": {
    "id": "871b56a4-6512-42da-9fca-3269b2d87e1a",
    "email": "admin@distrimayorista.com"
  }
}
```

---

### DELETE /api/compras/{compra_id}
Anula una compra y reversa stock automáticamente.

**Response 200:**
```json
{
  "ok": true,
  "message": "Compra anulada e inventario reversado correctamente",
  "stock_reversado": {
    "550b8400-e29b-41d4-a716-446655440000": -100.00,
    "660c9511-f39c-52e5-b827-557766551111": -50.00
  }
}
```

**Efectos Colaterales (Transacción ACID):**
1. Marca `Compra.is_active = False` (soft delete) y `Compra.estado = 'ANULADA'`.
2. Marca `DetalleCompra.is_active = False`.
3. **Reversa stock:** `Producto.cantidad_actual -= DetalleCompra.cantidad`
4. **Valida stock:** Si algún producto quedaría en cantidad negativa (mercancía ya vendida), rechaza con `400 Bad Request`.
5. **Si hay CuentaPorPagar:** La marca como inactiva y sus abonos también.

**Errores:**
- `400 Bad Request`: No se puede reversar, stock insuficiente (mercancía ya vendida).
- `404 Not Found`: Compra no existe.

---

## 💰 Cuentas por Pagar (Módulo Financiero)

**Restricción de Rol:** Solo `admin` puede acceder a estos endpoints. El rol `asistente` recibirá `403 Forbidden`.

### GET /api/cuentas-por-pagar
Lista de obligaciones financieras con proveedores.

**Query Params:**
- `estado` (opcional): PENDIENTE | PAGADA | VENCIDA
- `proveedor_id` (opcional): UUID del proveedor
- `vence_antes` (opcional): ISO date (alertas de vencimientos próximos)
- `skip` (opcional, default 0)
- `limit` (opcional, default 100)

**Response 200:**
```json
{
  "total": 12,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "id": "aa7b822d-bb4b-4b11-9a7c-3f92a106f366",
      "compra_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "monto_total": 1250000.00,
      "saldo_pendiente": 750000.00,
      "fecha_vencimiento": "2026-06-21T18:00:00Z",
      "estado": "PENDIENTE",
      "proveedor": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "razon_social": "Distribuidora Nacional de Papelería S.A.S.",
        "telefono": "+57 315 123 4567"
      },
      "dias_para_vencimiento": 31
    }
  ]
}
```

**Computables en Frontend:**
- `dias_para_vencimiento = (fecha_vencimiento - ahora) / 86400`
- Color rojo si `dias_para_vencimiento < 0` (vencida)
- Color amarillo si `0 < dias_para_vencimiento < 7` (próxima a vencer)

---

### POST /api/cuentas-por-pagar/{cxp_id}/abonos
Registra un pago/abono a una deuda.

**Request:**
```json
{
  "monto": 500000.00,
  "metodo_pago": "TRANSFERENCIA",
  "nota": "Transferencia Bancolombia Ref: #48109"
}
```

**Response 201:**
```json
{
  "id": "e309cb42-bb44-4822-b91b-c6b758b29c91",
  "cuenta_por_pagar_id": "aa7b822d-bb4b-4b11-9a7c-3f92a106f366",
  "monto": 500000.00,
  "fecha_abono": "2026-05-21T19:15:00Z",
  "metodo_pago": "TRANSFERENCIA",
  "nota": "Transferencia Bancolombia Ref: #48109",
  "nuevo_saldo_pendiente": 750000.00,
  "estado_obligacion": "PENDIENTE"
}
```

**Efectos Colaterales (Transacción ACID):**
1. Crea `AbonoCuentaPorPagar`.
2. Amortiza: `CuentaPorPagar.saldo_pendiente -= Abono.monto`
3. **Si `saldo_pendiente == 0.00`:**
   - Cambia `CuentaPorPagar.estado = 'PAGADA'`
   - Cambia `Compra.estado = 'PAGADA'` (compra completamente saldada)
4. Retorna nuevo saldo y estado actualizado.

**Errores:**
- `400 Bad Request`: Monto del abono > saldo_pendiente, monto ≤ 0, CuentaPorPagar no existe.
- `403 Forbidden`: Usuario no es admin.
- `404 Not Found`: CuentaPorPagar no existe o no pertenece a la empresa.

---

### GET /api/cuentas-por-pagar/{cxp_id}/abonos
Lista el historial de abonos de una deuda.

**Response 200:**
```json
{
  "cuenta_por_pagar_id": "aa7b822d-bb4b-4b11-9a7c-3f92a106f366",
  "abonos": [
    {
      "id": "e309cb42-bb44-4822-b91b-c6b758b29c91",
      "monto": 500000.00,
      "fecha_abono": "2026-05-21T19:15:00Z",
      "metodo_pago": "TRANSFERENCIA",
      "nota": "Transferencia Bancolombia Ref: #48109"
    },
    {
      "id": "f410dcb53-cc55-5933-c02c-d7c767d30ab2",
      "monto": 250000.00,
      "fecha_abono": "2026-05-28T10:30:00Z",
      "metodo_pago": "EFECTIVO",
      "nota": "Pago en persona, Cristina"
    }
  ]
}
```

---

### DELETE /api/cuentas-por-pagar/abonos/{abono_id}
Reversa un abono registrado.

**Response 200:**
```json
{
  "ok": true,
  "message": "Abono reversado correctamente, saldo pendiente restaurado",
  "nuevo_saldo_pendiente": 1250000.00,
  "estado_obligacion": "PENDIENTE"
}
```

**Efectos Colaterales (Transacción ACID):**
1. Marca `AbonoCuentaPorPagar.is_active = False` (soft delete).
2. Restaura: `CuentaPorPagar.saldo_pendiente += Abono.monto`
3. **Degrada estado:**
   - Si `CuentaPorPagar.estado == 'PAGADA'` → vuelve a `'PENDIENTE'`
   - Si `CuentaPorPagar.estado == 'VENCIDA'` → se mantiene `'VENCIDA'`
4. Degrada `Compra.estado` a `'PENDIENTE'` si era `'PAGADA'`.

**Errores:**
- `403 Forbidden`: Usuario no es admin.
- `404 Not Found`: Abono no existe.

---

## 📊 Dashboard (Resumen Financiero)

### GET /api/dashboard/kpis
KPIs consolidados de la distribuidora (solo admin).

**Query Params:**
- `desde` (opcional): ISO date
- `hasta` (opcional): ISO date

**Response 200:**
```json
{
  "periodo": {
    "desde": "2026-05-01T00:00:00Z",
    "hasta": "2026-05-31T23:59:59Z"
  },
  "resumen_financiero": {
    "compras_totales": 5500000.00,
    "deudas_activas": 2750000.00,
    "deudas_vencidas": 500000.00,
    "pagos_realizados": 2250000.00,
    "efectivo_entrada": 3000000.00,
    "promedio_dias_pago": 28
  },
  "inventario": {
    "total_items": 340,
    "valor_total_stock": 12450000.00,
    "rotacion_promedio_dias": 14
  },
  "proveedores": {
    "total_activos": 45,
    "con_deuda_activa": 12,
    "con_deuda_vencida": 3
  }
}
```

---

## 🔍 Filtros Multi-Tenant Implícitos

**Todos los endpoints aplican automáticamente:**
```
WHERE empresa_id = user.empresa_id AND is_active = true
```

No es necesario que el cliente lo especifique, se extrae del JWT.

---

## ⚠️ Códigos de Error Globales

| Código | Ejemplo |
|--------|---------|
| 200 | Operación exitosa |
| 201 | Recurso creado |
| 204 | Sin contenido (delete exitoso) |
| 400 | Solicitud malformada, validación fallida |
| 401 | Token expirado o ausente |
| 403 | Permiso denegado (ej. asistente accediendo Cuentas por Pagar) |
| 404 | Recurso no encontrado |
| 409 | Conflicto (ej. NIT duplicado) |
| 422 | Error de validación en campos |
| 500 | Error interno del servidor |

---

## 📝 Notas de Implementación

1. **Transacciones ACID:** Todos los efectos colaterales (stock, deuda, estado) deben ejecutarse en una transacción para evitar inconsistencias.
2. **Validación de Rol:** Implementar middleware que rechace acceso a Cuentas por Pagar para `rol = 'asistente'`.
3. **Cálculo de `dias_para_vencimiento`:** Computar en backend para mayor exactitud temporal.
4. **Alertas de Vencimiento:** Frontend debe renderizar en rojo si `estado = 'VENCIDA'` o `dias_para_vencimiento < 0`.
5. **Rate Limiting:** Implementar límites por IP/usuario para evitar abuse (ej. 100 requests/min).
