# Session 65 — Mobile Night Mode & Emergency

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-45|Session 45]], [[sessions/session-61|Session 61]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08

## Tasks
- [x] Night mode: auto (20h-6h30) or manual toggle, timer-based re-evaluation
- [x] NightModeNotifier (Riverpod) with auto/manual/off preferences (persisted)
- [x] EmergencyScreen: full red overlay, GPS sharing, responder list, call button, cancel with confirmation
- [x] SecurityQuestionnaireScreen: safety rating, time slots, night distance, concerns (reuses onboarding models)
- [x] NightModeToggle widget for profile/preferences
- [x] Routes updated: /emergency → EmergencyScreen, /profile/security → SecurityQuestionnaireScreen

## Files Created (5)
- `mobile/lib/services/night_mode_service.dart`
- `mobile/lib/screens/emergency/emergency_screen.dart`
- `mobile/lib/screens/profile/security_questionnaire_screen.dart`
- `mobile/lib/widgets/night_mode_toggle.dart`
- Tests: `night_mode_service_test.dart`, `emergency_screen_test.dart`, `night_mode_toggle_test.dart`

## Tests
- Tests written: 5 | Tests passing: 268 mobile + 131 backend + 18 frontend = 417 total | Tests failing: 0
