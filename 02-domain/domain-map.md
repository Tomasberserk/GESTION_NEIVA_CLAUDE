# 02 — Domain Map

## Bounded contexts

```mermaid
graph TD
    AuthTenancy["auth_tenancy<br/>empresas, usuarios"]
    Inventario["inventario<br/>productos"]
    PosVentas["pos_ventas<br/>ventas, detalles_venta"]
    SoporteCrm["soporte_crm<br/>soporte_tickets, soporte_mensajes"]
    AgenteIa["agente_ia<br/>agent_commands"]
    ReportesAnalytics["reportes_analytics<br/>(read-only projections)"]

    PosVentas -->|validates stock and fetches price snapshot from| Inventario
    PosVentas -->|validates cashier and active tenant with| AuthTenancy
    AgenteIa -->|executes voice restocking and queries with| Inventario
    AgenteIa -->|queries sales history via| PosVentas
    SoporteCrm -->|fetches tenant and user profile from| AuthTenancy
    ReportesAnalytics -.->|reads closed sales from| PosVentas
    ReportesAnalytics -.->|reads stock valuation from| Inventario
```

## Relationship legend

| Arrow | Meaning |
|---|---|
| `validates stock and fetches price snapshot` | In-process call to `InventarioFacade`. Checks availability and locks row with `FOR UPDATE`. Returns unit price snapshot |
| `validates cashier and active tenant` | In-process call to `AuthTenancyFacade`. Verifies user role and non-expired subscription |
| `executes voice restocking and queries` | In-process call to `InventarioFacade`. Mutates stock or performs catalog search from AI command |
| `queries sales history` | In-process call to `VentasFacade`. Reads sales volume or aggregates for AI queries |
| `fetches tenant and user profile` | In-process call to `AuthTenancyFacade`. Loads merchant identity for support ticket threads |
| `reads data (read projections)` | Analytical read queries for dashboard computation and Excel exports |

Every arrow is an in-process method call behind a facade. No database `FOREIGN KEY`
crosses between bounded contexts; references are stored as plain UUIDs.

---

**Related:** [`./entities-and-rules.md`](./entities-and-rules.md) · [`./module-boundaries.md`](./module-boundaries.md)
