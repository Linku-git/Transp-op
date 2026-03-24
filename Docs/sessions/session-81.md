# Session 81 — SIRH Sync Dashboard

> Previous: [[sessions/session-80|Session 80 — Talentsoft & Sage Connectors]] | Next: [[sessions/session-82|Session 82 — Operator Sizing Plan Export]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-77|Session 77]] completed
## Complexity: Medium

## Objective
Build an administrative dashboard for managing SIRH connections and monitoring synchronization activity, including a sync history log, conflict resolution queue, error details view, and a connection management page with setup wizard and test functionality.

---

## Tasks
- [ ] Create SIRHSyncDashboardPage component at `/admin/sirh/sync`
- [ ] Build sync history log table displaying: started_at, completed_at, records created/updated/failed, status
- [ ] Implement conflict resolution queue: list unresolved conflicts with resolution action buttons (platform_wins, sirh_wins, manual)
- [ ] Add expandable error details per sync log entry
- [ ] Implement auto-refresh for sync status (polling interval)
- [ ] Create API endpoint GET `/sirh/sync/status` to fetch current sync status and recent history
- [ ] Create API endpoint GET `/sirh/sync/conflicts` to list unresolved conflicts
- [ ] Create API endpoint PUT `/sirh/sync/conflicts/{id}/resolve` to resolve a conflict with chosen strategy
- [ ] Create SIRHConnectionsPage component at `/admin/sirh`
- [ ] Build connection list view with status indicators
- [ ] Build add connection wizard (provider selection, credentials input, sync frequency configuration)
- [ ] Add test connection button that validates credentials against the SIRH provider
- [ ] Add routing for both dashboard pages

## Files to Create/Modify
- `frontend/src/pages/admin/SIRHSyncDashboardPage.tsx`
- `frontend/src/pages/admin/SIRHConnectionsPage.tsx`
- `frontend/src/components/sirh/SyncHistoryTable.tsx`
- `frontend/src/components/sirh/ConflictResolutionQueue.tsx`
- `frontend/src/components/sirh/ConnectionWizard.tsx`
- `frontend/src/services/sirhApi.ts`
- `backend/app/api/routes/sirh.py` (add sync status and conflict endpoints)
- `frontend/src/router.tsx` (add routes)

## Tests
- [ ] Test SIRHSyncDashboardPage renders sync history table correctly
- [ ] Test sync history table displays correct data columns
- [ ] Test conflict resolution queue lists unresolved conflicts
- [ ] Test conflict resolution buttons trigger correct API calls (platform_wins, sirh_wins, manual)
- [ ] Test error details expand and collapse correctly
- [ ] Test auto-refresh updates sync status
- [ ] Test SIRHConnectionsPage renders connection list
- [ ] Test add connection wizard flow
- [ ] Test connection test button triggers validation
- [ ] Test API GET `/sirh/sync/status` returns correct data
- [ ] Test API GET `/sirh/sync/conflicts` returns unresolved conflicts
- [ ] Test API PUT `/sirh/sync/conflicts/{id}/resolve` updates conflict resolution

## Acceptance Criteria
- Sync dashboard displays full sync history with all relevant columns
- Conflict resolution queue shows unresolved conflicts with actionable buttons
- Resolving a conflict updates the SyncConflict record and removes it from the queue
- Error details are expandable per sync log entry
- Sync status auto-refreshes without manual page reload
- Connections page lists all SIRH connections with status
- Add connection wizard guides through provider selection, credentials, and frequency
- Test connection button validates credentials and reports success or failure

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
