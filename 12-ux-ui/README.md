# 12 — UX / UI

## Purpose

**Applies to this system:** Yes — The application serves a React 19 Single Page Application (SPA) for store POS operations.

This section defines the design system and key screen specifications for the Gestión
Neiva user interface. It ensures accessibility compliance (WCAG 2.1 AA), responsive
touch sizing for mobile retail environments, and visual consistency across the React 19 SPA.

## Documents

| Document | Answers | Priority |
|---|---|---|
| [design-system.md](./design-system.md) | What visual tokens, component libraries, and accessibility rules apply? | ⭐ |
| [screens/SCR-01-login.md](./screens/SCR-01-login.md) | Login and multi-tenant authentication screen | — |
| [screens/SCR-02-pos-caja.md](./screens/SCR-02-pos-caja.md) | High-speed POS sales terminal and barcode scanner | ⭐ |
| [screens/SCR-03-inventario.md](./screens/SCR-03-inventario.md) | Product catalog, stock tracking, and 15-day alerts | ⭐ |
| [screens/SCR-04-dashboard.md](./screens/SCR-04-dashboard.md) | Financial performance overview and daily cash close | ⭐ |
| [screens/SCR-05-soporte.md](./screens/SCR-05-soporte.md) | Support CRM helpdesk inbox and messaging | — |
| [screens/SCR-06-historial-ventas.md](./screens/SCR-06-historial-ventas.md) | Sales history, daily activity timeline, and Excel export | ⭐ |

## Out of scope

Full Figma design tokens export or marketing website styling. This section governs
the core in-store POS web application.

## Ready when

- [x] Tokens for colors, fonts, and spacing reflect Tailwind CSS v4 in `design-system.md`
- [x] Touch targets are verified at >= 48x48dp for mobile screens
- [x] All 5 key screens are documented with explicit states and validation rules

---

**Related:** [`../04-requirements/user-stories.md`](../04-requirements/user-stories.md) · [`../05-architecture/modular-monolith.md`](../05-architecture/modular-monolith.md)
