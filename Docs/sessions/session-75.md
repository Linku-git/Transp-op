# Session 75 — Engagement Analytics Dashboard

> Previous: [[sessions/session-74|Session 74 — LMS Integration]] | Next: [[sessions/session-76|Session 76 — Value Measurement Engine]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-03|Session 03]], [[sessions/session-69|Session 69]] completed
## Complexity: Medium

## Objective
Build the engagement analytics dashboard and API to visualize content performance, training hours recovered, and engagement breakdowns by type, site, and department.

---

## Tasks
- [ ] Create ContentAnalyticsPage at `/content/analytics`
- [ ] Implement GET `/content/analytics` endpoint for aggregate engagement metrics
- [ ] Build engagement overview section: total views, completions, average quiz score, average time spent
- [ ] Build content performance ranking table sorted by engagement
- [ ] Calculate and display training hours recovered metric
- [ ] Build engagement by content type chart (news, training, safety, surveys)
- [ ] Build engagement by site/department breakdown visualization
- [ ] Connect frontend components to the analytics API

## Files to Create/Modify
- `frontend/src/pages/ContentAnalyticsPage.tsx`
- `frontend/src/components/analytics/EngagementOverview.tsx`
- `frontend/src/components/analytics/ContentRankingTable.tsx`
- `frontend/src/components/analytics/TrainingHoursRecovered.tsx`
- `frontend/src/components/analytics/EngagementByTypeChart.tsx`
- `frontend/src/components/analytics/EngagementBySiteChart.tsx`
- `frontend/src/services/analyticsApi.ts`
- `backend/app/api/endpoints/content_analytics.py`
- `backend/app/services/analytics_service.py`
- `backend/app/api/router.py`
- `frontend/src/routes.tsx`

## Tests
- [ ] Test ContentAnalyticsPage renders all dashboard sections
- [ ] Test engagement overview displays correct totals and averages
- [ ] Test content performance ranking table sorts by engagement
- [ ] Test training hours recovered metric calculates correctly
- [ ] Test engagement by content type chart renders with correct data
- [ ] Test engagement by site/department breakdown displays correctly
- [ ] Test GET `/content/analytics` returns aggregated metrics

## Acceptance Criteria
- Analytics page displays engagement overview with total views, completions, average quiz score, and average time spent
- Content performance ranking table lists content items sorted by engagement level
- Training hours recovered metric is calculated and prominently displayed
- Engagement by content type chart breaks down metrics across news, training, safety, and surveys
- Engagement by site and department breakdown allows filtering and comparison
- All metrics update when date range or filters change

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
