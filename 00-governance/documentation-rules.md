# 00 — Documentation Rules

## Living documentation principle

A design document is not historical documentation written after the fact; it is the plan
the code follows. A document that describes old behavior is not merely outdated — it is a bug.

```
If code changes but the document does not  ->  the document is broken
If the document says X but the code does Y  ->  the document is a defect
```

Whoever opens the pull request that changes system behavior is responsible for updating the
corresponding document in that same pull request.

## Core rules

1. **One question per document:** If a document answers two architectural questions, split it.
2. **25–80 lines:** Below 25 lines it is a stub; above 80 lines it covers two topics.
3. **Tables and diagrams over prose:** Use Mermaid diagrams and structured Markdown tables.
4. **Falsifiable statements:** Avoid vague adjectives ("fast", "secure"); write verifiable thresholds.
5. **Relative links:** Never use hardcoded absolute local paths; ensure links resolve in GitHub.
6. **Ubiquitous vocabulary:** Use the canonical terms defined in [`../01-context/glossary.md`](../01-context/glossary.md).

## Review checklist

- [x] Document answers the question defined in its section `README.md`
- [x] No unresolved placeholder blocks remain
- [x] All relative markdown links resolve correctly
- [x] Mermaid diagrams render cleanly without syntax errors

---

**Related:** [`./definition-of-done.md`](./definition-of-done.md) · [`./README.md`](./README.md)
