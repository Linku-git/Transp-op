# Session 50 — Trip Management

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-49|Session 49]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-49|Session 49]] | Next: [[sessions/session-51|Session 51]]

## Objective
Build trip management screens for viewing, modifying, and cancelling trips, along with detailed trip views and historical trip data with statistics.

---

## Tasks
- [x] Create TripsScreen with Upcoming ("À venir") and Past ("Passés") tabs
- [x] Display upcoming trips as TripCards with date, shift, pickup, route, status chip, CO2 badge, modify/cancel buttons
- [x] Implement trip cancellation with confirmation AlertDialog, removes trip from upcoming list
- [x] Trip modification only available >30 minutes before departure (canModify/canCancel logic)
- [x] Create TripDetailScreen with status timeline, detail card (date, shift, pickup, route, vehicle, distance, duration), CO2Badge, cancel button
- [x] Create TripHistoryScreen with stats header (total trips, CO2 saved, distance) and monthly grouped trip list
- [x] Integrate with APIs: GET /trips/upcoming, GET /trips/my, GET /trips/{id}, DELETE /trips/{id}, PUT /trips/{id}

## Files Created
- `mobile/lib/models/trip.dart` — Trip model (15 fields), TripStatus enum with French labels, TripStats aggregate
- `mobile/lib/providers/trips_provider.dart` — TripsNotifier with parallel load, cancelTrip, pastByMonth grouping, pastStats
- `mobile/lib/widgets/trip_card.dart` — Trip card with status chip, CO2 badge, conditional modify/cancel actions
- `mobile/lib/widgets/trip_status_timeline.dart` — 4-step visual timeline (Réservé → Confirmé → En cours → Terminé)
- `mobile/lib/widgets/co2_badge.dart` — Green badge showing CO2 kg saved with eco icon
- `mobile/lib/screens/trips/trips_screen.dart` — TabBar screen (À venir / Passés) with cancel dialog
- `mobile/lib/screens/trips/trip_detail_screen.dart` — Full detail with FutureProvider, timeline, details, CO2, cancel
- `mobile/lib/screens/trips/trip_history_screen.dart` — Stats header + monthly grouped trip list with French month names

## Files Modified
- `mobile/lib/services/trip_service.dart` — Added getUpcomingTrips, getPastTrips, getTripDetail, cancelTrip, modifyTrip
- `mobile/lib/config/routes.dart` — Replaced trip placeholders with real TripsScreen, TripDetailScreen, TripHistoryScreen
- `mobile/analysis_options.yaml` — Disabled use_null_aware_elements lint (Dart 3.10 feature, not stable)

## Tests
- Tests written: 21 (session 50)
- Tests passing: 163 (total)
- Tests failing: 0

### Test files:
- `test/models/trip_test.dart` — fromJson, canModify (>30min, <30min, completed), isUpcoming, TripStatus.fromString/labels, TripStats.fromTrips
- `test/widgets/trip_card_test.dart` — Renders info, CO2 badge, modify/cancel for modifiable, hides actions for completed
- `test/widgets/trip_status_timeline_test.dart` — 4 status labels, check icons for completed
- `test/widgets/co2_badge_test.dart` — Renders value and eco icon
- `test/providers/trips_provider_test.dart` — Initial state, pastStats, pastByMonth grouping, copyWith

## Acceptance Criteria
- [x] TripsScreen displays two tabs: À venir and Passés
- [x] Upcoming cards show info with modify/cancel (>30min only)
- [x] Cancellation requires confirmation dialog
- [x] Cancelled trips removed from upcoming list
- [x] TripDetailScreen shows timeline, details, CO2 badge, cancel
- [x] TripHistoryScreen groups by month with stats header
- [x] All API integrations (GET, PUT, DELETE) wired
- [x] Empty states for both tabs
- [x] `flutter analyze` reports 0 issues
- [x] All 163 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
