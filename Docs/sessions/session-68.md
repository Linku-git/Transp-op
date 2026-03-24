# Session 68 — Content Management Frontend

> Previous: [[sessions/session-67|Session 67 — Content Model & CRUD API]] | Next: [[sessions/session-69|Session 69 — Content Delivery & Engagement Tracking]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-67|Session 67]] completed
## Complexity: Medium

## Objective
Build the frontend content management interface allowing administrators to create, edit, list, and view content with audience targeting and engagement metrics.

---

## Tasks
- [ ] Create ContentListPage with table displaying title, type, status, published date, audience, and engagement
- [ ] Add filters for content type and status on the list page
- [ ] Create ContentCreatePage with title input, rich text editor for body, type selector, media upload, audience targeting (sites, departments, shifts), schedule fields (publish/expiry dates), and preview button
- [ ] Create ContentEditPage with pre-filled form from existing content data
- [ ] Create ContentDetailPage with read-only view and engagement metrics display
- [ ] Wire all pages to the Content CRUD API endpoints

## Files to Create/Modify
- `frontend/src/pages/ContentListPage.tsx`
- `frontend/src/pages/ContentCreatePage.tsx`
- `frontend/src/pages/ContentEditPage.tsx`
- `frontend/src/pages/ContentDetailPage.tsx`
- `frontend/src/components/content/ContentForm.tsx`
- `frontend/src/components/content/AudienceTargeting.tsx`
- `frontend/src/components/content/RichTextEditor.tsx`
- `frontend/src/services/contentApi.ts`
- `frontend/src/routes.tsx`

## Tests
- [ ] Test ContentCreatePage form rendering with all fields
- [ ] Test audience targeting UI (site, department, shift selectors)
- [ ] Test ContentEditPage loads and pre-fills data correctly
- [ ] Test ContentListPage renders table with filters
- [ ] Test ContentDetailPage displays read-only content and engagement metrics
- [ ] Test preview button functionality

## Acceptance Criteria
- ContentListPage displays all content items with correct columns and working filters
- ContentCreatePage renders all form fields including rich text editor and audience targeting
- ContentEditPage pre-fills all fields from existing content
- ContentDetailPage shows read-only content with engagement metrics
- Type and status filters correctly narrow the content list
- Media upload accepts and previews files before submission

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
