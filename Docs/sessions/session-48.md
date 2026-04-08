# Session 48 — Home Screen

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-47|Session 47]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-47|Session 47]] | Next: [[sessions/session-49|Session 49]]

## Objective
Build the main Home Screen with a prominent next departure card featuring a color-coded countdown, quick action shortcuts, a content carousel, and night mode emergency access.

---

## Tasks
- [x] Create HomeScreen with top bar displaying greeting message ("Bonjour/Bon après-midi/Bonsoir, {name}") and notification bell with unread count badge
- [x] Create NextDepartureCard widget showing: departure time, live countdown timer (updates every second), pickup point + walking time, vehicle type, route name, driver name, and "Voir sur la carte" button
- [x] Implement color-coded countdown: Green (>5 minutes), Orange (2-5 minutes), Red (<2 minutes), Red for "Parti"
- [x] Create QuickActionsRow widget with 3 card buttons: Réserver, Carte, Mes trajets — each navigating to correct route
- [x] Create ContentCarousel widget with horizontal ListView showing latest content items with type badges (Actualité, Formation, Sécurité, Sondage), unread dots, and tap navigation
- [x] Implement night mode behavior: EmergencyButton visible during night hours (20h-6h30) with red styling and emergency icon
- [x] Integrate with HomeNotifier (Riverpod) for data loading with pull-to-refresh, empty state for no upcoming trips

## Files Created
- `mobile/lib/models/departure.dart` — Departure model (id, departureTime, pickupPointName, walkingMinutes, vehicleType, routeName, driverName) + ContentItem model
- `mobile/lib/utils/night_mode_helper.dart` — NightModeHelper with configurable night hours (20h-6h30)
- `mobile/lib/services/departure_service.dart` — DepartureService (getNextDeparture, getLatestContent, getUnreadNotificationCount)
- `mobile/lib/providers/home_provider.dart` — HomeNotifier (StateNotifier) with parallel data loading
- `mobile/lib/widgets/next_departure_card.dart` — Live countdown with Timer.periodic, color-coded badge, detail rows
- `mobile/lib/widgets/quick_actions_row.dart` — 3 action cards (Réserver, Carte, Mes trajets)
- `mobile/lib/widgets/content_carousel.dart` — Horizontal scroll with type badges, unread indicators
- `mobile/lib/widgets/emergency_button.dart` — Red emergency button with URGENCE label
- `mobile/lib/screens/home/home_screen.dart` — Full home screen composing all widgets

## Files Modified
- `mobile/lib/config/routes.dart` — Replaced placeholder with real `HomeScreen`

## Tests
- Tests written: 29 (session 48)
- Tests passing: 112 (total across all sessions)
- Tests failing: 0

### Test files:
- `test/models/departure_test.dart` — Departure fromJson, hasDeparted, minutesRemaining; ContentItem fromJson with defaults
- `test/utils/night_mode_helper_test.dart` — 9 boundary tests (10pm, 11pm, 3am, 6:30am, 6:31am, noon, 3pm, 7:59pm, 8pm)
- `test/widgets/next_departure_card_test.dart` — All info displayed, map button visible/hidden, callback
- `test/widgets/quick_actions_row_test.dart` — 3 buttons render, callback fires
- `test/widgets/content_carousel_test.dart` — Items render, empty renders nothing, type badges, onItemTap
- `test/widgets/emergency_button_test.dart` — URGENCE label, icon, callback
- `test/providers/home_provider_test.dart` — Initial state, copyWith, clearDeparture

## Implementation Notes
- **Live countdown** uses `Timer.periodic(1 second)` with proper disposal in `dispose()`
- **Greeting** is time-aware: Bonjour (<12h), Bon après-midi (12-18h), Bonsoir (>=18h) with optional first name
- **Night mode** uses `NightModeHelper.isNightTime()` with injectable DateTime for testing
- **Parallel data loading** in HomeNotifier uses `Future.wait()` for concurrent API calls
- **Pull-to-refresh** via `RefreshIndicator` wrapping the main ListView
- **Empty state** shows "Aucun trajet prévu" when no next departure
- **Content type badges** with semantic colors: blue (news), purple (training), orange (safety), teal (survey)
- **Notification badge** shows count (caps at "9+") on bell icon

## Acceptance Criteria
- [x] Home screen loads and displays personalized greeting with user name
- [x] Notification bell icon shows unread count badge
- [x] Next departure card is the most prominent element on screen
- [x] Countdown timer updates in real time (every second)
- [x] Color transitions: green (>5min) > orange (2-5min) > red (<2min)
- [x] Quick actions navigate to Book Trip, View Map, and My Trips
- [x] Content carousel displays content items with type badges
- [x] Emergency button appears during configured night hours (20h-6h30)
- [x] Screen handles empty state gracefully (no upcoming trips)
- [x] `flutter analyze` reports 0 issues
- [x] All 112 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
