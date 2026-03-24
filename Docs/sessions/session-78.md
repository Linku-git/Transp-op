# Session 78 — SAP SuccessFactors Connector

> Previous: [[sessions/session-77|Session 77 — SIRH Connection Framework]] | Next: [[sessions/session-79|Session 79 — Workday Connector]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-77|Session 77]] completed
## Complexity: High

## Objective
Implement a dedicated connector for SAP SuccessFactors that handles OAuth 2.0 authentication, employee data synchronization, delta updates, and field mapping from SAP data structures to the Transpop Employee model, with robust error handling and retry logic.

---

## Tasks
- [ ] Create `backend/app/services/sirh/sap_connector.py` with SAP SuccessFactors connector class
- [ ] Implement OAuth 2.0 authentication flow with SAP (client credentials grant)
- [ ] Implement token refresh and session management
- [ ] Build employee data sync: fetch employees, sites, departments, and shifts from SAP
- [ ] Implement delta update logic: query SAP for records modified since last sync timestamp
- [ ] Create field mapping layer: map SAP SuccessFactors fields to Transpop Employee model fields
- [ ] Handle SAP-specific data formats (date formats, enums, nested objects)
- [ ] Implement error handling with retry logic: retry up to 3 times with exponential backoff
- [ ] Log all sync operations to SyncLog
- [ ] Detect and record conflicts in SyncConflict when values differ

## Files to Create/Modify
- `backend/app/services/sirh/sap_connector.py`
- `backend/app/services/sirh/sap_field_mapping.py`
- `backend/app/core/config.py` (add SAP-related settings)
- `backend/tests/services/sirh/test_sap_connector.py`

## Tests
- [ ] Test OAuth 2.0 authentication flow with mocked SAP API
- [ ] Test token refresh when token expires
- [ ] Test employee data mapping from SAP format to Transpop Employee model
- [ ] Test site and department mapping
- [ ] Test shift data mapping
- [ ] Test delta sync only fetches records modified since last sync
- [ ] Test retry logic with exponential backoff on transient failures
- [ ] Test error handling for invalid responses, timeouts, and rate limits
- [ ] Test full sync cycle end-to-end with mocked SAP API

## Acceptance Criteria
- SAP connector authenticates via OAuth 2.0 and manages token lifecycle
- Employee, site, department, and shift data sync correctly from SAP
- Delta updates only process records changed since the last sync
- Field mapping correctly translates all SAP fields to Transpop Employee model
- Failed API calls are retried up to 3 times with exponential backoff
- All errors are captured in SyncLog with detailed error information
- Conflicts between SAP and platform values are detected and stored

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
