# Session 50 — Trip Management

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-49|Session 49]]
## Complexity: Medium
> Previous: [[sessions/session-49|Session 49]] | Next: [[sessions/session-51|Session 51]]

## Objective
Build trip management screens for viewing, modifying, and cancelling trips, along with detailed trip views and historical trip data with statistics.

---

## Tasks
- [ ] Create TripsScreen with Upcoming and Past tabs
- [ ] Display upcoming trips as cards with modify and cancel buttons
- [ ] Implement trip modification: allow changing pickup point and shift (only if >30 minutes before departure)
- [ ] Implement trip cancellation with confirmation dialog
- [ ] Create TripDetailScreen showing full details, mini-map, status timeline, and CO2 badge
- [ ] Create TripHistoryScreen with monthly grouped list and stats header
- [ ] Integrate with APIs: PUT `/trips/{id}`, DELETE `/trips/{id}`, GET `/trips/my`, GET `/trips/upcoming`

## Files to Create/Modify
- `mobile/lib/screens/trips_screen.dart`
- `mobile/lib/screens/trip_detail_screen.dart`
- `mobile/lib/screens/trip_history_screen.dart`
- `mobile/lib/widgets/trip_card.dart`
- `mobile/lib/widgets/trip_status_timeline.dart`
- `mobile/lib/widgets/co2_badge.dart`
- `mobile/lib/widgets/trip_mini_map.dart`
- `mobile/lib/providers/trips_provider.dart`
- `mobile/lib/services/trip_service.dart`
- `mobile/lib/models/trip.dart`

## Tests
- [ ] Upcoming trips list renders correctly with mock data
- [ ] Past trips list renders correctly with mock data
- [ ] Cancel flow shows confirmation dialog and calls DELETE `/trips/{id}`
- [ ] Modify flow allows changing pickup and shift when >30 min before departure
- [ ] Modify is disabled when <30 min before departure
- [ ] TripDetailScreen displays all trip information
- [ ] TripHistoryScreen groups trips by month
- [ ] Stats header shows correct aggregated data

## Acceptance Criteria
- TripsScreen displays two tabs: Upcoming and Past
- Upcoming trip cards show essential info with modify and cancel actions
- Trip modification is only available more than 30 minutes before departure
- Trip cancellation requires confirmation before proceeding
- Cancelled trips are removed from the upcoming list
- TripDetailScreen shows trip details, a mini-map of the route, status timeline, and CO2 savings badge
- TripHistoryScreen groups past trips by month with a statistics summary header
- All API integrations (GET, PUT, DELETE) work correctly
- Empty states are handled for both tabs

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
- [[LOCAL_MOBILE_FUNCTIONALITY]]
- [[API_ENDPOINTS]]
