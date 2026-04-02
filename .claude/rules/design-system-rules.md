# Design System Rules — "Azure Velocity"

## Mandatory for ALL Frontend & Mobile UI Work

When writing any React component, Flutter widget, or CSS/Tailwind styling, you MUST follow the Azure Velocity design system. This is a hard requirement.

## Critical Rules (Never Break These)

1. **AZURE BLUE PRIMARY** — Primary interactive color is #0058be. Use `bg-primary`, `text-primary`. Never use teal or navy as primary.

2. **INTER ONLY** — Use Inter font everywhere. `font-sans` for all text. No Manrope, no `font-display` (it maps to Inter too).

3. **MATERIAL SYMBOLS** — Use Material Symbols Outlined for all icons. Render as `<span className="material-symbols-outlined">icon_name</span>`.

4. **SUBTLE BORDERS** — Cards and containers use `border border-outline-variant/10` with `shadow-sm`. Heavier borders use `/15`.

5. **90/10 COLOR RULE** — 90% neutral surfaces (slate-50, surface tokens). 10% Azure Blue for interactive/actionable elements.

6. **UPPERCASE LABELS** — Section headers and labels use `text-[10px] font-bold uppercase tracking-widest text-on-surface-variant`.

## Color Tokens
```
primary: #0058be (Azure Blue)
primary-container: #2170e4
secondary: #495e8a (Slate Blue)
tertiary: #924700 (Amber)
surface: #f7f9fb
surface-container-lowest: #ffffff (cards)
surface-container-low: #f2f4f6 (sidebar/nav)
surface-container: #eceef0
surface-container-high: #e6e8ea (input bg)
on-surface: #191c1e
on-surface-variant: #424754
outline-variant: #c2c6d6
error: #ba1a1a
```

## Surface Nesting Pattern
```
surface (#f7f9fb)                      <- page background
  └─ slate-50                          <- sidebar / header
  └─ surface-container-lowest (#fff)   <- card / workspace
      └─ surface-container-low (#f2f4f6) <- nested module
```

## Component Patterns

### Cards
`bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 p-6`

### Tables
- Wrapper: `bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/10 overflow-hidden`
- Headers: `bg-surface-container-low/50`, `text-[10px] font-black uppercase tracking-widest`
- Row hover: `hover:bg-surface-bright`
- Row dividers: `divide-y divide-outline-variant/10`

### Inputs
- `bg-surface-container-high/50 border-none rounded-lg focus:ring-2 focus:ring-primary/20`
- Labels: `text-[10px] font-bold uppercase tracking-widest text-outline`

### Buttons
- Primary: `bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-lg shadow-lg shadow-primary/20`
- Secondary: `bg-surface-container-lowest text-primary border border-outline-variant/15 rounded-lg shadow-sm`

### Badges
- Success: `bg-green-50 text-green-700`
- Warning: `bg-amber-50 text-amber-700`
- Danger: `bg-error-container/30 text-error`
- Info: `bg-primary/10 text-primary`

### Maps
- Glassmorphism overlays: `bg-white/90 backdrop-blur-md rounded-xl shadow-lg border border-white/20`
- Primary markers: #0058be
- Route lines: primary blue palette

### Sidebar
- `bg-slate-50` fixed w-64
- Logo: gradient icon from-primary to-primary-container
- Active nav: `bg-blue-50 text-blue-700`
- Inactive nav: `text-slate-600 hover:bg-slate-200`

### Header
- `sticky top-0 bg-slate-50/80 backdrop-blur-md shadow-sm`
- Search: `rounded-full bg-surface-container-high`

## Quick Reference
Read `Docs/DESIGN_SYSTEM.md` for the full specification.
