# 01 — Glossary

## Terms

| Term | Definition | Forbidden synonyms |
|---|---|---|
| Tendero (Dueño) | Store owner managing products, prices, trials, and business reports | Merchant, admin (use only in technical code) |
| Cajero (Ayudante) | Store employee authorized only to scan items and execute sales | Cashier clerk, clerk |
| Empresa (Tenant) | Independent retail business account owning isolated catalog and sales data | Store, shop, organization |
| Producto | Salable catalog item with cost, sale price, unit, and stock count | Item, article, SKU |
| Código de Barras | Barcode identifier (EAN/UPC) unique per tenant | Barcode string, product code |
| Venta POS | Atomic checkout transaction totaling line items and discounting stock | Invoice, bill, order |
| Detalle de Venta | Individual line item recording quantity and frozen unit price in a sale | Line item, sale row |
| Snapshot de Venta | Historical copy of unit price and product name frozen at checkout time | Price record, history entry |
| Snapshot de Vendedor | Historical cashier name frozen in the sale header for audit traceability | User log, seller record |
| Vencimiento Crítico | Alert triggered when a product's expiration date is within 15 days | Expiration notice, dead stock |
| Ticket de Soporte | Communication thread between a shopkeeper and the platform SuperAdmin | Issue, complaint, chat |
| AgentCommand | Idempotent transaction record executed by the in-app AI assistant | AI action, bot task |
| Turno de Voz | Complete cycle of audio recording, Whisper STT, FSM processing, and TTS/UI response | Voice loop, audio roundtrip |
| Módulo | Bounded context inside the single deployable, owning its tables and public facade | Microservice, service, layer |

## Why forbidden synonyms matter

Two words for the same concept cause documents and code contracts to diverge. When a
reviewer encounters a forbidden synonym in a pull request or design document, the fix is
to rename the usage to match this glossary.

---

**Related:** [`./overview.md`](./overview.md) · [`../02-domain/module-boundaries.md`](../02-domain/module-boundaries.md)
