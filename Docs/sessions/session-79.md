# Session 79 — Workday Connector

> Previous: [[sessions/session-78|Session 78 — SAP SuccessFactors Connector]] | Next: [[sessions/session-80|Session 80 — Talentsoft & Sage Connectors]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-77|Session 77]] completed
## Complexity: High

## Objective
Implement a dedicated connector for Workday that handles OAuth 2.0 authentication, employee data synchronization (employees, positions, schedules), field mapping from Workday data structures to the Transpop Employee model, and proper handling of Workday-specific data formats.

---

## Tasks
- [x] Create `backend/app/services/sirh/workday_connector.py` with Workday connector class
- [x] Implement OAuth 2.0 authentication flow with Workday
- [x] Implement token refresh and session management
- [x] Build employee data sync: fetch employees, positions, and schedules from Workday
- [x] Implement delta update logic: query Workday for records modified since last sync
- [x] Create field mapping layer: map Workday fields to Transpop Employee model fields
- [x] Handle Workday-specific data formats (XML/SOAP responses, WID references, effective-dated records)
- [x] Implement pagination for large Workday result sets
- [x] Log all sync operations to SyncLog
- [x] Detect and record conflicts in SyncConflict when values differ

## Files to Create/Modify
- `backend/app/services/sirh/workday_connector.py`
- `backend/app/services/sirh/workday_field_mapping.py`
- `backend/app/core/config.py` (add Workday-related settings)
- `backend/tests/services/sirh/test_workday_connector.py`

## Tests
- [x] Test OAuth 2.0 authentication flow with mocked Workday API
- [x] Test token refresh when token expires
- [x] Test employee data mapping from Workday format to Transpop Employee model
- [x] Test position data mapping
- [x] Test schedule data mapping
- [x] Test handling of Workday-specific data formats (effective-dated records, WID references)
- [x] Test delta sync only fetches records modified since last sync
- [x] Test pagination handling for large datasets
- [x] Test full sync cycle end-to-end with mocked Workday API

## Test Results
- Tests written: 40
- Tests passing: 40
- Tests failing: 0
- Coverage: auth (4), field mapping (6), WID refs (5), effective dating (4), employee mapping (8), position/schedule (2), data sync (6), pagination/retry (5)

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
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
