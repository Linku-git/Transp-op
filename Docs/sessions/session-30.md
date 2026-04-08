# Session 30 — Export Engine (PDF, Excel, CSV, GeoJSON)

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-23|Session 23]]

> Previous: [[sessions/session-29|Session 29]] | Next: [[sessions/session-31|Session 31]]

## Complexity: Medium

## Objective
Build the export engine generating PDF driver sheets, Excel workbooks, CSV stop orders, and GeoJSON route exports.

---

## Tasks

- [x] Create `backend/app/services/export_engine.py` — Export service:
  - PDF driver sheets (per site, per route, with PMR indicators) — using reportlab
  - Excel cluster list (multi-sheet workbook, per-site sheets) — using openpyxl
  - CSV stop order (ordered stops with employee data, PMR flags)
  - GeoJSON route export (FeatureCollection with route polylines, stops, clusters)
- [x] Create `backend/app/api/v1/exports.py` — Endpoints:
  - GET `/export/pdf` — Generate PDF driver sheets
  - GET `/export/excel` — Generate multi-sheet Excel
  - GET `/export/csv/stops` — CSV stop order
  - GET `/export/csv/employees` — CSV employee assignments
  - GET `/export/geojson` — GeoJSON FeatureCollection
- [x] Implement file generation as Celery tasks for large exports
- [x] Return file as streaming response or generate URL for download
- [x] Register export router
- [x] Create `backend/tests/test_exports.py`

## Files to Create/Modify
- `backend/app/services/export_engine.py` (create)
- `backend/app/api/v1/exports.py` (create)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_exports.py` (create)

## Tests
- [x] `test_export_pdf` — Generates valid PDF file (2 tests)
- [x] `test_export_excel` — Generates valid XLSX with correct sheets (3 tests)
- [x] `test_export_csv_stops` — CSV has correct columns and data (3 tests)
- [x] `test_export_csv_employees` — CSV has employee assignments (2 tests)
- [x] `test_export_geojson` — Valid GeoJSON FeatureCollection (5 tests)
- [x] `test_export_with_pmr_indicators` — PMR flags present in exports (5 tests)
- [x] `test_decode_polyline` — Polyline decoder helper (2 tests)

## Test Results
- Tests written: 22
- Tests passing: 22
- Tests failing: 0

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
- [[PRD]] — Product Requirements Document v4.0
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
