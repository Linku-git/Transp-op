# Session 70 — Mobile Content Feed

> Previous: [[sessions/session-69|Session 69 — Content Delivery & Engagement Tracking]] | Next: [[sessions/session-71|Session 71 — Mobile Micro-Training Player]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-45|Session 45]], [[sessions/session-69|Session 69]] completed
## Complexity: Medium

## Objective
Build the mobile content feed and detail screens enabling employees to browse, filter, and consume content during their commute.

---

## Tasks
- [x] Create ContentFeedScreen with tabs: All, News, Training, Safety, Surveys
- [x] Implement card list with title, snippet, type badge, date, media thumbnail, completion indicator, and "New" badge
- [x] Add pull-to-refresh functionality
- [x] Add offline indicator for cached content
- [x] Create ContentDetailScreen with full article view, rich text rendering, image gallery, and video support
- [x] Implement "Mark as Read" auto-trigger on scroll completion
- [x] Cache content locally for offline access

## Files to Create/Modify
- `mobile/src/screens/ContentFeedScreen.tsx`
- `mobile/src/screens/ContentDetailScreen.tsx`
- `mobile/src/components/content/ContentCard.tsx`
- `mobile/src/components/content/ContentTabs.tsx`
- `mobile/src/components/content/OfflineIndicator.tsx`
- `mobile/src/services/contentFeedService.ts`
- `mobile/src/hooks/useContentFeed.ts`
- `mobile/src/navigation/routes.ts`

## Tests
- [x] Test ContentFeedScreen renders card list with all required fields
- [x] Test tab filtering switches between content types correctly
- [x] Test pull-to-refresh triggers data reload
- [x] Test offline indicator displays when cached content is shown
- [x] Test ContentDetailScreen renders full article with rich text and media
- [x] Test "Mark as Read" triggers on scroll completion

## Test Results
- Tests written: 27
- Tests passing: 27
- Tests failing: 0
- Coverage: model (8), widgets (12), screens (7)

## Notes
- Session file listed `.tsx` paths but project is Flutter/Dart — created actual Dart files
- Used simple HTML-to-text rendering for MVP (strip tags + paragraph splitting), not a full HTML renderer
- ContentCard uses manual French date formatting to avoid intl locale initialization in tests
- Hive caching with 30-minute TTL for offline content feed

## Acceptance Criteria
- Content feed displays cards with title, snippet, type badge, date, media thumbnail, completion indicator, and "New" badge
- Tab navigation filters content by type (All, News, Training, Safety, Surveys)
- Pull-to-refresh reloads the feed from the API
- Offline indicator is visible when displaying cached content without network
- Content detail screen renders rich text, images, and video correctly
- Scrolling to the end of content automatically triggers "Mark as Read"

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
