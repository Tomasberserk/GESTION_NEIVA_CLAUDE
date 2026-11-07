# 00 — Git Conventions

## Branch strategy

```
main                    Production. Deploys to live environment upon release tag.
  |-- dev               Integration branch. Merges from tested feature branches.
        |-- feat/<module>-<hu>    Feature branch for a specific user story
        |-- fix/<module>-<issue>  Bug fix branch
        |-- chore/<description>   Infrastructure, linter, dependencies, or docs
        |-- hotfix/<description>  Urgent patch branched directly from main
```

- Direct commits to `main` and `dev` are strictly blocked by branch protection.
- One branch represents exactly one task or story and is deleted immediately after merge.

## Branch naming

`[type]/[module]-[short-description]` — example: `feat/inventario-barcode-scanner`

## Commit format (Conventional Commits)

Format: `type(scope): imperative, lowercase, no trailing period`

| Type | When to use | Example |
|---|---|---|
| `feat` | New functionality | `feat(pos_ventas): add pessimistic row locking on checkout` |
| `fix` | Bug fix | `fix(inventario): prevent negative stock on fractional bulk items` |
| `docs` | Documentation updates | `docs(06-data): update data model and remove legacy tables` |
| `refactor` | Restructuring without changing behavior | `refactor(auth_tenancy): extract facade from auth service` |
| `test` | Add or update automated tests | `test(pos_ventas): add concurrency test with 10 threads` |
| `chore` | CI/CD, dependencies, linter | `chore(importlinter): add contracts for 6 modular domains` |

## Pull request & merge policy

- **Squash and merge** for feature branches merging into `dev` (preserves clean history).
- **Green CI required:** GitHub Actions `build`, `boundary-check`, and `test` must pass.
- **Docs updated:** Pull request must include doc changes if behavior changed.

---

**Related:** [`./agile-conventions.md`](./agile-conventions.md) · [`./definition-of-done.md`](./definition-of-done.md)
