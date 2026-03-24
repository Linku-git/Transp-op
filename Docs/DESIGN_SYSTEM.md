# Design System Specification: The Orchestration Framework

> See also: [[FRONTEND_PAGES]] | [[MOBILE_PAGES]] | [[ARCHITECTURE]]

## 1. Overview & Creative North Star
**The Creative North Star: "The Architectural Conductor"**

The design system moves beyond the "grid-and-border" monotony of standard Enterprise SaaS. As a platform for HR Mobility Orchestration, the UI must feel like a high-end command center—authoritative yet effortless. We achieve this through **Editorial Data Storytelling**: a method where data density is managed not by lines and boxes, but by sophisticated tonal layering and intentional white space.

The "Architectural Conductor" aesthetic relies on:
* **Intentional Asymmetry:** Breaking the expected 12-column rigidity to create focus points for key mobility metrics.
* **Structural Depth:** Replacing traditional borders with background shifts to create a "nested" look that feels carved rather than pasted.
* **The Power of the Void:** Using generous spacing (`spacing.24`) to separate high-intensity data modules, allowing the user's eye to rest between complex tasks.

---

## 2. Colors & Surface Philosophy
The palette is rooted in the "Deep Navy" of institutional trust, punctuated by "Vibrant Teal" to signal movement and progression.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders for sectioning. This is a hard requirement to maintain the premium feel.
* **Separation via Tonal Shift:** Define layout regions by transitioning from `surface` (#f4faff) to `surface_container_low` (#e9f6fd).
* **In-Section Grouping:** Use `surface_container` (#e3f0f8) for secondary modules sitting within a primary workspace.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of semi-translucent materials.
1. **Base Layer:** `surface` (#f4faff) — The global canvas.
2. **Navigation/Context Rails:** `surface_container_low` (#e9f6fd).
3. **Active Workspaces/Cards:** `surface_container_lowest` (#ffffff).
4. **Actionable Overlays:** `surface_bright` with 80% opacity and a 20px backdrop blur.

### Color Tokens

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | #041627 | Primary buttons, key actions, headlines |
| `on_primary` | #ffffff | Text on primary surfaces |
| `primary_container` | #1a2b3c | Gradient endpoints, selected states |
| `secondary` | #006b5c | Interactive elements, teal accents |
| `on_secondary` | #ffffff | Text on secondary surfaces |
| `secondary_container` | #68fadd | Status chips, low-chrome indicators |
| `on_secondary_container` | #007261 | Text on secondary containers |
| `surface` | #f4faff | Global canvas / base layer |
| `surface_container_lowest` | #ffffff | Cards, active workspaces |
| `surface_container_low` | #e9f6fd | Navigation rails, context panels |
| `surface_container` | #e3f0f8 | In-section grouping |
| `surface_container_high` | #dde8f0 | Input field backgrounds (rest state) |
| `surface_container_highest` | #d7e4ec | Recessed/elevated elements |
| `surface_bright` | rgba(255,255,255,0.8) | Floating panels (+ backdrop-blur: 20px) |
| `on_surface` | #111d23 | Primary text (never pure black) |
| `on_surface_variant` | #44474c | Secondary text, metadata, labels |
| `outline_variant` | rgba(196,198,205,0.15) | Ghost borders (accessibility fallback only) |
| `error` | #ba1a1a | Budget overflow, critical alerts |
| `error_container` | #ffdad6 | Error backgrounds |

### Signature Textures
* **The Momentum Gradient:** For primary CTAs and high-level progress indicators, use a linear gradient: `primary` (#041627) to `primary_container` (#1a2b3c) at a 135-degree angle.
* **Glassmorphism:** Floating action panels (e.g., map controls) must use `surface_container_lowest` with a `backdrop-blur` of 12px and 70% opacity.

---

## 3. Typography
The system utilizes a dual-font strategy to balance editorial authority with data precision.

### Font Families
* **Display & Headlines:** Manrope — Used for "The Narrative"
* **Interface & Data:** Inter — Used for "The Facts"

### Type Scale

| Token | Font | Size | Weight | Line Height | Usage |
|-------|------|------|--------|-------------|-------|
| `display-lg` | Manrope | 3.5rem (56px) | 700 | 1.1 | Hero stats (total cost, employee count) |
| `display-md` | Manrope | 2.5rem (40px) | 700 | 1.15 | Page-level KPIs |
| `display-sm` | Manrope | 2rem (32px) | 600 | 1.2 | Section headlines |
| `headline-lg` | Manrope | 1.5rem (24px) | 700 | 1.3 | Card titles, primary stats |
| `headline-md` | Manrope | 1.25rem (20px) | 600 | 1.35 | Sub-section headers |
| `headline-sm` | Manrope | 1rem (16px) | 600 | 1.4 | Widget titles |
| `title-lg` | Inter | 1.125rem (18px) | 600 | 1.4 | Navigation items, prominent labels |
| `title-md` | Inter | 1rem (16px) | 500 | 1.4 | Table headers |
| `title-sm` | Inter | 0.875rem (14px) | 500 | 1.4 | Tab labels |
| `body-lg` | Inter | 1rem (16px) | 400 | 1.5 | Body text |
| `body-md` | Inter | 0.875rem (14px) | 400 | 1.5 | Default interface text |
| `body-sm` | Inter | 0.75rem (12px) | 400 | 1.5 | Dense table data |
| `label-lg` | Inter | 0.875rem (14px) | 500 | 1.3 | Button text |
| `label-md` | Inter | 0.75rem (12px) | 500 | 1.3 | Metadata, timestamps |
| `label-sm` | Inter | 0.6875rem (11px) | 500 | 1.3 | Micro labels, badge text |

### Hierarchy Rules
* **Primary Stats:** `headline-lg` in `on_surface` (#111d23) with `font-weight: 700`
* **Supporting Context:** `label-md` in `on_surface_variant` (#44474c)
* **Never use pure black (#000000):** Always use `on_surface` (#111d23)

---

## 4. Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| `spacing.1` | 0.25rem (4px) | Tight inline gaps |
| `spacing.2` | 0.5rem (8px) | Row padding, icon gaps |
| `spacing.3` | 0.75rem (12px) | Input padding |
| `spacing.4` | 1rem (16px) | Card internal padding |
| `spacing.6` | 1.5rem (24px) | Section padding |
| `spacing.8` | 2rem (32px) | Module gaps |
| `spacing.12` | 3rem (48px) | Large section breaks |
| `spacing.16` | 4rem (64px) | Chapter separators |
| `spacing.20` | 5rem (80px) | Major content divisions |
| `spacing.24` | 6rem (96px) | High-intensity module separation |

---

## 5. Elevation & Depth

### The Layering Principle
Depth is achieved through stacking tokens. To elevate a component:
* Place a `surface_container_highest` (#d7e4ec) element inside a `surface_container_low` (#e9f6fd) environment. This creates a "recessed" or "elevated" effect without a single pixel of shadow.

### Ambient Shadows
When a component must float (e.g., a modal or a context menu), use **Ambient Shadows**:
* **Shadow Color:** A 6% opacity tint of `on_surface` (#111d23).
* **Spread:** High blur (32px to 64px), 0px spread.

```css
/* Ambient shadow tokens */
--shadow-sm: 0 2px 32px rgba(17, 29, 35, 0.06);
--shadow-md: 0 4px 48px rgba(17, 29, 35, 0.06);
--shadow-lg: 0 8px 64px rgba(17, 29, 35, 0.06);
```

### The "Ghost Border" Fallback
If contrast ratios require a boundary for accessibility:
* Use `outline_variant` (#c4c6cd) at **15% opacity**.
* **Forbidden:** 100% opaque, high-contrast borders.

---

## 6. Components

### High-Density Tables
* **No Dividers:** Remove all horizontal/vertical lines
* **Row Padding:** `spacing.2` (8px)
* **Hover:** `surface_container_low` background transition
* **Number Alignment:** Right-aligned, tabular-lining figures
* **Text Alignment:** Left-aligned

### Interactive Maps & Charts
* **Map Base:** Custom "Silver/Navy" style
* **Movement Paths:** `secondary` (#006b5c) overlays
* **Positive Growth:** `secondary` (#006b5c)
* **Budget Overflow:** `error` (#ba1a1a)
* **Grid Lines:** `surface_container_highest` at 20% opacity

### Buttons

| Variant | Background | Text | Border Radius |
|---------|-----------|------|---------------|
| Primary | `primary` (#041627) | `on_primary` (#fff) | 0.375rem |
| Primary Gradient | linear-gradient(135deg, #041627, #1a2b3c) | `on_primary` | 0.375rem |
| Secondary | `secondary` (#006b5c) | `on_secondary` (#fff) | 0.375rem |
| Ghost | transparent | `on_surface` (#111d23) | 0.375rem |
| Danger | `error` (#ba1a1a) | #ffffff | 0.375rem |

### Status Chips (Low-Chrome)

| Status | Background | Text |
|--------|-----------|------|
| Active | `secondary_container` (#68fadd) | `on_secondary_container` (#007261) |
| Pending | `surface_container_high` (#dde8f0) | `on_surface_variant` (#44474c) |
| Error | `error_container` (#ffdad6) | `error` (#ba1a1a) |
| Inactive | `surface_container` (#e3f0f8) | `on_surface_variant` (#44474c) |

### Input Fields
* **Rest State:** No border, `surface_container_high` (#dde8f0) background
* **Focus State:** 1px `secondary` (#006b5c) ghost border at 40% opacity
* **Padding:** `spacing.3` (12px)
* **Border Radius:** 0.375rem

---

## 7. Do's and Don'ts

### Do:
* Use white space as a tool — `spacing.16`+ to separate data "chapters"
* Layer vertically — `surface` > `surface_container_low` > `surface_container_highest`
* Color for meaning — Teal only for interactive elements or innovation metrics
* Use Manrope for narrative, Inter for facts
* Use ambient shadows (high blur, low opacity) when floating is required

### Don't:
* Use 1px solid borders for containers (hard rule)
* Default to shadows — use tonal shifts first
* Over-color — 90% neutrals, 10% Teal
* Use pure black (#000000) — use `on_surface` (#111d23)
* Use heavy saturated badges — use low-chrome chips instead

---

## 8. TailwindCSS Integration

### Custom Theme Extension
```js
// tailwind.config.ts extend section
colors: {
  primary: { DEFAULT: '#041627', container: '#1a2b3c' },
  secondary: { DEFAULT: '#006b5c', container: '#68fadd' },
  surface: {
    DEFAULT: '#f4faff',
    'container-lowest': '#ffffff',
    'container-low': '#e9f6fd',
    container: '#e3f0f8',
    'container-high': '#dde8f0',
    'container-highest': '#d7e4ec',
  },
  on: {
    primary: '#ffffff',
    secondary: '#ffffff',
    'secondary-container': '#007261',
    surface: '#111d23',
    'surface-variant': '#44474c',
  },
  error: { DEFAULT: '#ba1a1a', container: '#ffdad6' },
  outline: { variant: 'rgba(196,198,205,0.15)' },
},
fontFamily: {
  display: ['Manrope', 'sans-serif'],
  sans: ['Inter', 'sans-serif'],
},
```

---

## Related Documentation
- [[FRONTEND_PAGES]] — Web dashboard pages
- [[MOBILE_PAGES]] — Mobile app screens
- [[ARCHITECTURE]] — System architecture
