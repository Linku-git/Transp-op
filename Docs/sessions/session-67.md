# Session 67 — Content Model & CRUD API

> Previous: [[sessions/session-66|Session 66 — Emergency Alert System]] | Next: [[sessions/session-68|Session 68 — Content Management Frontend]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-04|Session 04]] completed
## Complexity: Medium

## Objective
Create the Content model and full CRUD API to support news, training, safety, and survey content types with audience targeting capabilities.

---

## Tasks
- [ ] Create Content model with fields: title, body (rich text), content_type (news/training/safety/survey), media_url, target_sites (JSON), target_departments (JSON), target_shifts (JSON), published_at, expires_at, created_by, is_active
- [ ] Generate Alembic migration for the Content table
- [ ] Implement POST `/content` endpoint to create content
- [ ] Implement GET `/content` endpoint to list content with filtering
- [ ] Implement PUT `/content` endpoint to update content
- [ ] Implement DELETE `/content` endpoint to soft-delete content
- [ ] Implement POST `/content/{id}/publish` endpoint to publish/unpublish content
- [ ] Implement audience targeting logic to filter content by sites, departments, and shifts

## Files to Create/Modify
- `backend/app/models/content.py`
- `backend/app/schemas/content.py`
- `backend/app/api/endpoints/content.py`
- `backend/app/api/router.py`
- `backend/alembic/versions/xxx_create_content_table.py`
- `backend/app/services/content_service.py`

## Tests
- [ ] Test CRUD operations (create, read, update, delete)
- [ ] Test audience targeting logic (filter by sites, departments, shifts)
- [ ] Test publish/unpublish flow via POST `/content/{id}/publish`
- [ ] Test content listing with filters
- [ ] Test validation of content_type enum values

## Acceptance Criteria
- Content model persists all specified fields correctly
- Alembic migration runs without errors
- All CRUD endpoints return correct status codes and payloads
- Audience targeting filters content based on site, department, and shift criteria
- Publish endpoint toggles published_at and is_active appropriately
- Invalid content types are rejected with proper validation errors

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
