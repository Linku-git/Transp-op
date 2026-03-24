# Testing Rules

## Principle
Write tests BEFORE or ALONGSIDE implementation, never after.

## Coverage Requirements
- Every API endpoint: 1 happy-path + 1 error-case test minimum
- Every SQLAlchemy model: creation, validation, relationship tests
- Every React component: render test minimum
- Every optimization algorithm: correctness test with known inputs/outputs
- Every Flutter screen: widget test

## Commands
- Backend: `pytest backend/tests/ -v --tb=short`
- Frontend: `npx vitest run`
- Mobile: `flutter test`

## Reporting
After each session, document in the session file:
- Tests written: N
- Tests passing: N
- Tests failing: N (with descriptions)
- Coverage: N% (if measured)

## Fixtures & Setup
- Backend: `backend/tests/conftest.py` — test database, test client, sample data factories
- Frontend: `frontend/src/test/setup.ts` — test provider wrappers, mock API
- Mobile: `mobile/test/helpers/` — widget test wrappers, mock providers
