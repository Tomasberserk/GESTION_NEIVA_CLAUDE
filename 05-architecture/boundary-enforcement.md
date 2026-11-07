# 05 — Boundary Enforcement

## What is being enforced

A module may import another module's `api/`, and **never its `internal/`**.
Names match [`02-domain/module-boundaries.md`](../02-domain/module-boundaries.md) and
folders follow [`module-structure.md`](./module-structure.md).

## Tool configuration (`.importlinter`)

In Python / FastAPI, boundary enforcement is automated by `import-linter`.
A forbidden contract is registered for each module:

```ini
[importlinter]
root_package = app

[importlinter:contract:inventario-internals-are-private]
name = Only inventario imports inventario's internals
type = forbidden
allow_indirect_imports = True
source_modules =
    app.auth_tenancy
    app.pos_ventas
    app.soporte_crm
    app.agente_ia
    app.reportes_analytics
forbidden_modules =
    app.inventario.internal
```

- `app.pos_ventas.internal.application` -> `app.inventario.api.facade` — **Allowed**:
  Reaching another module through its public facade is legal and expected.
- `app.pos_ventas.internal.application` -> `app.inventario.internal.persistence.models` — **Fails**:
  Direct coupling to private models triggers non-zero exit in `lint-imports`.

## Execution pipeline

| Stage | Command | On failure |
|---|---|---|
| Local verification | `lint-imports` | Developer is blocked from committing boundary violations |
| CI Pipeline (`boundary check`) | `lint-imports` | Build fails immediately; tests do not execute |

The `boundary check` stage runs straight after `build` and before `test`:
a boundary violation invalidates test results.

---

**Related:** [`./modular-monolith.md`](./modular-monolith.md) · [`../10-devops/ci-cd.md`](../10-devops/ci-cd.md)
