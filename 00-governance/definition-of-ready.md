# 00 — Definition of Ready

A user story (`HU-NN`) does not enter sprint planning until all criteria below are satisfied.

## Checklist

| # | Criterion | How it is verified |
|---|---|---|
| 1 | Story has unambiguous acceptance criteria | Written as Given/When/Then scenarios in [`../04-requirements/user-stories.md`](../04-requirements/user-stories.md) |
| 2 | Owning module is explicitly identified | Mapped to one of the 6 modules in [`../09-modules/module-catalog.md`](../09-modules/module-catalog.md) |
| 3 | Business rules (`BR-NN`) are referenced | Cross-referenced in [`../02-domain/entities-and-rules.md`](../02-domain/entities-and-rules.md) |
| 4 | UI wireframe attached if screen changes | Screen state documented under [`../12-ux-ui/screens/`](../12-ux-ui/README.md) |
| 5 | OpenAPI contract is drafted | Endpoint defined in [`../07-api/contracts/openapi/openapi-spec.yaml`](../07-api/contracts/openapi/openapi-spec.yaml) |
| 6 | Scope does not invade other bounded contexts | Verified against [`../02-domain/module-boundaries.md`](../02-domain/module-boundaries.md) |
| 7 | Fits within one sprint cycle | Estimated at <= 8 story points by engineering team |

## What "Ready" is not

Ready does not mean the feature is already implemented or fully coded. It means the team
understands the business requirement and edge cases well enough to begin coding without
stopping to ask what is expected.

## Operational verification

- Verified automatically in the GitHub Actions CI pipeline (`.github/workflows/ci.yml`).
- Reviewed by the engineering team under the Monolith Governance Framework v2.1.0.

---

**Related:** [`./definition-of-done.md`](./definition-of-done.md) · [`../04-requirements/user-stories.md`](../04-requirements/user-stories.md)
