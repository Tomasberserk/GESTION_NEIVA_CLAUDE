# soporte-crm — Module Overview

## Purpose

The `soporte_crm` module provides an integrated helpdesk ticketing inbox for communication
between store owners and the platform SuperAdmin, handling inquiries, incident reports,
and plan upgrade requests.

## Public API

| Method | Input | Output | Called by |
|---|---|---|---|
| `SoporteCrmFacade.crear_ticket` | `empresa_id: UUID, usuario_id: UUID, asunto: str, mensaje: str` | `TicketDTO` | Presentation router |
| `SoporteCrmFacade.responder_ticket` | `ticket_id: UUID, remitente_rol: str, mensaje: str` | `MensajeDTO` | Presentation router |
| `SoporteCrmFacade.listar_tickets_tenant` | `empresa_id: UUID` | `list[TicketResumenDTO]` | Presentation router |

Everything not exposed in `SoporteCrmFacade` is private to `internal/application/`.

## Dependencies

| Depends on | Through | Why |
|---|---|---|
| `auth_tenancy` | `AuthTenancyFacade.obtener_usuario()` | Enriches ticket views with user email and store name |

## In-process events

| Event | Direction | Involved module |
|---|---|---|
| `TicketCreadoEvent` | Emits | Notifies SuperAdmin dashboard of pending support tickets |

---

**Related:** [`./data-model.md`](./data-model.md) · [`./runbook.md`](./runbook.md) · [`../module-catalog.md`](../module-catalog.md)
