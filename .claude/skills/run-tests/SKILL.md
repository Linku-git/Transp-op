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

Report for each suite:
- Total tests
- Passing
- Failing (with error summaries)
- Duration
