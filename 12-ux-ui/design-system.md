# 12 — Design System

## Design tokens (Tailwind CSS v4)

Gestión Neiva adopts a high-contrast, retail-optimized theme built with Tailwind CSS v4
and React 19, designed for readability under harsh store lighting.

### Color palette

| Token | Class / Hex | Use |
|---|---|---|
| `--color-primary` | `emerald-600` (`#059669`) | Primary POS action: cobrar, registrar, confirmar |
| `--color-danger` | `rose-600` (`#E11D48`) | Destructive actions, out of stock, critical expiration |
| `--color-warning` | `amber-500` (`#F59E0B`) | Low stock warning, 15-day expiration notice |
| `--color-surface` | `zinc-900` / `white` | Clean background for card surfaces and tables |
| `--color-text` | `zinc-950` / `zinc-100` | High-contrast body text adhering to WCAG 2.1 AA |

### Typography and touch metrics

| Element | Value | Purpose |
|---|---|---|
| Font family | Inter, -apple-system, sans-serif | High legibility on low-resolution mobile screens |
| Base body size | `1rem` (16px) | Standard table rows, inputs, and button labels |
| Currency display | `font-mono font-bold text-xl` | POS price totals and keypad numbers |
| Minimum touch target | `48px x 48px` | Critical for store clerks using touchscreens with one hand |

## Component primitives

- **Radix UI Primitives:** Dialog (modals), DropdownMenu, Toast (checkout feedback), Tooltip.
- **Data Table:** Responsive table collapsing into stacked cards on viewports `< 768px`.
- **Cart Sidebar:** Persistent slide-over drawer on desktop; bottom-sheet modal on mobile.
- **Scanner Viewport:** Camera overlay with barcode reticle and flashlight toggle.

## Accessibility target (WCAG 2.1 AA)

1. **Contrast:** Text contrast >= 4.5:1 against surfaces; numeric totals >= 7:1.
2. **One-Handed Usability:** Primary action buttons pinned within the bottom thumb zone on mobile.
3. **Form Labels:** Every input has a visible label and `aria-label` attribute.

---

**Related:** [`./README.md`](./README.md) · [`./screens/SCR-02-pos-caja.md`](./screens/SCR-02-pos-caja.md)
