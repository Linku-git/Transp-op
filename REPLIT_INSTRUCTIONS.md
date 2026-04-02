# Transpop — Replit Agent Instructions

## Your Role

You are a **refinement agent**. The Transpop codebase has been built across 44 development sessions by Claude Code. Your job is to:

1. **Initialize** the project on Replit infrastructure
2. **Refine** existing code (sessions 1-44 only)
3. **Document** every change you make for Claude Code to review later

**You must NEVER write new features beyond session 44.** No new sessions, no new modules, no new pages. You only improve what already exists.

---

## Phase 1: Project Initialization

### 1.1 — Install System Dependencies

The backend requires PostGIS system libraries:

```bash
# Nix packages needed (via replit.nix or Replit package manager)
postgresql_15      # with PostGIS extension
redis
python311
nodejs_18
gcc
libpq
geos
proj
gdal
```

### 1.2 — Set Up PostgreSQL + PostGIS

```bash
# Create database
createdb transpop
psql transpop -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql transpop -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

### 1.3 — Set Up Environment Variables

Copy and adapt `.env.example` to `.env` in the backend directory. Key overrides for Replit:

```env
DATABASE_URL=postgresql+asyncpg://runner:@localhost:5432/transpop
DATABASE_URL_SYNC=postgresql+psycopg2://runner:@localhost:5432/transpop
REDIS_URL=redis://localhost:6379/0
OSRM_URL=http://localhost:5000
SECRET_KEY=replit-dev-secret-change-me
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

Note: Auth0, Weather API, Google Maps, and Firebase keys are optional for refinement work. Use placeholder values.

### 1.4 — Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 1.5 — Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 1.6 — Start Services

Run these in parallel (use Replit's multi-process support):

| Service | Command | Port |
|---------|---------|------|
| Redis | `redis-server` | 6379 |
| PostgreSQL | (managed by Replit) | 5432 |
| Backend | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` | 8000 |
| Frontend | `cd frontend && npm run dev -- --host 0.0.0.0` | 5173 |
| Celery Worker | `cd backend && celery -A app.tasks worker --loglevel=info` | — |

### 1.7 — Verify Health

- Backend: `curl http://localhost:8000/health` should return `{"status": "healthy"}`
- Frontend: Open `http://localhost:5173` — should load the React app
- API Docs: `http://localhost:8000/docs` — Swagger UI

---

## Phase 2: Refinement Scope

### What You CAN Do

- Fix bugs, typos, broken imports, runtime errors
- Improve TypeScript types, remove `any` types
- Fix CSS/layout issues, improve responsiveness
- Optimize slow queries or components
- Fix broken tests, add missing edge-case tests
- Improve error handling at API boundaries
- Fix accessibility issues (aria labels, keyboard nav)
- Improve loading/error/empty states in components
- Fix i18n issues (missing translations)
- Refactor for clarity (only if something is genuinely unclear)
- Fix security issues (XSS, injection, missing validation)

### What You CANNOT Do

- Add new features, pages, endpoints, or models
- Implement session 45+ tasks
- Add new npm/pip dependencies (unless fixing a broken existing feature)
- Change the database schema (no new migrations)
- Modify the architecture or tech stack
- Delete or rename existing API endpoints
- Change the design system tokens or color palette

---

## Phase 3: Documentation of Changes

**This is critical.** Claude Code needs to know exactly what you changed and why.

### 3.1 — Change Log File

Create and maintain `REPLIT_CHANGES.md` in the project root. Every change must be logged:

```markdown
# Replit Agent Changes Log

> This file documents all changes made by Replit Agent for Claude Code to review.
> Do NOT delete this file. Claude Code will process it in the next session.

## Summary
- Total files modified: N
- Categories: bug fixes, style fixes, type fixes, test fixes, etc.

---

## Changes

### [YYYY-MM-DD HH:MM] Category: Short description
- **Files:** `path/to/file1.ts`, `path/to/file2.py`
- **What:** Describe exactly what was changed
- **Why:** Explain the reason (bug, typo, broken layout, etc.)
- **Before:** Brief description or code snippet of old behavior
- **After:** Brief description or code snippet of new behavior
- **Risk:** Low / Medium (never make high-risk changes)

---
```

### 3.2 — Per-File Change Comments

When modifying a file, add a comment at the change site:

```typescript
// [Replit-Fix] Fixed missing null check — was causing runtime crash on empty data
```

```python
# [Replit-Fix] Added try/except for geocoding timeout — was failing silently
```

These inline markers help Claude Code find and review changes quickly.

### 3.3 — Test Changes

If you fix or add tests, document in `REPLIT_CHANGES.md`:

```markdown
### [2026-04-02 14:30] Test Fix: SiteList render test
- **Files:** `frontend/src/pages/sites/__tests__/SiteList.test.tsx`
- **What:** Fixed mock data to match updated SiteResponse schema
- **Why:** Test was failing due to schema change in session-42
- **Before:** Test used `{ name: "Site A" }` without required `id` field
- **After:** Test uses `{ id: "uuid", name: "Site A", ...requiredFields }`
- **Risk:** Low
```

---

## Phase 4: Quality Checks

Before considering any refinement complete, verify:

1. **Backend tests pass:** `cd backend && pytest tests/ -v --tb=short`
2. **Frontend tests pass:** `cd frontend && npx vitest run`
3. **TypeScript compiles:** `cd frontend && npx tsc --noEmit`
4. **No console errors:** Check browser DevTools console
5. **API health:** `curl http://localhost:8000/health`
6. **Lint clean:** `cd frontend && npm run lint`

---

## Project Architecture Quick Reference

### Backend (Python 3.11 / FastAPI)

```
backend/
  app/
    main.py              # FastAPI app entry
    config.py            # Env-based settings
    database.py          # SQLAlchemy async engine
    models/              # SQLAlchemy models (site, employee, vehicle, optimization, financial, etc.)
    schemas/             # Pydantic v2 request/response
    api/v1/              # Route handlers
    services/            # Business logic (clustering, routing, tco, roi, etc.)
    tasks/               # Celery async tasks
    middleware/           # Auth, RBAC
  tests/                 # pytest tests
  alembic/               # DB migrations
```

### Frontend (React 18 / TypeScript / Vite)

```
frontend/src/
  pages/                 # Route-level pages (dashboard, sites, employees, optimization, financial, reports, settings)
  components/
    ui/                  # Button, Card, Modal, Input, Badge, DataTable, etc.
    layout/              # Sidebar, Header, AppLayout
    maps/                # MapView, markers, routes, legend
    charts/              # PieChart, BarChart, GaugeChart, Histogram
    optimization/        # MetricsPanel, RouteList, ClusterTable
    import/              # SheetPreview, ValidationErrors
    sites/               # ShiftConfigPanel, SiteSummaryCards
  api/                   # Axios API client functions
  stores/                # Zustand state stores
  types/                 # TypeScript interfaces
```

### Design System: "Azure Velocity"

- Primary color: `#0058be` (Azure Blue)
- Font: Inter only
- Icons: Material Symbols Outlined
- Cards: `bg-white rounded-xl shadow-sm border border-outline-variant/10`
- Full spec: `Docs/DESIGN_SYSTEM.md`

### Database: PostgreSQL 15 + PostGIS

- 38 tables across 10 groups
- Migrations via Alembic
- Schema doc: `Docs/DATABASE_SCHEMA.md`

### Key Ports

| Service | Port |
|---------|------|
| PostgreSQL | 5432 |
| Redis | 6379 |
| Backend API | 8000 |
| Frontend | 5173 |
| OSRM (optional) | 5000 |

---

## Important Files to Read First

1. `CLAUDE.md` — Full project context and conventions
2. `agents.md` — Coding rules and workflow
3. `Docs/PROGRESS.md` — What's been built (sessions 1-44)
4. `Docs/ARCHITECTURE.md` — System design
5. `Docs/DATABASE_SCHEMA.md` — All tables
6. `Docs/API_ENDPOINTS.md` — All endpoints
7. `Docs/FRONTEND_PAGES.md` — All web pages
8. `Docs/DESIGN_SYSTEM.md` — UI design tokens

---

## Rules Recap

1. **Refine only** — no new features beyond session 44
2. **Document everything** — log every change in `REPLIT_CHANGES.md`
3. **Mark inline** — use `[Replit-Fix]` comments at change sites
4. **Test after changes** — all tests must pass
5. **Ask before breaking changes** — if a fix requires changing an API contract, ask the user first
6. **Preserve conventions** — follow existing code patterns, don't introduce new ones
7. **No schema changes** — don't add/modify database tables or migrations
