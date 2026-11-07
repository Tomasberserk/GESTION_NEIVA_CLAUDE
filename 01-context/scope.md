# 01 — Scope

## In scope

| Capability | Note |
|---|---|
| Tenant & user management | Multi-tenant isolation by UUID, JWT auth, RBAC (Admin vs Cajero), and WhatsApp linking |
| Product & stock management | Per-tenant barcodes, fractional units (gramo, libra, kilo), and 15-day expiration alerts |
| Point of Sale (POS) checkout | Fast cart, camera barcode scanning, atomic stock deduction, and frozen price snapshot |
| Support CRM inbox | Multi-thread customer support between tenderos and SuperAdmin |
| In-app AI agent | Voice STT (Whisper), conversational LLM commands, FSM orchestration, and idempotency |
| Sales & financial reports | Daily cash register close, profit estimation, and Excel spreadsheet export (`openpyxl`) |
| SuperAdmin console | Tenant subscription controls, trial duration extensions, and platform metrics |

## Out of scope

| Capability | Why it is excluded |
|---|---|
| Accounts payable (CxP) & purchases | Legacy ERP module deprecated and pruned in migration `011`; the system focuses strictly on POS |
| Electronic invoicing (DIAN) | Deferred to future regulatory phase; requires specialized certificate infrastructure |
| Native mobile store apps | Handled via responsive mobile browser / PWA without App Store or Play Store distribution |
| Integrated banking dataphones | Cash, transfers (Nequi/Daviplata), and generic card records are recorded manually |
| Consumer e-commerce storefront | The catalog is private to each store; no public marketplace or end-consumer shopping cart |
| Payroll & employee contracts | Cashier management covers software access permissions only, not labor compensation |
| Microservices decomposition | The entire platform deploys and scales as a single unified modular monolith |

## Revisiting scope

An item moves from "Out" to "In" only after `../03-product/vision.md` is updated
first — scope follows vision, not the other way around.

---

**Related:** [`./overview.md`](./overview.md) · [`../03-product/problem-framing.md`](../03-product/problem-framing.md)
