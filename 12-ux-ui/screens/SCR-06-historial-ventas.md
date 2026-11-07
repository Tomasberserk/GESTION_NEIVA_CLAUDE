# SCR-06 — Historial de Ventas y Actividad del Día

## Identification

| Field | Value |
|---|---|
| Screen | Historial de Ventas y Reportes (`/ventas`) |
| Serves | `HU-06`, `HU-11`, `HU-12` |
| Route | `frontend/src/pages/Ventas.jsx` |

## States

| State | What the user sees |
|---|---|
| Loading | Skeleton rows while fetching chronological sales for the selected tab |
| Empty Period | Illustration and message indicating no sales recorded in the selected date range |
| Populated (LIFO) | Chronological list of sales (most recent first) showing timestamp, seller snapshot (`vendedor_nombre_snapshot`), line items, and total |
| Filtered by Seller | Admin filter dropdown narrowing daily sales to a specific cashier (`usuario_id`) |

## Tabs and actions

1. **Actividad del Día (Hoy):** Displays today's sales in Colombia commercial timezone (`America/Bogota`) ordered LIFO.
2. **Esta Semana:** Aggregates transactions starting Monday 00:00 COT.
3. **Histórico y Reportes:** 30-day transaction history with one-click Excel export (`/api/v1/reportes/{empresa_id}/excel`).

## Validation rules

| Field | Rule | Message shown |
|---|---|---|
| `fecha` | ISO format `YYYY-MM-DD` | "Formato de fecha inválido. Use YYYY-MM-DD" |
| `role` | Export Excel restricted to `ADMIN` role | Hidden for cashiers (`TENDERO`) |

---

**Related:** [`./SCR-02-pos-caja.md`](./SCR-02-pos-caja.md) · [`../design-system.md`](../design-system.md)
