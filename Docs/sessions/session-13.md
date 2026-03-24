# Session 13 — Excel Import Engine

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-06|Session 06]], [[sessions/session-09|Session 09]], [[sessions/session-12|Session 12]]

> Previous: [[sessions/session-12|Session 12]] | Next: [[sessions/session-14|Session 14]]

## Complexity: High

## Objective
Build the multi-sheet Excel import engine that parses the 6-sheet template, validates data, and imports into the database.

---

## Tasks

- [ ] Create `backend/app/services/excel_parser.py` — Main Excel import service:
  - Parse XLSX file using openpyxl
  - Detect and validate sheet names (SITES, EFFECTIF, USAGES & MODES, CONTRAINTES, PARC EXISTANT, ABSENCES)
  - Handle header row offsets (rows 2-3 per template spec)
  - Map columns to model fields per sheet
- [ ] Implement SITES sheet parser — validates and creates/updates Site records
- [ ] Implement EFFECTIF sheet parser — validates and creates/updates Employee records
  - Handle GPS coordinates from Google Maps format
  - Queue geocoding for missing lat/lng
  - Validate site code references exist
- [ ] Implement USAGES & MODES sheet parser — links modal data to employees by matricule
- [ ] Implement CONTRAINTES sheet parser — imports constraint key-value pairs
- [ ] Implement PARC EXISTANT sheet parser — imports vehicle fleet data
- [ ] Implement ABSENCES sheet parser — imports leave periods
- [ ] Create validation engine:
  - Required field checking (columns marked `*`)
  - Data type validation (numbers, dates, GPS, enums)
  - Foreign key validation (site codes, matricules)
  - Return per-row, per-column error list
- [ ] Create `backend/app/api/v1/excel_import.py` — Endpoints:
  - POST `/import/excel` — Upload and import full template
  - POST `/import/excel/preview` — Preview without importing (return parsed + validation results)
  - POST `/import/excel/sheet` — Import single sheet
- [ ] Support incremental import (update existing by code/matricule, add new)
- [ ] Create `backend/tests/test_excel_import.py`
- [ ] Create test Excel fixture file (`backend/tests/fixtures/test_template.xlsx`)

## Files to Create/Modify
- `backend/app/services/excel_parser.py` (create)
- `backend/app/api/v1/excel_import.py` (create)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_excel_import.py` (create)
- `backend/tests/fixtures/test_template.xlsx` (create)

## Tests
- [ ] `test_parse_valid_template` — All 6 sheets parsed correctly
- [ ] `test_parse_sites_sheet` — Creates site records
- [ ] `test_parse_effectif_sheet` — Creates employee records with site FK
- [ ] `test_parse_usages_sheet` — Links modal data to employees
- [ ] `test_parse_contraintes_sheet` — Creates constraint records
- [ ] `test_parse_parc_sheet` — Creates vehicle records
- [ ] `test_parse_absences_sheet` — Creates leave records
- [ ] `test_validation_required_fields` — Reports missing required fields
- [ ] `test_validation_invalid_data_types` — Reports type errors
- [ ] `test_validation_invalid_site_ref` — Reports unknown site codes
- [ ] `test_preview_mode` — Returns data without importing
- [ ] `test_incremental_import` — Updates existing, adds new
- [ ] `test_single_sheet_import` — Imports just one sheet

## Acceptance Criteria
- Full Excel template imports all 6 sheets correctly
- Validation reports specific row/column errors
- Preview mode shows data without database changes
- Incremental import updates existing records by code/matricule
- All 13 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
