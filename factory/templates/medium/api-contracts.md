# API Contracts — Tier Medium

> Endpoints estándar para sistemas ERP Ligeros.  
> Amplía la API básica incorporando compras, proveedores y gestión de deudas.  
> Autenticación: Bearer JWT en header `Authorization: Bearer {token}`.

---

## Proveedores

Todos los endpoints filtran por la `empresa_id` del usuario autenticado (multi-tenant implícito).

### GET /api/proveedores
Lista los proveedores activos de la empresa.

**Query params:** `q` (búsqueda por razón social, nit o contacto, opcional)

**Response 200:**
```json
[
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
]
```

---

### POST /api/proveedores
Registra un nuevo proveedor en la empresa.

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
- `409 Conflict`: Proveedor con ese `nit_o_cedula` ya registrado para esta empresa.
- `422 Unprocessable Entity`: Error de validación en campos.

---

### PUT /api/proveedores/{proveedor_id}
Actualiza los datos de un proveedor.

**Request:** (Cualquier campo de creación es opcional)
```json
{
  "contacto_nombre": "Carlos Alberto Mendoza",
  "telefono": "+57 315 765 4321"
}
```

**Response 200:** Proveedor con datos actualizados.

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
- `400 Bad Request`: Si el proveedor tiene compras o deudas activas registradas (por integridad referencial RESTRICT).

---

## Compras (Abastecimiento)

### GET /api/compras
Historial de facturas/compras a proveedores.

**Query Params:**
- `desde`: ISO date (opcional)
- `hasta`: ISO date (opcional)
- `proveedor_id`: UUID (opcional)
- `estado`: ENUM `PAGADA`, `PENDIENTE`, `ANULADA` (opcional)

**Response 200:**
```json
[
  {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "numero_factura": "FAC-8973",
    "fecha_compra": "2026-05-21T18:00:00Z",
    "metodo_pago": "CREDITO",
    "estado": "PENDIENTE",
    "total": 1250000.00,
    "proveedor": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "razon_social": "Distribuidora Nacional de Papelería S.A.S."
    },
    "usuario": {
      "id": "871b56a4-6512-42da-9fca-3269b2d87e1a",
      "email": "admin@tienda.com"
    }
  }
]
```

---

### POST /api/compras
Registra una compra y actualiza el stock y costo base en el inventario.

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
    }
  ]
}
```
*Nota: `fecha_vencimiento` es obligatoria únicamente si `metodo_pago = 'CREDITO'`.*

**Response 201:**
```json
{
  "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "numero_factura": "FAC-8973",
  "fecha_compra": "2026-05-21T18:00:00Z",
  "metodo_pago": "CREDITO",
  "estado": "PENDIENTE",
  "total": 1250000.00,
  "detalles": [
    {
      "producto_id": "550b8400-e29b-41d4-a716-446655440000",
      "nombre": "Cuaderno Espiral Norma 100h",
      "cantidad": 100.00,
      "precio_costo": 12500.00,
      "subtotal": 1250000.00
    }
  ],
  "cuenta_por_pagar_id": "aa7b822d-bb4b-4b11-9a7c-3f92a106f366" 
}
```

**Efectos colaterales en base de datos:**
1. Aumenta stock del producto `550b8400-e29b-41d4-a716-446655440000` en +100 unidades.
2. Actualiza `precio_costo` del producto a `$12,500.00`.
3. Crea un registro en `cuentas_por_pagar` por valor de `$1,250,000.00` con vencimiento al `21-Junio-2026`.

---

### DELETE /api/compras/{compra_id}
Anula una compra (Soft Delete).

**Response 200:**
```json
{
  "ok": true,
  "message": "Compra anulada e inventario reversado correctamente"
}
```

**Efectos colaterales:**
1. Descuenta del inventario las cantidades ingresadas en la compra. Si el stock actual es insuficiente para reversar la compra (es decir, ya se vendió la mercancía), lanzará un error 400.
2. Si la compra estaba a `CREDITO`, la `CuentaPorPagar` asociada y sus abonos se marcan como inactivos/anulados.

---

## Cuentas por Pagar (Módulo Financiero)

### GET /api/cuentas-por-pagar
Lista las obligaciones financieras con proveedores.

**Query Params:**
- `estado`: ENUM `PENDIENTE`, `PAGADA`, `VENCIDA` (opcional)
- `proveedor_id`: UUID (opcional)
- `vence_antes`: ISO date (útil para alertas de vencimientos próximos, opcional)

**Response 200:**
```json
[
  {
    "id": "aa7b822d-bb4b-4b11-9a7c-3f92a106f366",
    "compra_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "monto_total": 1250000.00,
    "saldo_pendiente": 1250000.00,
    "fecha_vencimiento": "2026-06-21T18:00:00Z",
    "estado": "PENDIENTE",
    "proveedor": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "razon_social": "Distribuidora Nacional de Papelería S.A.S."
    }
  }
]
```

---

### POST /api/cuentas-por-pagar/{cxp_id}/abonos
Registra un pago/abono a una obligación financiera.

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

**Efectos colaterales:**
1. Amortiza el saldo pendiente en `$500,000.00`.
2. Si el abono reduce el `saldo_pendiente` a `0.00`, cambia automáticamente el estado de la `CuentaPorPagar` a `PAGADA`, y de la `Compra` origen a `PAGADA`.

**Errores:**
- `400 Bad Request`: Si el monto del abono excede el saldo pendiente.

---

### GET /api/cuentas-por-pagar/{cxp_id}/abonos
Lista el historial de abonos realizados a una cuenta por pagar específica.

**Response 200:**
```json
[
  {
    "id": "e309cb42-bb44-4822-b91b-c6b758b29c91",
    "monto": 500000.00,
    "fecha_abono": "2026-05-21T19:15:00Z",
    "metodo_pago": "TRANSFERENCIA",
    "nota": "Transferencia Bancolombia Ref: #48109"
  }
]
```

---

### DELETE /api/cuentas-por-pagar/abonos/{abono_id}
Reversa un abono registrado.

**Response 200:**
```json
{
  "ok": true,
  "message": "Abono reversado correctamente, saldo pendiente restaurado"
}
```

**Efectos colaterales:**
1. El monto del abono se suma nuevamente al `saldo_pendiente` de la `CuentaPorPagar`.
2. Si el estado de la obligación era `PAGADA`, se degrada nuevamente a `PENDIENTE` (o `VENCIDA` si ya pasó la fecha de vencimiento).
3. Se degrada el estado de la `Compra` origen asociada a `PENDIENTE`.
