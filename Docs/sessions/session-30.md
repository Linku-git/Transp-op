# Session 30 — Export Engine (PDF, Excel, CSV, GeoJSON)

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-23|Session 23]]

> Previous: [[sessions/session-29|Session 29]] | Next: [[sessions/session-31|Session 31]]

## Complexity: Medium

## Objective
Build the export engine generating PDF driver sheets, Excel workbooks, CSV stop orders, and GeoJSON route exports.

---

## Tasks

- [ ] Create `backend/app/services/export_engine.py` — Export service:
  - PDF driver sheets (per site, per route, with PMR indicators) — using reportlab or weasyprint
  - Excel cluster list (multi-sheet workbook, per-site sheets) — using openpyxl
  - CSV stop order (ordered stops with employee data, PMR flags)
  - GeoJSON route export (FeatureCollection with route polylines, stops, clusters)
- [ ] Create `backend/app/api/v1/exports.py` — Endpoints:
  - GET `/export/pdf` — Generate PDF driver sheets
  - GET `/export/excel` — Generate multi-sheet Excel
  - GET `/export/csv/stops` — CSV stop order
  - GET `/export/csv/employees` — CSV employee assignments
  - GET `/export/geojson` — GeoJSON FeatureCollection
- [ ] Implement file generation as Celery tasks for large exports
- [ ] Return file as streaming response or generate URL for download
- [ ] Register export router
- [ ] Create `backend/tests/test_exports.py`

## Files to Create/Modify
- `backend/app/services/export_engine.py` (create)
- `backend/app/api/v1/exports.py` (create)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_exports.py` (create)

## Tests
- [ ] `test_export_pdf` — Generates valid PDF file
- [ ] `test_export_excel` — Generates valid XLSX with correct sheets
- [ ] `test_export_csv_stops` — CSV has correct columns and data
- [ ] `test_export_csv_employees` — CSV has employee assignments
- [ ] `test_export_geojson` — Valid GeoJSON FeatureCollection
- [ ] `test_export_with_pmr_indicators` — PMR flags present in exports

## Acceptance Criteria
- All 5 export formats generate correctly
- PDF includes route maps and PMR indicators
- Excel has per-site sheets
- GeoJSON is valid and renderable
- Large exports handled asynchronously
- All 6 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
