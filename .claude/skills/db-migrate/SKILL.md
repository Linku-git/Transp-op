---
name: db-migrate
description: Create and apply database migrations using Alembic. Generates migration from model changes, applies it, and updates schema docs.
arguments:
  - name: message
    description: Migration description
    required: true
---

# Database Migration

1. Generate migration:
   ```bash
   cd backend && alembic revision --autogenerate -m "{message}"
   ```
2. Review the generated migration file for correctness
3. Apply migration:
   ```bash
   alembic upgrade head
   ```
4. Verify:
   ```bash
   alembic current
   ```
5. Update `Docs/DATABASE_SCHEMA.md` with any schema changes
6. Commit: `[Session-XX] feat: migration - {message}`
