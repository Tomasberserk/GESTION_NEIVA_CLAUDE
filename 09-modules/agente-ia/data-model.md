# agente-ia — Data Model

## Tables owned

| Table | Entity | Key attributes |
|---|---|---|
| `agent_commands` | AgentCommand | id (UUID), empresa_id, conversation_id, command_id, action, payload, status, result, executed_at, is_active |

## Invariants

| Invariant | Enforced where |
|---|---|
| `BR-09`: AI commands require Pro/Premium plan | Route dependency `require_pro_entitlement` |
| `BR-12`: Command execution is strictly idempotent per `(empresa_id, command_id)` | Database unique constraint `uq_empresa_command_id` |

## Cross-module references

| Column | Points to | Validated by |
|---|---|---|
| `empresa_id` | `auth_tenancy.empresas` | Request token dependency / `AuthTenancyFacade` |

Stored as a plain UUID column without a database foreign key constraint per **ADR-004**.

## Operational verification

- Verified automatically in the GitHub Actions CI pipeline (`.github/workflows/ci.yml`).
- Reviewed by the engineering team under the Monolith Governance Framework v2.1.0.

---

**Related:** [`./README.md`](./README.md) · [`../../06-data/models.md`](../../06-data/models.md)
