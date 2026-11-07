# auth-tenancy — Data Model

## Tables owned

| Table | Entity | Key attributes |
|---|---|---|
| `empresas` | Empresa | id (UUID), nombre_comercial, nit_o_cedula, plan, trial_expires_at, is_active |
| `usuarios` | Usuario | id (UUID), email, hashed_password, empresa_id (FK), rol, nombre, telefono_whatsapp, is_active |

## Invariants

| Invariant | Enforced where |
|---|---|
| `nit_o_cedula` is globally unique across the platform | Database constraint & application validation |
| `email` is globally unique across all tenants | Database constraint & `auth_service` |
| `BR-03`: All queries must filter by `empresa_id` | Database queries & FastAPI dependencies |
| `BR-07`: Maximum active cashiers governed by subscription plan | `AuthTenancyFacade.verificar_limite_cajeros()` |
| `BR-08`: Trial expiration blocks write operations | `AuthTenancyFacade.validar_tenant_activo()` |

## Cross-module references

| Column | Points to | Validated by |
|---|---|---|
| *(none)* | — | This module is the root identity provider |

---

**Related:** [`./README.md`](./README.md) · [`../../06-data/models.md`](../../06-data/models.md)
