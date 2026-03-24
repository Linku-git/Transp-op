---
name: session-end
description: Complete a development session. Runs tests, updates PROGRESS.md, CHANGELOG.md, and documentation, then commits.
arguments:
  - name: session_number
    description: Session number (1-92) being completed
    required: true
  - name: status
    description: "Session status: COMPLETE, PARTIAL, or BLOCKED"
    required: true
---

# End Session

1. Run the full test suite for affected modules:
   - Backend: `pytest backend/tests/ -v --tb=short`
   - Frontend: `npx vitest run` (if frontend changes)
   - Mobile: `flutter test` (if mobile changes)
2. Document test results in the session file
3. Mark completed tasks with `[x]` in `Docs/sessions/session-{session_number}.md`
4. Update `Docs/PROGRESS.md`:
   - Set session status to `{status}`
   - Set date to today
   - Add any notes about deviations or blockers
5. Update relevant documentation files based on what changed
6. Add entry to `Docs/CHANGELOG.md`
7. Commit all changes: `[Session-{session_number}] docs: update progress and documentation`
8. Print summary:
   - Tasks completed vs total
   - Tests written/passing/failing
   - Files modified
   - Any follow-up items or technical debt
