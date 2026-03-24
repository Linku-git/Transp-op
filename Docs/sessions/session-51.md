# Session 51 — RTI Display & Vehicle Tracking

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-48|Session 48]]
## Complexity: High
> Previous: [[sessions/session-50|Session 50]] | Next: [[sessions/session-52|Session 52]]

## Objective
Implement real-time vehicle tracking with live ETA countdowns, animated map displays, and WebSocket-based position updates to give employees accurate arrival information.

---

## Tasks
- [ ] Create RTITrackingScreen with vehicle arrival card showing ETA countdown in seconds
- [ ] Implement color-coded ETA: green (<=90s), orange (90-180s), red (>180s)
- [ ] Display vehicle type and driver name on the tracking card
- [ ] Create mini map showing: employee current location, gathering point, and approaching vehicle (animated)
- [ ] Draw dashed line from employee position to gathering point
- [ ] Draw solid line for vehicle route to gathering point
- [ ] Create FullMapScreen with full-screen Google Maps and vehicle position updated every <=10 seconds
- [ ] Establish WebSocket connection using socket_io_client for real-time vehicle positions
- [ ] Implement push alert trigger at D-2 minutes before arrival

## Files to Create/Modify
- `mobile/lib/screens/rti_tracking_screen.dart`
- `mobile/lib/screens/full_map_screen.dart`
- `mobile/lib/widgets/vehicle_arrival_card.dart`
- `mobile/lib/widgets/tracking_mini_map.dart`
- `mobile/lib/services/websocket_service.dart`
- `mobile/lib/services/vehicle_tracking_service.dart`
- `mobile/lib/providers/tracking_provider.dart`
- `mobile/lib/models/vehicle_position.dart`
- `mobile/lib/utils/map_utils.dart`

## Tests
- [ ] RTITrackingScreen renders with vehicle arrival card and mini map
- [ ] ETA countdown updates every second
- [ ] ETA color changes at correct thresholds (green/orange/red)
- [ ] WebSocket connection establishes and receives position updates
- [ ] Vehicle marker animates on map as position updates arrive
- [ ] Dashed line renders from employee to gathering point
- [ ] Solid line renders for vehicle route
- [ ] FullMapScreen displays vehicle position updated within 10 seconds
- [ ] D-2 minutes push alert triggers correctly

## Acceptance Criteria
- RTI screen shows real-time ETA countdown in seconds with color coding
- Vehicle type and driver name are displayed prominently
- Mini map shows employee location, gathering point, and vehicle with appropriate line styles
- Vehicle marker animates smoothly between position updates
- Full map screen provides expanded view with live tracking
- WebSocket connection maintains stable real-time communication
- Vehicle position refreshes at most every 10 seconds
- Push notification fires 2 minutes before vehicle arrival
- Screen handles connection loss gracefully with reconnection logic

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
