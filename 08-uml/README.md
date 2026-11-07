# 08 — UML

## Purpose

This section indexes and maintains the architectural and behavioral diagrams of
Gestión Neiva. It visualizes the system at C4 Context, Container, and Component
levels, as well as critical runtime execution sequences.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [diagram-index.md](./diagram-index.md) | What diagrams exist, at what C4 level, and where are they rendered? | ⭐ |
| [diagrams/source/c4-context.mmd](./diagrams/source/c4-context.mmd) | Who and what external systems interact with Gestión Neiva? | ⭐ |
| [diagrams/source/c4-container.mmd](./diagrams/source/c4-container.mmd) | What deployable units compose the single application? | ⭐ |
| [diagrams/source/sequence-pos-checkout.mmd](./diagrams/source/sequence-pos-checkout.mmd) | How does atomic checkout execute with row-level locking? | ⭐ |
| [diagrams/source/sequence-voice-turn.mmd](./diagrams/source/sequence-voice-turn.mmd) | How does the multi-modal voice AI loop execute? | — |

## Out of scope

Outdated class diagrams, ephemeral whiteboard snapshots, and code-level call graphs
that duplicate what `import-linter` enforces statically.

## Ready when

- [x] Every diagram in `diagram-index.md` has its source file under `diagrams/source/`
- [x] All diagrams render valid Mermaid syntax without syntax errors
- [x] Critical flows (POS checkout, Voice turn) match the implementation in `pos_ventas` and `agente_ia`

---

**Related:** [`../05-architecture/modular-monolith.md`](../05-architecture/modular-monolith.md) · [`../09-modules/module-catalog.md`](../09-modules/module-catalog.md)
