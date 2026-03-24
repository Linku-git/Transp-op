# Session 69 — Content Delivery & Engagement Tracking

> Previous: [[sessions/session-68|Session 68 — Content Management Frontend]] | Next: [[sessions/session-70|Session 70 — Mobile Content Feed]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-67|Session 67]] completed
## Complexity: Medium

## Objective
Create the content delivery and engagement tracking system to serve personalized content feeds and capture detailed engagement metrics per employee.

---

## Tasks
- [ ] Create ContentDelivery model with fields: content_id, employee_id, delivered_at, viewed_at, completed_at, quiz_score, time_spent_seconds
- [ ] Generate Alembic migration for the ContentDelivery table
- [ ] Implement GET `/content/feed` endpoint for personalized mobile feed (filter by employee's site, department, shift)
- [ ] Implement GET `/content/{id}/engagement` endpoint for engagement metrics per content item
- [ ] Track delivery events when content is served to an employee
- [ ] Track view events when content is opened
- [ ] Track completion events when content is fully consumed
- [ ] Track quiz scores and time spent per content item
- [ ] Implement metrics aggregation for engagement reporting

## Files to Create/Modify
- `backend/app/models/content_delivery.py`
- `backend/app/schemas/content_delivery.py`
- `backend/app/api/endpoints/content_feed.py`
- `backend/app/services/engagement_service.py`
- `backend/alembic/versions/xxx_create_content_delivery_table.py`
- `backend/app/api/router.py`

## Tests
- [ ] Test feed personalization returns only content matching employee's site, department, and shift
- [ ] Test engagement tracking records delivery, view, and completion events
- [ ] Test quiz score and time spent are persisted correctly
- [ ] Test metrics aggregation returns correct totals and averages
- [ ] Test feed excludes expired and unpublished content

## Acceptance Criteria
- ContentDelivery model persists all engagement fields correctly
- Personalized feed returns only content targeted at the requesting employee's site, department, and shift
- Engagement events (delivery, view, completion) are tracked with timestamps
- Quiz scores and time spent are recorded per content-employee pair
- Engagement metrics endpoint returns aggregated views, completions, average quiz score, and average time spent
- Expired and unpublished content is excluded from the feed

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
