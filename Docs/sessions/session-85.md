# Session 85 — ERP Finance Export

> Previous: [[sessions/session-84|Session 84 — Operator Portal (Web)]] | Next: [[sessions/session-86|Session 86 — Payment & Transport Pass Integration]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-32|Session 32]], [[sessions/session-33|Session 33]] completed
## Complexity: Medium

## Objective
Implement financial data export functionality targeting major ERP systems used in France (SAP FI, Sage Comptabilite, Cegid), enabling DAF teams to import transport cost data directly into their accounting systems on-demand or via scheduled monthly push.

---

## Tasks
- [ ] Create `backend/app/services/erp_export.py` with ERP export service
- [ ] Implement SAP FI export format (specific CSV structure with SAP-compliant headers and fields)
- [ ] Implement Sage Comptabilite export format
- [ ] Implement Cegid export format
- [ ] Create API endpoint POST `/financial/export/daf` with target_system parameter (sap_fi/sage/cegid)
- [ ] Include export data: TCO reports, ROI analyses, cost-per-trip, investment comparator results
- [ ] Implement on-demand export trigger via API
- [ ] Implement scheduled monthly push (configurable per tenant)
- [ ] Add export history tracking (who exported, when, which format, file reference)
- [ ] Generate downloadable export files with appropriate content types

## Files to Create/Modify
- `backend/app/services/erp_export.py`
- `backend/app/services/erp_formats/sap_fi_formatter.py`
- `backend/app/services/erp_formats/sage_formatter.py`
- `backend/app/services/erp_formats/cegid_formatter.py`
- `backend/app/api/routes/financial_export.py`
- `backend/app/schemas/financial_export.py`
- `backend/app/models/export_history.py`
- `backend/app/tasks/scheduled_exports.py`

## Tests
- [ ] Test SAP FI format generates correct CSV structure with proper headers
- [ ] Test Sage Comptabilite format generates correct output
- [ ] Test Cegid format generates correct output
- [ ] Test export includes TCO report data
- [ ] Test export includes ROI analysis data
- [ ] Test export includes cost-per-trip data
- [ ] Test export includes investment comparator results
- [ ] Test data integrity: exported values match source financial data
- [ ] Test API endpoint with each target_system parameter
- [ ] Test scheduled monthly export task triggers correctly

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
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
