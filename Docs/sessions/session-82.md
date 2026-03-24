# Session 82 — Operator Sizing Plan Export

> Previous: [[sessions/session-81|Session 81 — SIRH Sync Dashboard]] | Next: [[sessions/session-83|Session 83 — Via & SWVL API Integration]]

## Phase: 6 — Enterprise Integrations
## Prerequisites: [[sessions/session-23|Session 23]] completed
## Complexity: Medium

## Objective
Create the data models and export functionality for generating standardized sizing plans that can be shared with transport operators. Support multiple export formats (JSON, XML, PDF) with versioning and change tracking.

---

## Tasks
- [ ] Create Operator model with fields: tenant_id, name, type (enum: via/swvl/local/internal), api_config (JSON), contacts (JSON)
- [ ] Create SizingPlanExport model with fields: optimization_id, operator_id, format (enum: json/xml/pdf), file_url, status, version
- [ ] Create Alembic migration for Operator table
- [ ] Create Alembic migration for SizingPlanExport table
- [ ] Create API endpoint POST `/export/sizing-plan` to generate a sizing plan export
- [ ] Implement JSON export format with full sizing plan data
- [ ] Implement XML export format with standardized schema
- [ ] Implement PDF export format with formatted report layout
- [ ] Include in export content: vehicle specifications, routes, schedules, passenger counts, PMR requirements, RTI targets
- [ ] Implement versioned exports with change tracking between versions
- [ ] Create API endpoints for operator CRUD (POST/GET/PUT/DELETE `/operators`)

## Files to Create/Modify
- `backend/app/models/operator.py`
- `backend/app/models/sizing_plan_export.py`
- `backend/alembic/versions/xxx_create_operator.py`
- `backend/alembic/versions/xxx_create_sizing_plan_export.py`
- `backend/app/services/export/sizing_plan_exporter.py`
- `backend/app/services/export/pdf_generator.py`
- `backend/app/api/routes/export.py`
- `backend/app/api/routes/operators.py`
- `backend/app/schemas/operator.py`
- `backend/app/schemas/sizing_plan_export.py`

## Tests
- [ ] Test Operator CRUD operations
- [ ] Test SizingPlanExport creation and status tracking
- [ ] Test JSON export generates valid JSON with all required content
- [ ] Test XML export generates valid XML with correct schema
- [ ] Test PDF export generates a valid PDF file
- [ ] Test export content includes vehicle specs, routes, schedules, passenger counts, PMR requirements, RTI targets
- [ ] Test versioned exports increment version number
- [ ] Test change tracking between export versions
- [ ] Test API endpoint POST `/export/sizing-plan` returns correct response

## Acceptance Criteria
- Operator model supports via, swvl, local, and internal operator types
- Sizing plan exports can be generated in JSON, XML, and PDF formats
- All exports contain complete data: vehicle specs, routes, schedules, passenger counts, PMR requirements, RTI targets
- Exports are versioned and changes between versions are tracked
- Export files are stored and accessible via file_url
- Operator CRUD endpoints work correctly

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
