# Session 47 — Onboarding Wizard

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-46|Session 46]]
## Complexity: Medium
> Previous: [[sessions/session-46|Session 46]] | Next: [[sessions/session-48|Session 48]]

## Objective
Create a 4-step onboarding wizard that collects transport preferences, security concerns, and required permissions from new users to personalize their experience.

---

## Tasks
- [ ] Create OnboardingFlow as a 4-step wizard using PageView
- [ ] Step 1: Welcome carousel with 3 informational slides
- [ ] Step 2: Transport preferences — mode selector, car toggle, volunteer driver option, walking distance slider, pickup point map picker
- [ ] Step 3: Security questionnaire — safety rating (1-5), vulnerable time slot selection, map pin for concern zones, night travel concerns
- [ ] Step 4: Permissions — request location (active-only) and notification permissions
- [ ] Save all collected preferences to backend API
- [ ] Add progress indicator and back/next navigation

## Files to Create/Modify
- `mobile/lib/screens/onboarding/onboarding_flow.dart`
- `mobile/lib/screens/onboarding/welcome_step.dart`
- `mobile/lib/screens/onboarding/transport_preferences_step.dart`
- `mobile/lib/screens/onboarding/security_questionnaire_step.dart`
- `mobile/lib/screens/onboarding/permissions_step.dart`
- `mobile/lib/models/transport_preferences.dart`
- `mobile/lib/models/security_preferences.dart`
- `mobile/lib/services/onboarding_service.dart`
- `mobile/lib/providers/onboarding_provider.dart`
- `mobile/lib/config/routes.dart`

## Tests
- [ ] Each step renders all expected form fields and controls
- [ ] Navigation between steps works (forward and backward)
- [ ] Step 2 transport preferences are captured correctly
- [ ] Step 3 security questionnaire data is captured correctly
- [ ] Step 4 triggers permission dialogs
- [ ] Data is submitted to backend API on completion
- [ ] Validation prevents advancing with incomplete required fields

## Acceptance Criteria
- Onboarding wizard displays after first login for new users
- All 4 steps are navigable via swipe and next/back buttons
- Welcome carousel auto-advances and supports manual swiping
- Transport preferences include all specified inputs (mode, car, volunteer, walking distance, map picker)
- Security questionnaire captures safety ratings, vulnerable times, concern zones, and night concerns
- Permissions step requests location and notification access
- All preferences are persisted to the backend on wizard completion
- Progress indicator reflects the current step

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
