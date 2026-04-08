# Transpop — Claude Code Context

## Project Identity
- **Codename:** Transpop
- **Full Name:** Plateforme d'Orchestration Mobilité RH
- **Type:** Enterprise SaaS — HR mobility orchestration platform
- **Stage:** Sessions 1–44 complete + Replit deployment done. Next: Phase 3 — Mobile MVP (sessions 45–56)

## Tech Stack
- **Backend:** Python 3.12 / FastAPI / SQLAlchemy 2.0 + GeoAlchemy2 / PostgreSQL 15 + PostGIS / Redis + Celery / OR-Tools + scikit-learn
- **Frontend:** React 19 / TypeScript (strict) / Vite / TailwindCSS v4 / Zustand / `@vis.gl/react-google-maps` / Recharts / Vitest
- **Mobile:** Flutter (Dart) / Riverpod / Google Maps / Firebase FCM / Hive + SQLite _(Phase 3, not yet built)_
- **Infra:** Docker Compose (dev) / Replit Reserved VM (production)

## Monorepo Layout
```
backend/    — FastAPI application (Python)
frontend/   — React web dashboard (TypeScript)
mobile/     — Flutter mobile app (Dart) ← NOT YET CREATED (Phase 3)
Docs/       — Project documentation (Obsidian vault with wikilinks)
```

## Current State
@Docs/PROGRESS.md

## Architecture
@Docs/ARCHITECTURE.md

## Coding Conventions
@agents.md

## Key Reference Documents
- Database schema (41 tables): `Docs/DATABASE_SCHEMA.md`
- API endpoints (~130+): `Docs/API_ENDPOINTS.md`
- Frontend pages: `Docs/FRONTEND_PAGES.md`
- Mobile screens: `Docs/MOBILE_PAGES.md`
- Offline capabilities: `Docs/LOCAL_MOBILE_FUNCTIONALITY.md`
- Development roadmap: `Docs/ROADMAP.md`
- Replit changes log: `REPLIT_CHANGES.md`
- Replit session notes: `Docs/sessions/session-replit.md`
- Documentation index: `Docs/INDEX.md`

## Session Workflow
1. Run `/session-start` to load context for the target session
2. Follow atomic task list in `Docs/sessions/session-XX.md`
3. Write tests alongside implementation
4. Run `/session-end` to update progress and documentation

## Commit Convention
Format: `[Session-XX] <type>: <short description>`
Types: feat, fix, refactor, test, docs, chore
Branch: `feature/session-XX-short-description`

## Agent Routing
When working on a task, delegate to the appropriate specialist agent rather than handling it in the main context:

| Task Type | Agent | Trigger Keywords |
|-----------|-------|-----------------|
| Database models, migrations, SQL | @db-engineer | models, schema, migration, query, index, PostGIS |
| Backend API endpoints, services | @backend-dev | endpoint, route, service, FastAPI, Celery |
| React pages, components, stores | @frontend-dev | page, component, dashboard, Zustand, Google Maps |
| Flutter screens, providers | @mobile-dev | screen, widget, provider, Flutter, offline |
| Architecture decisions | @architect | architecture, design, trade-off, ADR |
| UI design review, visual polish | @ui-designer | UI, visual, design system, layout, polish, clean |
| Code review | @reviewer | review, audit, checklist, quality |
| Documentation updates | @docs-manager | docs, changelog, progress, wikilink |
| Docker, CI/CD, deployment | @devops | Docker, pipeline, deploy, GitHub Actions |
| Test planning, QA strategy | @qa-engineer | test plan, regression, coverage, QA |
| Security review, RGPD | @security-auditor | security, OWASP, RGPD, vulnerability, auth |
| Performance optimization | @performance-engineer | performance, profiling, caching, N+1, load test |
| SIRH/ERP integrations | @integration-engineer | integration, SAP, Workday, SIRH, connector, sync |
| Routing/clustering algorithms | @optimizer | optimization, CVRP, clustering, DBSCAN, OR-Tools |

Always delegate rather than handling specialist tasks in the main context. Use `@agent-name` to explicitly invoke an agent.

## Rules
- Always read the session file before starting work
- Write tests BEFORE or ALONGSIDE implementation
- Never leave `print()` debugging in code
- All config via environment variables, never hardcoded
- Use wikilinks `[[reference]]` in documentation
- Update PROGRESS.md after every session
- Keep commits small: one logical change per commit
- PostGIS for all geospatial operations (never app-level distance calc)
- Celery for any async task >5 seconds
- Every API endpoint: minimum 1 happy-path + 1 error-case test

---

## ⚠️ Critical: Replit-Specific Rules

These rules apply when the code runs on Replit. Read `Docs/sessions/session-replit.md` for full context.

### API Client
- `baseURL: ''` (empty string) in `frontend/src/api/client.ts`
- ALL frontend API files MUST use full paths: `/api/v1/...`
- NEVER use paths like `/kpis/dashboard` — always `/api/v1/kpis/dashboard`

### Pydantic v2 Errors
- Always use `extractApiError(err, fallback)` from `@/lib/apiError.ts`
- Handles both `detail: string` and `detail: [{type,loc,msg}]` formats

### Google Maps
- Package: `@vis.gl/react-google-maps` (NOT the older `@react-google-maps/api`)
- `APIProvider` must have `region="MA"` on MapView and MapPicker
- API key: `VITE_GOOGLE_MAPS_API_KEY` Replit secret

### Production Port
- Read `${PORT:-8080}` — Cloud Run/Replit VM injects PORT=8080
- Never hard-code port 8000 in production startup

### CORS
- `allow_origins=["*"]`, `allow_credentials=False` — required for Replit's proxied environment

### Employees Pagination
- Max `page_size=2000` (increased from default) to fetch all 1200 employees in one call

---

## Database: Current State
- **Host:** `helium` (Replit managed PostgreSQL)
- **DB:** `heliumdb`
- **URL:** `postgresql+asyncpg://postgres:password@helium:5432/heliumdb`
- **Tenant ID:** `0cea9745-6aa2-4105-9bdc-341d95999048`
- **19 Alembic migrations** applied
- **41 tables** across 10 groups
- Extensions: PostGIS, pg_trgm

## Live Data Summary
| Entity | Count |
|--------|-------|
| Employees | 1,200 (all with lat/lng) |
| Vehicles | 106 |
| Configuration Transport rows | 591 |
| Total fleet distance | 32,696 km |
| Sites | 4 (Casablanca zones) |
