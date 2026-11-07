# 10 — DevOps

## Purpose

This section defines the operational procedures for building, running, and deploying
Gestión Neiva. It covers the local development environment, environment configurations,
and the single CI/CD deployment pipeline.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [local-setup.md](./local-setup.md) | How does a developer run the application locally in under 1 hour? | ⭐ |
| [environments.md](./environments.md) | What environments exist, and how are secrets and variables configured? | ⭐ |
| [ci-cd.md](./ci-cd.md) | What automated pipeline gates govern pull requests and releases? | ⭐ |

## Out of scope

Per-module pipelines, Kubernetes clusters, and multi-region traffic mesh routing.
The application deploys as a single containerized FastAPI monolith with a companion
Vite/React SPA.

## Ready when

- [x] Local setup steps are verified to run within the 1-hour budget of **NFR-08**
- [x] Environment matrix defines variables for Local, Staging (Render), and Production
- [x] CI/CD pipeline specifies the `boundary-check` stage using `import-linter`

---

**Related:** [`../00-governance/security-policy.md`](../00-governance/security-policy.md) · [`../11-quality/testing-strategy.md`](../11-quality/testing-strategy.md)
