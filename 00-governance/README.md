# 00 — Governance

## Purpose

This section defines the rules the team commits to across the entire lifecycle of
Gestión Neiva: how work enters a sprint, how pull requests are merged, branch conventions,
definition of done, living documentation standards, and security controls.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [definition-of-ready.md](./definition-of-ready.md) | When can a story enter a sprint? | ⭐ |
| [definition-of-done.md](./definition-of-done.md) | When is a user story considered finished? | ⭐ |
| [git-conventions.md](./git-conventions.md) | How are branches and commit messages formatted? | ⭐ |
| [documentation-rules.md](./documentation-rules.md) | What rules ensure living documentation stays current? | ⭐ |
| [agile-conventions.md](./agile-conventions.md) | What agile ceremonies run and what artifacts do they produce? | — |
| [security-policy.md](./security-policy.md) | How are JWT secrets, tenant isolation, and credentials secured? | — |

## Out of scope

Distributed microservice governance, multi-team release trains, and external enterprise
bureaucracy. This policy applies to one small, high-velocity engineering team releasing a
single modular monolith.

## Ready when

- [x] Every document in this section defines verifiable, non-ambiguous rules
- [x] `definition-of-ready.md` and `definition-of-done.md` are referenced in all modules
- [x] Security policies explicitly mandate zero secrets in git and strict JWT validation

---

**Related:** [`../00-sdd-guide.md`](../00-sdd-guide.md) · [`./documentation-rules.md`](./documentation-rules.md)
