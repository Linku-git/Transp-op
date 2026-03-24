---
name: update-docs
description: Update project documentation after code changes. Detects changed files and updates corresponding docs with wikilinks.
---

# Update Documentation

1. Check `git diff --name-only` to identify changed files
2. For each changed area, update the corresponding doc:
   - `backend/app/models/` changes -> update `Docs/DATABASE_SCHEMA.md`
   - `backend/app/api/` changes -> update `Docs/API_ENDPOINTS.md`
   - `frontend/src/pages/` changes -> update `Docs/FRONTEND_PAGES.md`
   - `mobile/lib/screens/` changes -> update `Docs/MOBILE_PAGES.md`
   - `mobile/lib/services/` offline changes -> update `Docs/LOCAL_MOBILE_FUNCTIONALITY.md`
3. Ensure all new files are referenced with `[[wikilinks]]`
4. Update `Docs/INDEX.md` if new documentation pages were added
5. Commit: `[Session-XX] docs: update documentation`
