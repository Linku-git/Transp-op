# Session 65 — Mobile Night Mode & Emergency

> Previous: [[sessions/session-64|Session 64 — Security Dashboard Frontend]] | Next: [[sessions/session-66|Session 66 — Emergency Alert System]]

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-45|Session 45]], [[sessions/session-61|Session 61]] completed
## Complexity: Medium

## Objective
Implement mobile night mode with automatic activation, dark theme, and battery optimization, along with a full-screen emergency overlay for immediate alert triggering, location sharing, and emergency service contact.

---

## Tasks
- [ ] Implement night mode:
  - Auto-activate based on configurable time window (default: 20h00-6h30) or manual toggle
  - Dark theme with `#1a1a2e` background and high-contrast text/elements
  - Reduced animations for battery optimization
  - Battery optimization: reduce GPS polling frequency, minimize background tasks
  - Emergency button always visible in night mode (fixed position, prominent styling)
- [ ] Create `EmergencyScreen` (full-screen overlay):
  - Full screen red overlay (`#dc2626` background) for maximum visibility
  - Active GPS location sharing — send current coordinates to server
  - "Sending alert to..." list showing notified responders
  - "Call Emergency Services" button with direct dial capability
  - Cancel button with confirmation dialog ("Are you sure you want to cancel?")
  - Haptic feedback on activation
- [ ] Create `SecurityQuestionnaireScreen`:
  - Reuse onboarding step 3 questionnaire component
  - Accessible from security section of the app
  - Pre-fill with previous responses when available
  - Submit updates to POST /security/questionnaire endpoint
- [ ] Implement night mode detection service:
  - Check current time against configured night hours
  - Listen for manual toggle changes
  - Persist user preference (auto vs manual)

## Files to Create/Modify
- `mobile/src/screens/EmergencyScreen.tsx`
- `mobile/src/screens/SecurityQuestionnaireScreen.tsx`
- `mobile/src/themes/nightMode.ts`
- `mobile/src/services/nightModeService.ts`
- `mobile/src/components/EmergencyButton.tsx`
- `mobile/src/components/NightModeToggle.tsx`
- `mobile/src/hooks/useNightMode.ts`
- `mobile/src/navigation/routes.tsx` (add new screens)

## Tests
- [ ] Test night mode auto-activates at configured time
- [ ] Test night mode manual toggle works correctly
- [ ] Test dark theme applies correct background color (#1a1a2e)
- [ ] Test emergency button is always visible in night mode
- [ ] Test emergency screen displays red overlay
- [ ] Test emergency flow sends location to server
- [ ] Test "Sending alert to..." list populates with responders
- [ ] Test cancel requires confirmation dialog
- [ ] Test security questionnaire pre-fills with previous responses
- [ ] Test location sharing activates GPS on emergency trigger

## Acceptance Criteria
- Night mode activates automatically based on time or via manual toggle
- Dark theme uses #1a1a2e background with high contrast and reduced animations
- Emergency button is always visible and accessible in night mode
- Emergency screen shows full red overlay with location sharing and responder list
- Direct dial to emergency services is available from emergency screen
- Cancel requires explicit confirmation to prevent accidental dismissal
- Security questionnaire screen reuses onboarding component and submits via API
- All tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
