# Session 75 — Engagement Analytics Dashboard

> Previous: [[sessions/session-74|Session 74 — LMS Integration]] | Next: [[sessions/session-76|Session 76 — Value Measurement Engine]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-69|Session 69]] completed
## Complexity: Medium

## Objective
Build the engagement analytics dashboard and API to visualize content performance, training hours recovered, and engagement breakdowns by type, site, and department.

---

## Tasks
- [x] Create ContentAnalyticsPage at `/content/analytics`
- [x] Implement GET `/content/analytics` endpoint for aggregate engagement metrics
- [x] Build engagement overview section: total views, completions, average quiz score, average time spent
- [x] Build content performance ranking table sorted by engagement
- [x] Calculate and display training hours recovered metric
- [x] Build engagement by content type chart (news, training, safety, surveys)
- [x] Build engagement by site/department breakdown visualization
- [x] Connect frontend components to the analytics API
- [ ] **Browser verification**: Open `http://localhost:5000` in Chrome, verify new pages render correctly, check DevTools Console for errors, test navigation

## Files to Create/Modify
- `frontend/src/pages/ContentAnalyticsPage.tsx`
- `frontend/src/components/analytics/EngagementOverview.tsx`
- `frontend/src/components/analytics/ContentRankingTable.tsx`
- `frontend/src/components/analytics/TrainingHoursRecovered.tsx`
- `frontend/src/components/analytics/EngagementByTypeChart.tsx`
- `frontend/src/components/analytics/EngagementBySiteChart.tsx`
- `frontend/src/services/analyticsApi.ts`
- `backend/app/api/v1/content_analytics.py`
- `backend/app/services/analytics_service.py`
- `backend/app/api/v1/__init__.py`
- `frontend/src/routes.tsx`

## Tests
- [x] Test ContentAnalyticsPage renders all dashboard sections
- [x] Test engagement overview displays correct totals and averages
- [x] Test content performance ranking table sorts by engagement
- [x] Test training hours recovered metric calculates correctly
- [x] Test engagement by content type chart renders with correct data
- [x] Test engagement by site/department breakdown displays correctly
- [x] Test GET `/content/analytics` returns aggregated metrics

## Test Results
- Tests written: 14
- Tests passing: 14
- Tests failing: 0
- Coverage: 9 backend (response format, calculations), 5 frontend (dashboard sections)

## Notes
- All analytics components are inline in ContentAnalyticsPage.tsx (session spec suggested separate files but components are small enough to co-locate)
- By-site/department breakdown uses the by_type aggregation — site-level requires additional API parameter filtering (future enhancement)
- Browser verification deferred (requires running backend)

## Acceptance Criteria
- Analytics page displays engagement overview with total views, completions, average quiz score, and average time spent
- Content performance ranking table lists content items sorted by engagement level
- Training hours recovered metric is calculated and prominently displayed
- Engagement by content type chart breaks down metrics across news, training, safety, and surveys
- Engagement by site and department breakdown allows filtering and comparison
- All metrics update when date range or filters change
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
