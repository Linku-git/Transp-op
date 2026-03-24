# Session 48 — Home Screen

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-47|Session 47]]
## Complexity: Medium
> Previous: [[sessions/session-47|Session 47]] | Next: [[sessions/session-49|Session 49]]

## Objective
Build the main Home Screen with a prominent next departure card featuring a color-coded countdown, quick action shortcuts, a content carousel, and night mode emergency access.

---

## Tasks
- [ ] Create HomeScreen with top bar displaying greeting message and notification bell icon
- [ ] Create NextDepartureCard widget (large, prominent) showing: departure time, countdown timer, pickup point, vehicle info, and "View on Map" button
- [ ] Implement color-coded countdown: Green (>5 minutes), Orange (2-5 minutes), Red (<2 minutes)
- [ ] Create QuickActionsRow widget with buttons: Book Trip, View Map, My Trips
- [ ] Create ContentCarousel widget with horizontal scroll displaying latest 5 content items
- [ ] Implement night mode behavior: emergency button visible during night hours
- [ ] Integrate with data providers for real-time updates

## Files to Create/Modify
- `mobile/lib/screens/home_screen.dart`
- `mobile/lib/widgets/next_departure_card.dart`
- `mobile/lib/widgets/quick_actions_row.dart`
- `mobile/lib/widgets/content_carousel.dart`
- `mobile/lib/widgets/emergency_button.dart`
- `mobile/lib/providers/home_provider.dart`
- `mobile/lib/services/departure_service.dart`
- `mobile/lib/utils/night_mode_helper.dart`

## Tests
- [ ] HomeScreen renders correctly with mock data
- [ ] NextDepartureCard displays all required fields
- [ ] Countdown timer updates every second
- [ ] Countdown color changes at correct thresholds (green/orange/red)
- [ ] QuickActionsRow buttons navigate to correct screens
- [ ] ContentCarousel scrolls horizontally and displays up to 5 items
- [ ] Night mode shows emergency button during night hours
- [ ] Emergency button is hidden during daytime hours

## Acceptance Criteria
- Home screen loads and displays personalized greeting with user name
- Notification bell icon shows unread count badge
- Next departure card is the most prominent element on screen
- Countdown timer is accurate and updates in real time
- Color transitions are smooth: green > orange > red as departure approaches
- Quick actions navigate to Book Trip, View Map, and My Trips screens
- Content carousel fetches and displays the latest 5 content items
- Emergency button appears automatically during configured night hours
- Screen handles empty state gracefully (no upcoming trips)

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
