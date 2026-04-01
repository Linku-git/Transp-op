# Session 14 — Excel Import Frontend

## Phase: 1 — MVP Core (Module B)
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-13|Session 13]]

> Previous: [[sessions/session-13|Session 13]] | Next: [[sessions/session-15|Session 15]]

## Complexity: Medium

## Objective
Build the Excel import frontend page with file upload, sheet preview, validation display, and import controls.

---

## Tasks

- [x] Create `frontend/src/api/import.ts` — API client (upload, preview, import sheet)
- [x] Create `frontend/src/pages/import/ExcelImportPage.tsx`:
  - File upload dropzone (accept .xlsx only)
  - Upload progress bar
  - After upload: tab navigation per detected sheet
  - Per sheet tab:
    - Preview data table (first 20 rows)
    - Validation results (errors highlighted in red, row/column reference)
    - "Import This Sheet" button
  - "Import All Valid" button
  - Summary: records to create, records to update, errors count
- [x] Create `frontend/src/components/ui/FileUpload.tsx` — Drag-and-drop file upload component
- [x] Create `frontend/src/components/import/SheetPreview.tsx` — Sheet data preview table
- [x] Create `frontend/src/components/import/ValidationErrors.tsx` — Error list with row/column
- [x] Create `frontend/src/components/ui/Tabs.tsx` — Tab navigation component
- [x] Create `frontend/src/components/ui/ProgressBar.tsx` — Upload/import progress
- [x] Add import route and Sidebar link
- [x] Handle large file upload (show progress, handle timeout)

## Files to Create/Modify
- `frontend/src/api/import.ts` (create)
- `frontend/src/pages/import/ExcelImportPage.tsx` (create)
- `frontend/src/components/ui/FileUpload.tsx` (create)
- `frontend/src/components/import/SheetPreview.tsx` (create)
- `frontend/src/components/import/ValidationErrors.tsx` (create)
- `frontend/src/components/ui/Tabs.tsx` (create)
- `frontend/src/components/ui/ProgressBar.tsx` (create)
- `frontend/src/routes.tsx` (modify)
- `frontend/src/components/layout/Sidebar.tsx` (modify)

## Tests
- [x] `ExcelImportPage.test.tsx` — Renders upload area, handles file
- [x] `FileUpload.test.tsx` — Drag-drop works, validates file type
- [x] `SheetPreview.test.tsx` — Renders data table
- [x] `ValidationErrors.test.tsx` — Displays errors with row references

## Acceptance Criteria
- File upload accepts .xlsx only, rejects other formats
- Preview shows parsed data per sheet
- Validation errors clearly show row and column
- Import per sheet or all at once
- Progress indicator during upload/import
- Success/error toast messages

## Test Results
- Tests written: 5 (ExcelImportPage, FileUpload, SheetPreview, ValidationErrors x2)
- Tests passing: 27 frontend (5 new + 22 prior)
- Tests failing: 0

## Notes
- SheetPreview shows stats summary since backend doesn't return raw row data in preview
- FileUpload uses ring-2 ring-dashed for drop zone (documented border exception)
- Tabs use h-0.5 bg-secondary indicator (documented border exception)
- Added import link to Sidebar navigation

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
