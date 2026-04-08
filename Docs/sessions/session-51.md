# Session 51 — RTI Display & Vehicle Tracking

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-48|Session 48]]
## Complexity: High
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-50|Session 50]] | Next: [[sessions/session-52|Session 52]]

## Objective
Implement real-time vehicle tracking with live ETA countdowns, map displays, and WebSocket-based position updates.

---

## Tasks
- [x] Create RTITrackingScreen with vehicle arrival card showing ETA countdown
- [x] Implement color-coded ETA: green (<=90s), orange (90-180s), red (>180s)
- [x] Display vehicle type, route name, driver name on tracking card
- [x] Create TrackingMiniMap with legend (Vous, Arrêt, Véhicule) and LIVE badge
- [x] Create FullMapScreen with expanded view, bottom ETA overlay, legend panel
- [x] WebSocket connection via socket_io_client with HTTP polling fallback (10s)
- [x] Connection status indicator (EN DIRECT / HORS LIGNE)
- [x] VehicleTrackingService for REST fallback
- [x] MapUtils for ETA color coding and formatting

## Files Created
- `mobile/lib/models/vehicle_position.dart` — VehiclePosition + TrackingInfo
- `mobile/lib/utils/map_utils.dart` — etaColor, formatEta, formatEtaShort
- `mobile/lib/services/websocket_service.dart` — Socket.IO client
- `mobile/lib/services/vehicle_tracking_service.dart` — REST fallback
- `mobile/lib/providers/tracking_provider.dart` — TrackingNotifier
- `mobile/lib/widgets/vehicle_arrival_card.dart` — Live countdown, color ETA
- `mobile/lib/widgets/tracking_mini_map.dart` — Map placeholder with legend
- `mobile/lib/screens/tracking/rti_tracking_screen.dart` — Main tracking screen
- `mobile/lib/screens/tracking/full_map_screen.dart` — Full-screen map

## Files Modified
- `mobile/lib/config/routes.dart` — Real RTITrackingScreen + FullMapScreen

## Tests
- Tests written: 28 (session 51)
- Tests passing: 191 (total)
- Tests failing: 0

## Acceptance Criteria
- [x] RTI screen shows real-time ETA countdown with color coding
- [x] Vehicle info displayed prominently
- [x] Mini map shows legend and LIVE badge
- [x] Full map with ETA overlay and legend
- [x] WebSocket + HTTP polling fallback
- [x] Connection status indicator
- [x] `flutter analyze` 0 issues, 191 tests pass
