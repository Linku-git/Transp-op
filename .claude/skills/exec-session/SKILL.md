---
name: exec-session
description: "Execute a full development session end-to-end: load context, check prerequisites, create branch, implement all tasks with appropriate agents, run tests, update docs, and commit. One command to run an entire session."
arguments:
  - name: session_number
    description: Session number (1-92) to execute
    required: true
---

# Execute Full Session

This skill runs an entire session from start to finish. Follow each phase in order.

---

## PHASE 1 — LOAD CONTEXT

1. Read `Docs/sessions/session-{session_number}.md` for the task list, objective, files, and acceptance criteria
2. Read `Docs/PROGRESS.md` — verify ALL prerequisite sessions are marked COMPLETE. If any prerequisite is NOT COMPLETE, **stop immediately** and report the blocker.
3. Read `agents.md` for coding conventions
4. Based on the session's tasks, read the relevant reference docs:
   - If tasks mention models, schema, migration → read `Docs/DATABASE_SCHEMA.md`
   - If tasks mention endpoints, API, routes → read `Docs/API_ENDPOINTS.md`
   - If tasks mention pages, dashboard, components → read `Docs/FRONTEND_PAGES.md` and `Docs/DESIGN_SYSTEM.md`
   - If tasks mention screens, mobile, Flutter → read `Docs/MOBILE_PAGES.md` and `Docs/LOCAL_MOBILE_FUNCTIONALITY.md`
   - If tasks mention Docker, CI/CD, deploy → read `Docs/ARCHITECTURE.md`
5. Create the feature branch: `git checkout -b feature/session-{session_number}-<short-title>`
6. Print a brief session summary (objective, task count, key files)

---

## PHASE 2 — DETERMINE AGENTS NEEDED

Analyze the session tasks and determine which specialist agents to invoke. Map tasks to agents:

| Task Keywords | Agent to Use |
|---------------|-------------|
| SQLAlchemy model, migration, schema, PostGIS, index | `@db-engineer` |
| API endpoint, route handler, Pydantic schema, service | `@backend-dev` |
| React page, component, Zustand store, Leaflet map | `@frontend-dev` |
| Flutter screen, widget, Riverpod provider, offline | `@mobile-dev` |
| Docker, Dockerfile, CI pipeline, GitHub Actions | `@devops` |
| Architecture decision, system design, trade-off | `@architect` |
| OR-Tools, CVRP, clustering, DBSCAN, optimization algo | `@optimizer` |
| SIRH, SAP, Workday, ERP connector, sync | `@integration-engineer` |
| Security, OWASP, RGPD, auth flow, vulnerability | `@security-auditor` |
| Performance, caching, N+1, profiling, load test | `@performance-engineer` |

Most sessions need 1-3 agents. Some sessions are single-domain (e.g., pure backend), some are cross-cutting (e.g., model + API + frontend page).

---

## PHASE 3 — IMPLEMENT

Work through the task list **in order**. For each task:

1. **Delegate to the appropriate agent** based on the mapping above. Launch agents in parallel when tasks are independent.
2. **Write tests alongside implementation** — never defer tests to the end.
3. **Run tests after each logical unit** to catch issues early.
4. **Commit after each significant unit of work** using format: `[Session-{session_number}] <type>: <description>`
   - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
   - Keep commits small and focused — one logical change per commit

### Implementation Rules (MUST follow)
- All functions have type annotations
- No `print()` debugging — use `logging`
- No hardcoded secrets/URLs — use environment variables
- Backend: Pydantic v2 for validation, SQLAlchemy ORM only, async endpoints
- Frontend: TypeScript strict, TailwindCSS, handle loading/error/empty states
- Mobile: Dart strong typing, Riverpod, offline-first, active-only geolocation
- PostGIS for all geospatial operations
- Celery for any operation > 5 seconds

---

## PHASE 4 — VERIFY

After all tasks are implemented:

1. **Run the full test suite** for all affected stacks:
   - Backend: `docker compose exec backend python -m pytest tests/ -v --tb=short`
   - Frontend (if changed): `cd frontend && npx vitest run`
   - Mobile (if changed): `cd mobile && flutter test`
2. **Verify acceptance criteria** from the session file — test each criterion manually if needed
3. **Run UI review** on any new frontend/mobile code (invoke `@ui-designer` agent)
4. If any test fails, **fix it before proceeding** — never leave failing tests

---

## PHASE 5 — UPDATE DOCUMENTATION

1. **Mark tasks** with `[x]` in `Docs/sessions/session-{session_number}.md`
2. **Add test results** to the session file:
   ```
   ## Test Results
   - Tests written: X
   - Tests passing: X
   - Tests failing: X
   - Coverage: X%
   ```
3. **Add notes** about any deviations, decisions, or issues encountered
4. **Update `Docs/PROGRESS.md`**:
   - Set session status to `COMPLETE` (or `PARTIAL`/`BLOCKED` if applicable)
   - Set date to today
   - Add brief notes
   - Update phase completion count (e.g., `2/5` → `3/5`)
   - Update total count
5. **Update relevant documentation** based on what changed:
   - New/modified DB models → `Docs/DATABASE_SCHEMA.md`
   - New/modified API endpoints → `Docs/API_ENDPOINTS.md`
   - New/modified web pages → `Docs/FRONTEND_PAGES.md`
   - New/modified mobile screens → `Docs/MOBILE_PAGES.md`
   - New offline capabilities → `Docs/LOCAL_MOBILE_FUNCTIONALITY.md`
   - Architecture decisions → `Docs/ARCHITECTURE.md` + create ADR if significant
6. **Add CHANGELOG entry** to `Docs/CHANGELOG.md`:
   ```
   ## [Session-{session_number}] — YYYY-MM-DD
   ### Added
   - ...
   ### Changed
   - ...
   ### Fixed
   - ...
   ```

---

## PHASE 6 — FINAL COMMIT

1. Stage and commit all documentation updates:
   `[Session-{session_number}] docs: update progress and documentation`
2. Verify `git status` shows a clean working tree
3. **Print final summary**:
   - Tasks completed vs total
   - Tests written / passing / failing
   - Files created / modified
   - Commits made (list with short messages)
   - Next session number and title
   - Any follow-up items or technical debt
