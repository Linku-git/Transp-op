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

## Agent Routing
When working on a task, delegate to the appropriate specialist agent rather than handling it in the main context:

| Task Type | Agent | Trigger Keywords |
|-----------|-------|-----------------|
| Database models, migrations, SQL | @db-engineer | models, schema, migration, query, index, PostGIS |
| Backend API endpoints, services | @backend-dev | endpoint, route, service, FastAPI, Celery |
| React pages, components, stores | @frontend-dev | page, component, dashboard, Zustand, Leaflet |
| Flutter screens, providers | @mobile-dev | screen, widget, provider, Flutter, offline |
| Architecture decisions | @architect | architecture, design, trade-off, ADR |
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
