# SCR-02 — Terminal POS y Cobro Rápido

## Identification

| Field | Value |
|---|---|
| Screen | Terminal de Ventas POS (`/ventas`) |
| Serves | `HU-04`, `HU-05`, `HU-06` |
| Route | `frontend/src/pages/Ventas.jsx` |

## States

| State | What the user sees |
|---|---|
| Empty Cart | Left panel shows product grid / camera scanner; right sidebar shows empty cart illustration |
| Populated Cart | Items listed with quantities, unit price snapshot, subtotals, and total in green |
| Scanning | Mobile camera active with scanning reticle overlay detecting EAN-13 barcodes |
| Processing | Cobrar button disabled: "Procesando venta y bloqueando stock..." |
| Success | Modal with sale ticket summary, change calculation, and "Nueva Venta" button |

## Wireframe outline

```
+------------------------------------+-----------------------------+
| [ Cámara / Lector de Barras ]      | CARRITO DE VENTA            |
| [ Buscar producto por nombre...  ] | • 2x Leche Alquería $ 9,000 |
|                                    | • 1x Pan Tajado     $ 4,500 |
| +--------------------------------+ | --------------------------- |
| | Arroz Roa 1kg   | Gaseosa 350ml| | TOTAL:             $13,500  |
| | Stock: 15       | Stock: 8     | |                             |
| | $ 4,200 [AGREGAR]| $ 2,500 [+] | | [   COBRAR ($13,500)   ]    |
| +--------------------------------+ +-----------------------------+
+------------------------------------+-----------------------------+
```

## Validation rules

| Field | Rule | Message shown |
|---|---|---|
| `cart.items` | Cart must contain at least 1 item | "Agrega al menos un producto para cobrar" |
| `stock` | Item quantity cannot exceed `cantidad_actual` | "Stock insuficiente para [Producto]" |

---

**Related:** [`../design-system.md`](../design-system.md) · [`../../04-requirements/user-stories.md`](../../04-requirements/user-stories.md)
