---
name: run-tests
description: Run test suites for backend, frontend, and/or mobile. Reports total, passing, and failing tests.
arguments:
  - name: scope
    description: "Test scope: all, backend, frontend, or mobile (default: all)"
    required: false
---

# Run Tests

Based on scope (default: all):

## Backend
```bash
cd backend && python -m pytest tests/ -v --tb=short
```

## Frontend
```bash
cd frontend && npx vitest run
```

## Mobile
```bash
cd mobile && flutter test
```

## Browser (optional scope: `browser`)
Open the running app in Google Chrome and verify no runtime errors:
```bash
start chrome http://localhost:5173
```
Navigate to key pages (dashboard, sites, employees) and check:
- Chrome DevTools Console: no JS errors or React warnings
- Network tab: no failed API requests (4xx/5xx) or CORS errors
- Pages render correctly (no blank screens, no layout breakage)

Report: pages visited, console errors found, network failures.

---

Report for each suite:
- Total tests
- Passing
- Failing (with error summaries)
- Duration
