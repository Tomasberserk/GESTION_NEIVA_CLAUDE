# 01 — Overview

## What it does

Gestión Neiva (TiendApp) is a single-deployable multi-tenant POS SaaS tailored for
neighborhood micro-retailers (*tiendas de barrio*) in Neiva, Colombia. It allows shopkeepers
to manage catalog stock, scan barcodes with a mobile camera, execute fast sales with atomic
stock deduction, resolve customer support, and invoke an AI assistant via voice or text.

| Capability | Description |
|---|---|
| Multi-Tenancy & Auth | Tenant isolation by `empresa_id`, JWT auth, RBAC roles (Admin/Tendero vs Cajero) |
| Inventory & Stock | Barcodes per tenant, stock counts, wholesale units, and 15-day expiration alerts |
| POS Fast Checkout | High-speed sales cart, barcode lookup, and pessimistic concurrency locking |
| Support CRM | In-app helpdesk inbox connecting shopkeepers with platform administrators |
| AI Voice Agent | Natural language task execution and voice transcription via Groq Whisper / Gemini |
| Reporting & Analytics | Daily financial cash register close and Excel spreadsheet export |

## Who it is for

| Audience | Uses it to |
|---|---|
| Tendero (Shop Owner) | Control catalog prices, monitor profit, re-stock via voice, and manage staff |
| Cajero (Cashier) | Scan items, ring up customer orders, and issue sale tickets quickly |
| Platform SuperAdmin | Provision tenant accounts, manage subscription plans, and resolve support tickets |

## Problem it solves

Before this system, store owners in Neiva relied on memory, paper notebooks, and manual
calculators. Product prices drifted between staff shifts, perishable goods expired on shelves
undetected, and cashiers caused overselling during peak hours because stock was not tracked
in real time.

## Constraints

| Constraint | Why |
|---|---|
| One deployable application | Managed by a small team; avoids operational complexity of microservices |
| One relational database | Multi-tenant PostgreSQL instance; guarantees ACID sales consistency in one transaction |
| Mobile-first responsive web | Tenderos use existing Android/iOS mobile browsers; hardware scanner purchases are optional |
| Low-bandwidth tolerance | Optimized for cellular data networks typical of small local businesses |

---

**Related:** [`./scope.md`](./scope.md) · [`./glossary.md`](./glossary.md)
