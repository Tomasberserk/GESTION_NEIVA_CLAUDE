# soporte-crm — Data Model

## Tables owned

| Table | Entity | Key attributes |
|---|---|---|
| `soporte_tickets` | SoporteTicket | id (UUID), empresa_id, usuario_id (UUID), asunto, estado, is_active |
| `soporte_mensajes` | SoporteMensaje | id (UUID), ticket_id (FK), remitente_rol, remitente_email, mensaje, created_at |

## Invariants

| Invariant | Enforced where |
|---|---|
| State transitions: `abierto` -> `respondido` -> `cerrado` | `internal/application/tickets.py` |
| `remitente_rol` is either `superadmin` or `usuario` | Enum validation in schema |

## Cross-module references

| Column | Points to | Validated by |
|---|---|---|
| `soporte_tickets.usuario_id` | `auth_tenancy.usuarios` | `AuthTenancyFacade.obtener_usuario()` |

Stored as a plain UUID column without a database foreign key constraint per **ADR-004**.

---

**Related:** [`./README.md`](./README.md) · [`../../06-data/models.md`](../../06-data/models.md)
