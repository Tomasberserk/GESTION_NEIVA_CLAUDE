# 00 — Definition of Done

A user story is considered Done only when every criterion below is verified in CI and review.

## Checklist

| # | Criterion | How it is verified |
|---|---|---|
| 1 | Acceptance criteria implemented | Automated tests pass and manual review confirms running app behavior |
| 2 | Boundary check is clean | `lint-imports` passes with zero contract violations in CI |
| 3 | Automated test suite passes | `pytest -m "unit or module_integration"` completes with zero failures |
| 4 | Code coverage meets threshold | Tested via `pytest --cov=app --cov-fail-under=80` (90% on `pos_ventas`) |
| 5 | Migrations run bidirectionally | `alembic upgrade head` and `downgrade -1` verified in test pipeline |
| 6 | Observability standard respected | Logs emit structured JSON with `correlationId` and timestamp per **NFR-09** |
| 7 | Documentation synchronized | Architecture/SDD documents updated in the exact same pull request |
| 8 | Code review approved | Peer code review approved and GitHub Actions status checks green |

## Coverage thresholds

- **Global changed files:** Minimum 80% line coverage required to merge.
- **`pos_ventas` module:** Minimum 90% line coverage (**NFR-07**) due to financial criticality.
- Pull requests falling below these thresholds are blocked automatically by the CI pipeline.

---

**Related:** [`./definition-of-ready.md`](./definition-of-ready.md) · [`./documentation-rules.md`](./documentation-rules.md)
