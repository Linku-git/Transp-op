# Session 85 — ERP Finance Export

> Previous: [[sessions/session-84|Session 84 — Operator Portal (Web)]] | Next: [[sessions/session-86|Session 86 — Payment & Transport Pass Integration]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-32|Session 32]], [[sessions/session-33|Session 33]] completed
## Complexity: Medium

## Objective
Implement financial data export functionality targeting major ERP systems used in France (SAP FI, Sage Comptabilite, Cegid), enabling DAF teams to import transport cost data directly into their accounting systems on-demand or via scheduled monthly push.

---

## Tasks
- [x] Create `backend/app/services/erp_export.py` with ERP export service
- [x] Implement SAP FI export format (specific CSV structure with SAP-compliant headers and fields)
- [x] Implement Sage Comptabilite export format
- [x] Implement Cegid export format
- [x] Create API endpoint POST `/financial/export/daf` with target_system parameter (sap_fi/sage/cegid)
- [x] Include export data: TCO reports, ROI analyses, cost-per-trip, investment comparator results
- [x] Implement on-demand export trigger via API
- [x] Implement scheduled monthly push (configurable per tenant)
- [x] Add export history tracking (who exported, when, which format, file reference)
- [x] Generate downloadable export files with appropriate content types

## Files to Create/Modify
- `backend/app/services/erp_export.py`
- `backend/app/services/erp_formats/sap_fi_formatter.py`
- `backend/app/services/erp_formats/sage_formatter.py`
- `backend/app/services/erp_formats/cegid_formatter.py`
- `backend/app/api/v1/financial_export.py`
- `backend/app/schemas/financial_export.py`
- `backend/app/models/export_history.py`
- `backend/app/tasks/scheduled_exports.py`

## Tests
- [x] Test SAP FI format generates correct CSV structure with proper headers
- [x] Test Sage Comptabilite format generates correct output
- [x] Test Cegid format generates correct output
- [x] Test export includes TCO report data
- [x] Test export includes ROI analysis data
- [x] Test export includes cost-per-trip data
- [x] Test export includes investment comparator results
- [x] Test data integrity: exported values match source financial data
- [x] Test API endpoint with each target_system parameter
- [x] Test scheduled monthly export task triggers correctly

## Test Results
- Tests written: 23
- Tests passing: 23
- Tests failing: 0
- Coverage: SAP FI (6), Sage (5), Cegid (3), service (6), schema (3)

## Acceptance Criteria
- SAP FI export produces valid CSV in SAP-compliant format
- Sage Comptabilite export produces valid output in Sage-compatible format
- Cegid export produces valid output in Cegid-compatible format
- All exports contain complete financial data: TCO, ROI, cost-per-trip, investment comparator
- On-demand export via API returns downloadable file
- Scheduled monthly push can be configured and runs automatically
- Export history is tracked for audit purposes
- Data integrity is maintained between source data and exported files

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
