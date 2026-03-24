# Design System Rules — "The Architectural Conductor"

## Mandatory for ALL Frontend & Mobile UI Work

When writing any React component, Flutter widget, or CSS/Tailwind styling, you MUST follow `Docs/DESIGN_SYSTEM.md`. This is a hard requirement.

## Critical Rules (Never Break These)

1. **NO BORDERS** — Never use `border`, `border-solid`, `divide-y`, or 1px lines to separate sections. Use tonal surface shifts instead (`surface` → `surface-container-low` → `surface-container`).

2. **NO PURE BLACK** — Never use `#000000` or `text-black`. Always use `on-surface` (#111d23).

3. **NO BOX SHADOWS BY DEFAULT** — Elevation comes from surface nesting, not shadows. Use ambient shadows (32-64px blur, 6% opacity) only for floating elements (modals, dropdowns, map controls).

4. **DUAL FONT STRATEGY** — Manrope (`font-display`) for headlines/stats/narrative. Inter (`font-sans`) for interface text/data/labels. Never mix.

5. **90/10 COLOR RULE** — 90% neutral surfaces + slate grays. 10% Teal (`secondary`) for interactive/actionable elements only.

6. **LOW-CHROME CHIPS** — Status indicators use muted backgrounds (`secondary-container`, `surface-container-high`, `error-container`), never saturated badges.

## Surface Nesting Pattern
```
surface (#f4faff)                    ← page background
  └─ surface-container-low (#e9f6fd) ← sidebar / nav rail
  └─ surface-container-lowest (#fff) ← card / workspace
      └─ surface-container (#e3f0f8) ← nested module
```

## Component Patterns

### Tables → No grid lines, hover with surface-container-low, right-align numbers
### Inputs → No border at rest (surface-container-high bg), teal ghost border on focus (40% opacity)
### Buttons → rounded-md (0.375rem), primary uses momentum gradient (135deg)
### Spacing → spacing.16+ between major sections, spacing.24 for high-intensity data separation
### Maps → Silver/Navy base, teal overlays for paths, glassmorphism for floating controls

## Quick Reference
Read `Docs/DESIGN_SYSTEM.md` for:
- Full color token table
- Typography scale
- Spacing system
- TailwindCSS theme config
- Component specifications
