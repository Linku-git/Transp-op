# Session 05 — CI/CD & Test Infrastructure

## Phase: 0 — Cadrage & Setup
## Prerequisites: [[sessions/session-02|Session 02]], [[sessions/session-03|Session 03]]

> Previous: [[sessions/session-04|Session 04]] | Next: [[sessions/session-06|Session 06]]

## Complexity: Low

## Objective
Set up GitHub Actions CI pipeline, linting, formatting, pre-commit hooks, and verify the full test suite runs in CI.

---

## Tasks

- [ ] Create `.github/workflows/ci.yml` — CI pipeline:
  - Backend: install deps, lint (ruff), type check (mypy), run pytest
  - Frontend: install deps, lint (eslint), type check (tsc), run vitest
- [ ] Install and configure `ruff` for Python linting (`backend/ruff.toml`)
- [ ] Install and configure `mypy` for Python type checking (`backend/mypy.ini`)
- [ ] Configure ESLint for frontend (`frontend/.eslintrc.json`)
- [ ] Configure Prettier for frontend (`frontend/.prettierrc`)
- [ ] Create `backend/pytest.ini` — Pytest configuration
- [ ] Create `frontend/vitest.config.ts` — Vitest configuration
- [ ] Add `scripts` section to `backend/` — `lint`, `test`, `format` commands
- [ ] Add `scripts` to `frontend/package.json` — `lint`, `test`, `format`, `type-check`
- [ ] Create `.pre-commit-config.yaml` (optional — ruff, prettier, eslint)
- [ ] Verify CI pipeline passes with current code
- [ ] Verify linting catches intentional error, then fix it
- [ ] Verify test commands work locally

## Files to Create
- `.github/workflows/ci.yml`
- `backend/ruff.toml`
- `backend/mypy.ini`
- `backend/pytest.ini`
- `frontend/.eslintrc.json`
- `frontend/.prettierrc`
- `frontend/vitest.config.ts`
- `.pre-commit-config.yaml`

## Tests
- [ ] CI pipeline completes successfully (GitHub Actions green)
- [ ] `ruff check backend/` passes
- [ ] `mypy backend/app/` passes (or only known issues)
- [ ] `pytest backend/tests/ -v` passes all tests
- [ ] `npm run lint` (frontend) passes
- [ ] `npm run test` (frontend) passes

## Acceptance Criteria
- CI pipeline runs on push to any branch
- Backend linting (ruff) and testing (pytest) pass
- Frontend linting (eslint) and testing (vitest) pass
- All existing tests from sessions 02-04 pass in CI
- Pre-commit hooks available for local development

## Related Documentation
- [[PROGRESS]] — Progress tracker
- [[agents]] — Development rules
