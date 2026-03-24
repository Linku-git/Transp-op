# Session 77 — SIRH Connection Framework

> Previous: [[sessions/session-76|Session 76 — Value Measurement Engine]] | Next: [[sessions/session-78|Session 78 — SAP SuccessFactors Connector]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-09|Session 09]] completed
## Complexity: High

## Objective
Build the foundational framework for connecting to external SIRH (Human Resources Information Systems) such as SAP, Workday, Talentsoft, and Sage. This includes data models for connections, sync logs, and conflict tracking, along with a base sync engine that supports delta updates and configurable conflict resolution strategies.

---

## Tasks
- [ ] Create SIRHConnection model with fields: tenant_id, provider (enum: sap/workday/talentsoft/sage), config (JSON, encrypted), sync_frequency, last_sync_at, status
- [ ] Create SyncLog model with fields: connection_id (FK to SIRHConnection), started_at, completed_at, records_created, records_updated, records_failed, errors (JSON), status
- [ ] Create SyncConflict model with fields: sync_log_id (FK to SyncLog), employee_id, field_name, platform_value, sirh_value, resolution (enum: platform_wins/sirh_wins/manual/unresolved)
- [ ] Create Alembic migration for SIRHConnection table
- [ ] Create Alembic migration for SyncLog table
- [ ] Create Alembic migration for SyncConflict table
- [ ] Implement base sync framework with delta update support (only sync changed records since last_sync_at)
- [ ] Implement configurable conflict resolution strategy (SIRH wins / platform wins / manual)
- [ ] Create API endpoint POST `/sirh/connections` to register a new SIRH connection
- [ ] Create API endpoint GET `/sirh/connections` to list all connections for a tenant
- [ ] Create API endpoint PUT `/sirh/connections/{id}` to update a connection
- [ ] Create API endpoint DELETE `/sirh/connections/{id}` to remove a connection
- [ ] Create API endpoint POST `/sirh/sync/{id}` to trigger a sync for a given connection

## Files to Create/Modify
- `backend/app/models/sirh_connection.py`
- `backend/app/models/sync_log.py`
- `backend/app/models/sync_conflict.py`
- `backend/alembic/versions/xxx_create_sirh_connection.py`
- `backend/alembic/versions/xxx_create_sync_log.py`
- `backend/alembic/versions/xxx_create_sync_conflict.py`
- `backend/app/services/sirh/sync_engine.py`
- `backend/app/services/sirh/conflict_resolver.py`
- `backend/app/api/routes/sirh.py`
- `backend/app/schemas/sirh.py`

## Tests
- [ ] Test SIRHConnection CRUD operations (create, read, update, delete)
- [ ] Test SyncLog creation and status tracking
- [ ] Test SyncConflict creation and resolution
- [ ] Test base sync framework triggers delta updates correctly
- [ ] Test conflict detection when platform and SIRH values differ
- [ ] Test conflict resolution with each strategy (SIRH wins, platform wins, manual)
- [ ] Test API endpoints return correct responses and status codes
- [ ] Test encrypted config storage and retrieval

## Acceptance Criteria
- All three models are created with proper relationships and constraints
- Alembic migrations run without errors and are reversible
- Sync framework supports delta updates based on last_sync_at timestamp
- Conflict resolution is configurable per connection (SIRH wins, platform wins, manual)
- All CRUD API endpoints for connections work correctly
- Triggering a sync via POST creates a SyncLog and processes records
- Conflicts are detected and stored in SyncConflict table
- Config JSON field is encrypted at rest

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
