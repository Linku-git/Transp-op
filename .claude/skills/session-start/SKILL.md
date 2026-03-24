---
name: session-start
description: Start a new development session by loading context for a specific session number. Reads session file, checks prerequisites, and creates feature branch.
arguments:
  - name: session_number
    description: Session number (1-92) to start working on
    required: true
---

# Start Session

1. Read `Docs/sessions/session-{session_number}.md` for task list and requirements
2. Read `Docs/PROGRESS.md` to verify prerequisites are COMPLETE
3. Check the session's prerequisite sessions are all marked COMPLETE
4. Read `agents.md` to refresh coding conventions
5. If the session involves:
   - Database models: read `Docs/DATABASE_SCHEMA.md`
   - API endpoints: read `Docs/API_ENDPOINTS.md`
   - Frontend pages: read `Docs/FRONTEND_PAGES.md`
   - Mobile screens: read `Docs/MOBILE_PAGES.md`
   - Offline features: read `Docs/LOCAL_MOBILE_FUNCTIONALITY.md`
6. Create the feature branch: `git checkout -b feature/session-{session_number}-<title>`
7. Print a summary of:
   - Session objective
   - Number of tasks
   - Files to create/modify
   - Any blockers or dependencies
