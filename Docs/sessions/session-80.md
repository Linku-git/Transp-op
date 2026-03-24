# Session 80 — Talentsoft & Sage Connectors

> Previous: [[sessions/session-79|Session 79 — Workday Connector]] | Next: [[sessions/session-81|Session 81 — SIRH Sync Dashboard]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-77|Session 77]] completed
## Complexity: Medium

## Objective
Implement connectors for Talentsoft and Sage SIRH systems, both using API Key authentication. Talentsoft syncs employee and training records while Sage syncs employee and payroll data, each with appropriate rate limiting.

---

## Tasks
- [ ] Create `backend/app/services/sirh/talentsoft_connector.py` with Talentsoft connector class
- [ ] Create `backend/app/services/sirh/sage_connector.py` with Sage connector class
- [ ] Implement API Key authentication for Talentsoft
- [ ] Implement API Key authentication for Sage
- [ ] Build Talentsoft sync: fetch employees and training records
- [ ] Build Sage sync: fetch employees and payroll data
- [ ] Create field mapping for Talentsoft fields to Transpop Employee model
- [ ] Create field mapping for Sage fields to Transpop Employee model
- [ ] Implement rate limiting for Talentsoft: 1000 requests/hour
- [ ] Implement rate limiting for Sage: 500 requests/hour
- [ ] Implement delta update logic for both connectors
- [ ] Log all sync operations to SyncLog
- [ ] Detect and record conflicts in SyncConflict

## Files to Create/Modify
- `backend/app/services/sirh/talentsoft_connector.py`
- `backend/app/services/sirh/talentsoft_field_mapping.py`
- `backend/app/services/sirh/sage_connector.py`
- `backend/app/services/sirh/sage_field_mapping.py`
- `backend/app/core/config.py` (add Talentsoft and Sage settings)
- `backend/tests/services/sirh/test_talentsoft_connector.py`
- `backend/tests/services/sirh/test_sage_connector.py`

## Tests
- [ ] Test Talentsoft API Key authentication with mocked API
- [ ] Test Sage API Key authentication with mocked API
- [ ] Test Talentsoft employee data sync and field mapping
- [ ] Test Talentsoft training records sync
- [ ] Test Sage employee data sync and field mapping
- [ ] Test Sage payroll data sync
- [ ] Test Talentsoft rate limiting enforces 1000 requests/hour
- [ ] Test Sage rate limiting enforces 500 requests/hour
- [ ] Test delta sync for both connectors
- [ ] Test error handling for both connectors

## Acceptance Criteria
- Talentsoft connector authenticates via API Key and syncs employee and training data
- Sage connector authenticates via API Key and syncs employee and payroll data
- Rate limiting is enforced: 1000/hour for Talentsoft, 500/hour for Sage
- Field mappings correctly translate both providers' fields to Transpop Employee model
- Delta updates work for both connectors
- All sync operations are logged and conflicts are detected

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
