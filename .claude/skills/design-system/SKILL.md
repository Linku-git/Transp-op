---
name: design-system
description: "Review, apply, or audit the Transpop design system. Use when building UI components, reviewing frontend code for design compliance, or generating TailwindCSS configuration. Outputs design tokens, component patterns, and compliance checks."
arguments:
  - name: action
    description: "Action: tokens (show color/type/spacing tokens), audit (check a file or component for violations), tailwind (generate tailwind config), component (show spec for a component type), full (show entire design system)"
    required: false
  - name: target
    description: "File path or component name to audit (for audit action)"
    required: false
---

# Design System — The Orchestration Framework

First, read `Docs/DESIGN_SYSTEM.md` for the full specification.

## Based on action argument:

### If action = "tokens" (or default)
Print a summary of:
1. **Color tokens** — All surface, primary, secondary, error colors with hex values
2. **Typography scale** — Manrope (display/headlines) and Inter (interface/data) with sizes
3. **Spacing tokens** — spacing.1 through spacing.24 with rem and px values
4. **Shadow tokens** — Ambient shadow definitions

### If action = "audit"
Read the target file and check for these violations:
1. **Border violations** — Any use of `border`, `border-solid`, `divide-y`, `border-t`, `border-b` for section separation
2. **Pure black** — Any use of `#000000`, `text-black`, `bg-black`
3. **Box shadow abuse** — `shadow-sm`, `shadow-md`, `shadow-lg` (Tailwind defaults) instead of custom ambient shadows
4. **Font violations** — Missing Manrope for headlines or Inter for body text
5. **Color overuse** — Too many colored elements (>10% rule)
6. **Status badges** — Saturated/heavy badges instead of low-chrome chips
7. **Input borders** — Visible borders on input rest state

Report each violation with file, line number, the violation, and the correct design system pattern.

### If action = "tailwind"
Output the complete TailwindCSS theme extension from `Docs/DESIGN_SYSTEM.md` Section 8, ready to paste into `tailwind.config.ts`.

### If action = "component"
Look up the target component type (table, button, chip, input, card, map, chart) in the design system and output:
- The exact specification
- A code example using TailwindCSS classes
- Common mistakes to avoid

### If action = "full"
Output the entire design system specification from `Docs/DESIGN_SYSTEM.md`.

## Critical Rules to Always Enforce
- NO 1px borders for layout separation
- NO pure black (#000000)
- NO default Tailwind shadows
- Manrope for narrative, Inter for facts
- 90% neutrals, 10% Teal
- Surface nesting for depth, not shadows
