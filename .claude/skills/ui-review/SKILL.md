---
name: ui-review
description: "Audit UI code for visual quality and design system compliance. Scans React components or Flutter widgets for violations, layout issues, and polish opportunities. Fixes problems automatically when possible."
arguments:
  - name: target
    description: "File path, directory, or 'all' to audit. Examples: 'frontend/src/pages/dashboard/', 'mobile/lib/screens/home/', 'all'"
    required: false
  - name: fix
    description: "Set to 'true' to auto-fix violations instead of just reporting them. Default: false (report only)"
    required: false
---

# UI Review — Visual Quality Audit

First, read `Docs/DESIGN_SYSTEM.md` for the full design specification.

## Determine scope

- If `target` is a file path: audit that single file
- If `target` is a directory: audit all `.tsx`, `.jsx`, `.dart` files in that directory recursively
- If `target` is "all" or not provided: audit all UI files:
  - `frontend/src/pages/**/*.tsx`
  - `frontend/src/components/**/*.tsx`
  - `mobile/lib/screens/**/*.dart`
  - `mobile/lib/widgets/**/*.dart`

## For each file, check these categories:

### Category 1: Hard Violations (MUST FIX)
Scan for patterns that break the design system:

1. **Border violations** — grep for: `border`, `border-solid`, `border-t`, `border-b`, `border-l`, `border-r`, `divide-x`, `divide-y` used for layout separation (not input focus states)
2. **Pure black** — grep for: `#000000`, `#000`, `text-black`, `bg-black`, `Colors.black`, `Color(0xFF000000)`
3. **Default shadows** — grep for: `shadow-sm`, `shadow-md`, `shadow-lg`, `shadow-xl`, `shadow-2xl` (Tailwind defaults instead of custom ambient shadows)
4. **Font misuse** — Manrope used for body/label text, or Inter used for display/headline text
5. **Color overuse** — more than ~10% of elements using `secondary`/teal for non-interactive purposes
6. **Saturated badges** — `bg-green-500`, `bg-red-500`, `bg-blue-500` style badges instead of low-chrome chips using container tokens
7. **Hardcoded colors** — arbitrary hex values instead of design system tokens (`bg-[#xxx]` instead of `bg-surface-container-low`)

### Category 2: Visual Quality (SHOULD FIX)
Check for polish issues:

1. **Spacing** — cramped layouts missing `spacing.16`+ between sections, inconsistent padding
2. **Typography hierarchy** — missing size/weight differentiation between heading levels
3. **Surface nesting** — flat layouts without proper surface layering for depth
4. **Empty states** — lists/tables missing designed empty states
5. **Loading states** — missing skeleton placeholders or using generic spinners
6. **Number alignment** — numbers in tables not right-aligned
7. **Text contrast** — metadata using `on-surface` instead of lighter `on-surface-variant`

### Category 3: Layout & Composition (NICE TO HAVE)
Look for opportunities:

1. **Visual hierarchy** — key stats not visually prominent enough
2. **White space** — sections too close together, missing breathing room
3. **Responsive issues** — hardcoded widths, missing responsive breakpoints
4. **Consistency** — similar components styled differently across pages

## Output format

Print a report:

```
# UI Review Report

## Summary
- Files scanned: X
- Hard violations: X (must fix)
- Quality issues: X (should fix)
- Polish opportunities: X (nice to have)

## Hard Violations
| File | Line | Rule | Current | Should Be |
|------|------|------|---------|-----------|
| ... | ... | ... | ... | ... |

## Quality Issues
| File | Line | Issue | Suggestion |
|------|------|-------|------------|
| ... | ... | ... | ... |

## Polish Opportunities
- ...

## Clean Files (no issues)
- ...
```

## If fix = "true"

After generating the report, automatically fix:
1. All hard violations (Category 1)
2. All quality issues (Category 2) where the fix is unambiguous

For each fix, use the Edit tool to make the change. Preserve all functionality — never break interactivity.

Do NOT fix Category 3 items automatically — report them for human review.

After fixing, re-scan to confirm all hard violations are resolved and print an updated summary.

---

## Live Browser Check

After the static code audit, verify the app in Google Chrome:

1. **Open Chrome**:
   ```bash
   start chrome http://localhost:5173
   ```
2. **Check Console** — Open DevTools (F12 > Console tab) and look for:
   - JavaScript errors (red)
   - React warnings (yellow)
   - Failed network requests (4xx/5xx in Network tab)
   - CORS errors
3. **Check Visual Rendering**:
   - Page loads without blank screen
   - Navigation between pages works
   - No layout breakage or missing elements
   - Design system tokens applied (no raw borders, no pure black, correct fonts)
4. **Report** any console errors or visual issues found alongside the static audit report.
