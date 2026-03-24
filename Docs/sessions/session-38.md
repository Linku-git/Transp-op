# Session 38 — DAF Export (ERP Format)

## Phase: 2 — Financial Module
## Prerequisites: [[sessions/session-32|Session 32]], [[sessions/session-33|Session 33]]
## Complexity: Medium
> Previous: [[sessions/session-37|Session 37]] | Next: [[sessions/session-39|Session 39]]

## Objective
Build the DAF (Direction Administrative et Financiere) export engine generating ERP-compatible financial reports in multiple formats (CSV, XML, PDF, Excel) targeting SAP FI, Sage, and Cegid systems.

---

## Tasks

- [ ] Create `backend/app/services/daf_export.py` — DAF export engine:
  - Generate ERP-compatible CSV with standard accounting columns (account code, label, debit, credit, date, journal)
  - Generate XML export following standard accounting interchange format
  - Configurable target ERP: SAP FI, Sage, Cegid — each with specific column mapping and format rules
  - Include TCO summary, ROI summary, and investment comparison data
- [ ] Create POST `/financial/export/daf` endpoint in `backend/app/api/v1/financial.py`:
  - Accepts scenario ID, target ERP format, output format (CSV, XML)
  - Returns generated file as download
- [ ] Create POST `/export/financial/tco` endpoint:
  - Generate TCO report as PDF (using reportlab or weasyprint) or Excel (using openpyxl)
  - Include TCO breakdown, motorization comparison, evolution chart data
  - Formatted for DAF presentation
- [ ] Create POST `/export/financial/roi` endpoint:
  - Generate ROI report as PDF or Excel
  - Include ROI levers breakdown, payback period, total ROI percentage
  - Formatted for DAF presentation
- [ ] Implement ERP format templates:
  - SAP FI: BKPF/BSEG structure, document type, posting key
  - Sage: journal code, account number, piece reference
  - Cegid: standard Cegid import format with section analytique
- [ ] Create `backend/tests/test_daf_export.py`

## Files to Create/Modify
- `backend/app/services/daf_export.py` (create)
- `backend/app/api/v1/financial.py` (modify)
- `backend/app/schemas/financial.py` (modify)
- `backend/tests/test_daf_export.py` (create)

## Tests
- [ ] `test_daf_export_csv_structure` — CSV has correct accounting columns
- [ ] `test_daf_export_xml_structure` — XML follows valid accounting interchange schema
- [ ] `test_daf_export_sap_format` — SAP FI format has BKPF/BSEG structure
- [ ] `test_daf_export_sage_format` — Sage format has correct journal/account structure
- [ ] `test_daf_export_cegid_format` — Cegid format has section analytique
- [ ] `test_tco_report_pdf` — TCO PDF report generates with correct sections
- [ ] `test_tco_report_excel` — TCO Excel report has correct sheets and data
- [ ] `test_roi_report_pdf` — ROI PDF report generates with lever breakdown
- [ ] `test_roi_report_excel` — ROI Excel report has correct sheets and data
- [ ] `test_export_endpoint_download` — Endpoints return file download responses

## Acceptance Criteria
- DAF export generates valid CSV and XML files for ERP import
- SAP FI, Sage, and Cegid formats follow their respective conventions
- TCO and ROI reports generate as both PDF and Excel
- Reports include all relevant financial data (TCO breakdown, ROI levers, comparisons)
- Generated files are downloadable via API endpoints
- All 10 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
