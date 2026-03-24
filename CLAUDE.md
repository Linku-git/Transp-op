# Transpop — Claude Code Context

## Project Identity
- **Codename:** Transpop
- **Full Name:** Plateforme d'Orchestration Mobilite RH
- **Type:** Enterprise SaaS — HR mobility orchestration platform
- **Stage:** Pre-code, all documentation complete, 92 development sessions planned

## Tech Stack
- **Backend:** Python 3.11+ / FastAPI / SQLAlchemy 2.0 + GeoAlchemy2 / PostgreSQL 15 + PostGIS / Redis + Celery / OR-Tools + scikit-learn
- **Frontend:** React 18+ / TypeScript (strict) / Vite / TailwindCSS / Zustand / Leaflet / Recharts / Vitest
- **Mobile:** Flutter (Dart) / Riverpod / Google Maps / Firebase FCM / Hive + SQLite
- **Infra:** Docker Compose (dev) / Kubernetes (prod) / GitHub Actions / Terraform

## Monorepo Layout
```
backend/    — FastAPI application (Python)
frontend/   — React web dashboard (TypeScript)
mobile/     — Flutter mobile app (Dart)
Docs/       — Project documentation (Obsidian vault with wikilinks)
```

## Current State
@Docs/PROGRESS.md

## Architecture
@Docs/ARCHITECTURE.md

## Coding Conventions
@agents.md

## Key Reference Documents
- Database schema (37 tables): `Docs/DATABASE_SCHEMA.md`
- API endpoints (~125): `Docs/API_ENDPOINTS.md`
- Frontend pages: `Docs/FRONTEND_PAGES.md`
- Mobile screens: `Docs/MOBILE_PAGES.md`
- Offline capabilities: `Docs/LOCAL_MOBILE_FUNCTIONALITY.md`
- Development roadmap: `Docs/ROADMAP.md`
- Full PRD: `Employee_Transport_Optimization_PRD_v3.md`
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
