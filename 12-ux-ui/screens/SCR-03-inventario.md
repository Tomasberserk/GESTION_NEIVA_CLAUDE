# SCR-03 — Catálogo de Inventario y Alertas

## Identification

| Field | Value |
|---|---|
| Screen | Catálogo de Inventario (`/inventario`) |
| Serves | `HU-02`, `HU-03` |
| Route | `frontend/src/pages/Inventario.jsx` |

## States

| State | What the user sees |
|---|---|
| Empty | "No tienes productos registrados aún." Action: "+ Registrar Producto" button |
| Loading | Table skeleton loading 5 placeholder rows |
| Populated | Search input, category filter chips, product table with stock and expiration badges |
| Warning / Critical | Rows with stock <= 3 highlight amber; products expiring in <= 15 days highlight red |
| Modal | Slide-over drawer with product form (barcode, name, cost, sale price, unit, date) |

## Wireframe outline

```
+------------------------------------------------------------------+
| INVENTARIO DE TIENDA              [ + Nuevo Producto ]           |
| [ Buscar por nombre o código... ] [ Todas las categorías v ]     |
|------------------------------------------------------------------|
| Código      Producto       Costo    Precio   Stock  Vence  Estado|
| 77020101    Leche 1L      $3,200   $4,500    12 un  5 días [CRIT]|
| 77010203    Arroz 1kg     $3,100   $4,200     2 un  8 meses[BAJO]|
| 77030405    Aceite 500ml  $5,000   $7,000    25 un  1 año  [OK]  |
+------------------------------------------------------------------+
```

## Validation rules

| Field | Rule | Message shown |
|---|---|---|
| `codigo_barras` | Required; unique per store | "El código de barras ya existe en tu tienda" |
| `precio_costo` | Decimal >= 0 | "El costo debe ser mayor o igual a cero" |
| `precio_venta` | Decimal >= precio_costo | "El precio de venta debería ser mayor al costo" |

---

**Related:** [`../design-system.md`](../design-system.md) · [`../../04-requirements/user-stories.md`](../../04-requirements/user-stories.md)
