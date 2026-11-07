# 00 — Agile Conventions

This project runs on two-week sprints managed on a single Kanban board for the unified
modular monolith application.

## Ceremonies

| Ceremony | Cadence | Artifact produced |
|---|---|---|
| Sprint planning | Every 2 weeks, 2 hours | Sprint goal and committed list of user stories from `04-requirements/` |
| Daily standup | Daily, 15 minutes | Blockers identified and tracked; progress aligned |
| Backlog refinement | Weekly, 1 hour | Stories refined to meet [`definition-of-ready.md`](./definition-of-ready.md) |
| Sprint review / demo | Every 2 weeks, 1 hour | Live demo of completed features against staging environment |
| Sprint retrospective | Every 2 weeks, 1 hour | Concrete process improvements logged and assigned |

## Estimation scale

- **Unit:** Story points using the Fibonacci sequence: `1, 2, 3, 5, 8`.
- **Upper limit:** Any story estimated at `> 8 points` must be split before entering a sprint.
- **Participants:** The engineering team estimates collectively during refinement.

## Board workflow

```
Backlog  ──►  Ready (DoR)  ──►  In Progress  ──►  In Review (PR)  ──►  Done (DoD)
```

No story skips columns. A story moves to `Done` only when all criteria in
[`definition-of-done.md`](./definition-of-done.md) are verified.

---

**Related:** [`./definition-of-ready.md`](./definition-of-ready.md) · [`./definition-of-done.md`](./definition-of-done.md)
