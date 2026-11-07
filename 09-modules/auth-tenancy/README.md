# auth-tenancy — Module Overview

## Purpose

The `auth_tenancy` module manages store subscriptions, tenant isolation, user credentials,
roles (Admin vs Cajero), entitlements (plans and trial expiration), and WhatsApp linking.
It is the authoritative source of merchant identity.

## Public API

| Method | Input | Output | Called by |
|---|---|---|---|
| `AuthTenancyFacade.validar_tenant_activo` | `empresa_id: UUID` | `TenantDTO` | Any module |
| `AuthTenancyFacade.obtener_usuario` | `usuario_id: UUID` | `UsuarioDTO` | `pos_ventas`, `soporte_crm` |
| `AuthTenancyFacade.verificar_limite_cajeros` | `empresa_id: UUID` | `bool` | Presentation layer |
| `AuthTenancyFacade.verificar_acceso_pro` | `empresa_id: UUID` | `bool` | `agente_ia` |

## Dependencies

| Depends on | Through | Why |
|---|---|---|
| *(none)* | — | `auth_tenancy` sits at the root of identity and depends on no other domain module |

---

**Related:** [`./data-model.md`](./data-model.md) · [`./runbook.md`](./runbook.md) · [`../module-catalog.md`](../module-catalog.md)
