# Transpop — Coding Agent Instructions

## Purpose
This file provides mandatory rules for any coding agent (Claude, Copilot, or human developer) working on the Transpop codebase. Every session must follow these protocols.

> **Obsidian Vault:** This project uses Obsidian for documentation. All `.md` files are interconnected via `[[wikilinks]]`. Open this folder as an Obsidian vault to navigate the knowledge graph.

---

## 1. Development Workflow Rules

### Before Starting Any Session
1. Read the corresponding session file: [[sessions/session-XX]]
2. Read [[PROGRESS]] to understand current project state
3. Verify all prerequisite sessions are marked COMPLETE
4. Review any files listed as "Files to Modify" in the session file
5. Read this file ([[agents]]) if it's your first session
6. Consult [[ARCHITECTURE]] for system design context
7. Check [[DATABASE_SCHEMA]] if working with models
8. Check [[API_ENDPOINTS]] if working with endpoints

### During a Session
1. Follow the atomic tasks in order (checkbox list in session file)
2. Write tests BEFORE or ALONGSIDE implementation (not after)
3. Run tests after each logical unit of work
4. If a task is blocked, document the blocker in the session file and move to the next unblocked task
5. Never skip a test — if a test fails, fix it before proceeding
6. Keep commits small and focused — one logical change per commit

### After Completing a Session
1. Mark all completed tasks with `[x]` in the session file
2. Update [[PROGRESS]] with session status (COMPLETE / PARTIAL / BLOCKED)
3. Update relevant documentation files (see Section 3)
4. Run the full test suite for affected modules
5. Document any deviations from the plan in the session file under "Notes"
6. List any new technical debt or follow-up items

---

## 2. Testing Standards

### Test Requirements
- Every API endpoint must have at least one happy-path test and one error-case test
- Every model must have creation, validation, and relationship tests
- Every frontend component must have a render test at minimum
- Every optimization algorithm must have correctness tests with known inputs/outputs
- Mobile screens must have widget tests

### Test Organization
- Backend: `backend/tests/` — mirror the `app/` directory structure
- Frontend: `frontend/src/**/__tests__/` — colocated with components
- Mobile: `mobile/test/` — mirror the `lib/` directory structure

### Test Naming Convention
- Backend: `test_<module>_<action>.py` (e.g., `test_sites_crud.py`)
- Frontend: `<Component>.test.tsx` (e.g., `SiteList.test.tsx`)
- Mobile: `<widget>_test.dart` (e.g., `home_screen_test.dart`)

### Running Tests
- Backend: `pytest backend/tests/ -v --tb=short`
- Frontend: `npx vitest run`
- Mobile: `flutter test`

### Test Reporting
After each session, document in the session file:
```
## Test Results
- Tests written: X
- Tests passing: X
- Tests failing: X (list failures with brief description)
- Coverage: X% (if measured)
```

---

## 3. Documentation Update Requirements

### After EVERY Session, Update These Files:

| Condition | Files to Update |
|-----------|----------------|
| New/modified DB models | [[DATABASE_SCHEMA]] |
| New/modified API endpoints | [[API_ENDPOINTS]] |
| New/modified web pages | [[FRONTEND_PAGES]] |
| New/modified mobile screens | [[MOBILE_PAGES]] |
| New offline capabilities | [[LOCAL_MOBILE_FUNCTIONALITY]] |
| Architecture decisions | [[ARCHITECTURE]] |
| Always | [[PROGRESS]] (mark session status) |

### Documentation Format Rules
- Use consistent markdown formatting
- Use `[[wikilinks]]` for cross-referencing between docs
- Include code examples for complex patterns
- Keep descriptions concise — link to source files, don't duplicate code
- Mark any temporary/placeholder implementations with `<!-- TODO: ... -->`

---

## 4. Code Organization Conventions

### Backend (Python/FastAPI)
```
backend/
  app/
    main.py                 # FastAPI app, middleware, startup
    config.py               # Settings (env-based)
    database.py             # SQLAlchemy engine, session
    models/                 # SQLAlchemy models (one file per module)
      __init__.py
      site.py
      employee.py
      vehicle.py
      optimization.py
      financial.py
      content.py
      security.py
      rti.py
      auth.py
    schemas/                # Pydantic schemas (request/response)
      __init__.py
      site.py
      employee.py
      ...
    api/                    # Route handlers
      __init__.py
      v1/
        __init__.py
        sites.py
        employees.py
        ...
    services/               # Business logic
      clustering.py
      routing.py
      optimization.py
      tco_calculator.py
      roi_calculator.py
      excel_parser.py
      geocoding.py
      weather.py
      ...
    tasks/                  # Celery async tasks
      optimization_tasks.py
      sync_tasks.py
      ...
    middleware/              # Auth, RBAC, rate limiting
      auth.py
      rbac.py
      rate_limit.py
    utils/                  # Shared utilities
      geo.py
      validators.py
      ...
  tests/
    conftest.py             # Fixtures, test DB
    test_sites.py
    test_employees.py
    ...
  alembic/                  # DB migrations
    versions/
  requirements.txt
  Dockerfile
```

### Frontend (React/TypeScript)
```
frontend/
  src/
    main.tsx
    App.tsx
    routes.tsx
    api/                    # API client functions
      client.ts
      sites.ts
      employees.ts
      ...
    components/             # Shared components
      ui/                   # Button, Input, Modal, etc.
      layout/               # Sidebar, Header, PageLayout
      maps/                 # MapView, MapMarker, RouteLayer
      charts/               # PieChart, BarChart, Gauge
    pages/                  # Route-level pages
      dashboard/
      sites/
      employees/
      optimization/
      financial/
      reports/
      settings/
      admin/
    stores/                 # Zustand stores
      authStore.ts
      siteStore.ts
      ...
    hooks/                  # Custom hooks
    types/                  # TypeScript interfaces
    utils/                  # Helpers
    i18n/                   # Translations (fr, en)
  public/
  vite.config.ts
  tailwind.config.ts
  tsconfig.json
  Dockerfile
```

### Mobile (Flutter/Dart)
```
mobile/
  lib/
    main.dart
    app.dart
    config/
      theme.dart
      routes.dart
      constants.dart
    models/                 # Data models
    services/               # API, auth, push, location
    providers/              # State management (Riverpod or Provider)
    screens/                # Full screens
      auth/
      home/
      trips/
      tracking/
      content/
      profile/
      security/
    widgets/                # Reusable widgets
    utils/
    l10n/                   # Localization
  test/
  pubspec.yaml
```

---

## 5. Code Quality Checklist

Before marking any session COMPLETE, verify:

- [ ] All new code has type annotations (Python type hints, TypeScript strict, Dart types)
- [ ] No hardcoded secrets, URLs, or credentials (use env variables)
- [ ] No `print()` debugging left in code (use proper logging)
- [ ] API endpoints validate input (Pydantic models in FastAPI)
- [ ] SQL queries use ORM (no raw SQL unless justified and documented)
- [ ] Frontend components handle loading, error, and empty states
- [ ] Mobile screens handle offline gracefully
- [ ] No OWASP Top 10 vulnerabilities introduced
- [ ] CORS, auth, and rate limiting configured for new endpoints
- [ ] Imports are clean (no unused imports)

---

## 6. Git Conventions

### Branch Naming
- `feature/session-XX-short-description`
- `fix/session-XX-issue-description`
- `refactor/session-XX-what-changed`

### Commit Messages
```
[Session-XX] <type>: <short description>

Types: feat, fix, refactor, test, docs, chore
Example: [Session-06] feat: add Site model and CRUD API endpoints
```

### PR/Merge Rules
- Each session = one branch = one PR (when using Git)
- All tests must pass before merge
- Update docs before merge

---

## 7. Error Handling & Reporting

### When Errors Occur During a Session
1. Document the error in the session file under `## Issues Encountered`
2. Include: error message, stack trace (abbreviated), file/line, and resolution
3. If unresolved, mark the task as incomplete and add to `## Blockers`

### Error Documentation Format
```markdown
## Issues Encountered

### Issue 1: [Brief title]
- **Error:** `<error message>`
- **File:** `<file path>:<line>`
- **Cause:** <explanation>
- **Resolution:** <what fixed it> OR **Status:** UNRESOLVED — <next steps>
```

---

## 8. Performance Guidelines

- Use async/await for I/O-bound operations (FastAPI endpoints, external API calls)
- Use Celery tasks for operations >5 seconds (optimization, TCO calculation, report generation)
- Cache frequently read data in Redis (site configs, vehicle catalog, settings)
- Use database indexes on foreign keys and frequently filtered columns
- Paginate all list endpoints (default page_size=20, max=100)
- Use WebSockets for real-time data (RTI vehicle positions), never polling

---

## 9. Environment Variables

All config must come from environment variables. Reference file: `backend/.env.example`

Required variables:
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/transpop
REDIS_URL=redis://localhost:6379/0
AUTH0_DOMAIN=<domain>
AUTH0_CLIENT_ID=<id>
AUTH0_CLIENT_SECRET=<secret>
OSRM_URL=http://localhost:5000
WEATHER_API_KEY=<key>
GOOGLE_MAPS_API_KEY=<key>
FCM_SERVER_KEY=<key>
SECRET_KEY=<random-string>
ENVIRONMENT=development
```

---

## 10. Quick Reference: Session Workflow

```
1. Read session-XX.md
2. Read PROGRESS.md
3. Check prerequisites
4. Create feature branch
5. Implement tasks (write tests alongside)
6. Run tests
7. Update session-XX.md (mark tasks, add test results)
8. Update relevant Docs/*.md files
9. Update PROGRESS.md
10. Commit and push
```

---

## Related Documentation

- [[README]] — Project overview and setup
- [[PROGRESS]] — Session progress tracker
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Complete database schema
- [[API_ENDPOINTS]] — All API endpoints
- [[FRONTEND_PAGES]] — Web dashboard pages
- [[MOBILE_PAGES]] — Mobile app screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline capabilities
- [[ROADMAP]] — Development roadmap and timeline
