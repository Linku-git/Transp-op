---
name: lint-and-format
description: Run linters and formatters across all stacks. Use to enforce code style before commits or reviews.
arguments:
  - name: scope
    description: "Scope: all, backend, frontend, or mobile (default: all)"
    required: false
---

# Lint and Format

Based on scope (default: all):

## Backend (Python)
```bash
cd backend && python -m black app/ tests/ --check --diff
cd backend && python -m isort app/ tests/ --check --diff
cd backend && python -m flake8 app/ tests/ --max-line-length=120
cd backend && python -m mypy app/ --ignore-missing-imports
```

To auto-fix:
```bash
cd backend && python -m black app/ tests/
cd backend && python -m isort app/ tests/
```

## Frontend (TypeScript)
```bash
cd frontend && npx eslint src/ --ext .ts,.tsx
cd frontend && npx prettier src/ --check
cd frontend && npx tsc --noEmit
```

To auto-fix:
```bash
cd frontend && npx eslint src/ --ext .ts,.tsx --fix
cd frontend && npx prettier src/ --write
```

## Mobile (Dart)
```bash
cd mobile && dart format lib/ test/ --set-exit-if-changed
cd mobile && dart analyze lib/
```

To auto-fix:
```bash
cd mobile && dart format lib/ test/
```

Report: files checked, issues found, auto-fixable count.
