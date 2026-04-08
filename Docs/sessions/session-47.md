# Session 47 — Onboarding Wizard

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-46|Session 46]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-46|Session 46]] | Next: [[sessions/session-48|Session 48]]

## Objective
Create a 4-step onboarding wizard that collects transport preferences, security concerns, and required permissions from new users to personalize their experience.

---

## Backend API
All API calls use `dio` with base URL from `lib/config/api_config.dart`.
Full path format: `/api/v1/...` (e.g. `PATCH /api/v1/employees/me/preferences`).
Error handling: backend returns Pydantic v2 errors — `detail` may be a string or `[{type, loc, msg}]` array.

## Tasks
- [x] Create OnboardingFlow as a 4-step wizard using PageView
- [x] Step 1: Welcome carousel with 3 informational slides (Transport optimisé, Suivi en temps réel, Impact positif)
- [x] Step 2: Transport preferences — mode selector (8 modes), car toggle, volunteer driver option, carpool seats slider, walking distance slider (200m-2km)
- [x] Step 3: Security questionnaire — safety rating (1-5 stars), vulnerable time slot selection (6 slots), night walking distance slider, night concerns text input
- [x] Step 4: Permissions — request location (active-only) and notification permissions with privacy note
- [x] Save all collected preferences to backend API via OnboardingService
- [x] Add progress indicator (4-segment bar) and back/next navigation with "Passer" skip option

## Files Created
- `mobile/lib/models/transport_preferences.dart` — TransportPreferences model + 8 TransportMode constants
- `mobile/lib/models/security_preferences.dart` — SecurityPreferences model + ConcernZone + 6 TimeSlot constants
- `mobile/lib/services/onboarding_service.dart` — API service (PATCH /employees/me/preferences)
- `mobile/lib/providers/onboarding_provider.dart` — OnboardingNotifier (StateNotifier) managing wizard state
- `mobile/lib/screens/onboarding/onboarding_flow.dart` — Main wizard flow with PageView, progress bar, navigation
- `mobile/lib/screens/onboarding/welcome_step.dart` — 3-slide carousel with auto-dot indicators
- `mobile/lib/screens/onboarding/transport_preferences_step.dart` — Transport mode chips, switch tiles, sliders
- `mobile/lib/screens/onboarding/security_questionnaire_step.dart` — Star rating, time slot chips, night distance slider, text input
- `mobile/lib/screens/onboarding/permissions_step.dart` — Permission cards with grant status, privacy note

## Files Modified
- `mobile/lib/config/routes.dart` — Replaced placeholder with real `OnboardingFlow` screen

## Tests
- Tests written: 33 (session 47)
- Tests passing: 83 (total across all sessions)
- Tests failing: 0

### Test files:
- `test/models/transport_preferences_test.dart` — Defaults, toJson, null pickup omission, pickup inclusion, 8 transport modes
- `test/models/security_preferences_test.dart` — Defaults, toJson, concern zone serialization, 6 time slots
- `test/providers/onboarding_provider_test.dart` — Initial state, totalSteps, isLastStep, canGoBack, copyWith
- `test/screens/onboarding_flow_test.dart` — Step 1 render, progress indicator, Suivant/Retour navigation, forward/back through all 4 steps, Passer button, Commencer on last step, transport mode chips, walking slider, switch toggles, safety stars, time slots, permission cards, privacy note

## Implementation Notes
- **4-step PageView** with `NeverScrollableScrollPhysics` (navigation via buttons only, not swipe) for consistent UX
- **Progress bar** uses animated segment bar (not dots) matching Material 3 style
- **"Passer" skip button** on all non-last steps to let users skip onboarding
- **Welcome carousel** has internal PageView with dot indicators and manual swiping
- **Transport mode selector** uses ChoiceChip (single select) with 8 predefined modes
- **Volunteer driver** and carpool seats only visible when `hasPrivateCar` is true (conditional rendering)
- **Safety rating** uses 5-star rating with amber icons and descriptive labels (Très insécure → Très sécure)
- **Time slots** use FilterChip (multi-select) with error color for vulnerability indication
- **Permission cards** show granted/pending state with check icons and "Autoriser" buttons
- **Privacy note** with info container explaining RGPD-compliant active-only geolocation
- **Map picker for concern zones** deferred to future session (requires google_maps_flutter setup)
- **Actual permission dialogs** (location/notifications) prepared in provider but trigger real OS dialogs only on device — in tests, mock the granted state

## Acceptance Criteria
- [x] Onboarding wizard displays as a 4-step flow
- [x] All 4 steps are navigable via next/back buttons
- [x] Welcome carousel has 3 slides with auto dot indicators
- [x] Transport preferences include mode selector, car, volunteer, walking distance
- [x] Security questionnaire captures safety ratings, vulnerable times, night concerns
- [x] Permissions step shows location and notification cards with privacy note
- [x] All preferences serialized correctly for backend API submission
- [x] Progress indicator reflects the current step
- [x] "Passer" option available to skip onboarding
- [x] `flutter analyze` reports 0 issues
- [x] All 83 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
