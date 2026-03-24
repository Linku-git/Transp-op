# Session 83 — Via & SWVL API Integration

> Previous: [[sessions/session-82|Session 82 — Operator Sizing Plan Export]] | Next: [[sessions/session-84|Session 84 — Operator Portal (Web)]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-82|Session 82]] completed
## Complexity: Medium

## Objective
Implement API client integrations for Via Transportation and SWVL, enabling automated transmission of sizing plans and exchange of schedule, capacity, and route data with these external transport operators.

---

## Tasks
- [ ] Create `backend/app/services/operators/via_client.py` with Via Transportation API client
- [ ] Implement Via authentication and session management
- [ ] Implement sizing plan transmission in Via-compatible format
- [ ] Implement schedule and capacity data exchange with Via
- [ ] Create `backend/app/services/operators/swvl_client.py` with SWVL API client
- [ ] Implement SWVL authentication and session management
- [ ] Implement sizing plan transmission in SWVL-compatible format
- [ ] Implement route and capacity data exchange with SWVL
- [ ] Handle API response parsing and error handling for both providers
- [ ] Implement retry logic for transient failures

## Files to Create/Modify
- `backend/app/services/operators/via_client.py`
- `backend/app/services/operators/swvl_client.py`
- `backend/app/services/operators/base_operator_client.py`
- `backend/app/core/config.py` (add Via and SWVL settings)
- `backend/tests/services/operators/test_via_client.py`
- `backend/tests/services/operators/test_swvl_client.py`

## Tests
- [ ] Test Via API client authentication with mocked API
- [ ] Test Via sizing plan transmission formats correctly
- [ ] Test Via schedule data exchange
- [ ] Test Via capacity data exchange
- [ ] Test SWVL API client authentication with mocked API
- [ ] Test SWVL sizing plan transmission formats correctly
- [ ] Test SWVL route data exchange
- [ ] Test SWVL capacity data exchange
- [ ] Test data format validation for both providers
- [ ] Test error handling and retry logic for both clients

## Acceptance Criteria
- Via client authenticates and transmits sizing plans in Via-compatible format
- Via client exchanges schedule and capacity data correctly
- SWVL client authenticates and transmits sizing plans in SWVL-compatible format
- SWVL client exchanges route and capacity data correctly
- Both clients handle errors gracefully with appropriate retry logic
- Data format validation ensures compatibility before transmission

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
