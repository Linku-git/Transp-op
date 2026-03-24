# Session 79 — Workday Connector

> Previous: [[sessions/session-78|Session 78 — SAP SuccessFactors Connector]] | Next: [[sessions/session-80|Session 80 — Talentsoft & Sage Connectors]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-77|Session 77]] completed
## Complexity: High

## Objective
Implement a dedicated connector for Workday that handles OAuth 2.0 authentication, employee data synchronization (employees, positions, schedules), field mapping from Workday data structures to the Transpop Employee model, and proper handling of Workday-specific data formats.

---

## Tasks
- [ ] Create `backend/app/services/sirh/workday_connector.py` with Workday connector class
- [ ] Implement OAuth 2.0 authentication flow with Workday
- [ ] Implement token refresh and session management
- [ ] Build employee data sync: fetch employees, positions, and schedules from Workday
- [ ] Implement delta update logic: query Workday for records modified since last sync
- [ ] Create field mapping layer: map Workday fields to Transpop Employee model fields
- [ ] Handle Workday-specific data formats (XML/SOAP responses, WID references, effective-dated records)
- [ ] Implement pagination for large Workday result sets
- [ ] Log all sync operations to SyncLog
- [ ] Detect and record conflicts in SyncConflict when values differ

## Files to Create/Modify
- `backend/app/services/sirh/workday_connector.py`
- `backend/app/services/sirh/workday_field_mapping.py`
- `backend/app/core/config.py` (add Workday-related settings)
- `backend/tests/services/sirh/test_workday_connector.py`

## Tests
- [ ] Test OAuth 2.0 authentication flow with mocked Workday API
- [ ] Test token refresh when token expires
- [ ] Test employee data mapping from Workday format to Transpop Employee model
- [ ] Test position data mapping
- [ ] Test schedule data mapping
- [ ] Test handling of Workday-specific data formats (effective-dated records, WID references)
- [ ] Test delta sync only fetches records modified since last sync
- [ ] Test pagination handling for large datasets
- [ ] Test full sync cycle end-to-end with mocked Workday API

## Acceptance Criteria
- Workday connector authenticates via OAuth 2.0 and manages token lifecycle
- Employee, position, and schedule data sync correctly from Workday
- Delta updates only process records changed since the last sync
- Field mapping correctly translates all Workday fields to Transpop Employee model
- Workday-specific formats (XML/SOAP, WID references, effective-dated records) are properly handled
- Large result sets are paginated correctly
- All errors are captured in SyncLog with detailed error information
- Conflicts between Workday and platform values are detected and stored

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
