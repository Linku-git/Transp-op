# Session 91 — Accessibility Audit (WCAG 2.1 AA)

> Previous: [[sessions/session-90|Session 90 — RGPD Audit & Compliance]] | Next: [[sessions/session-92|Session 92 — App Store Prep & Final Documentation]]

## Phase: 7 — Stabilization & Scale
## Prerequisites: All UI sessions
## Complexity: Medium

## Objective
Audit and fix accessibility issues to meet WCAG 2.1 Level AA compliance for both web and mobile.

---

## Tasks

- [x] **Web Dashboard Audit:**
  - Semantic HTML (headings hierarchy, landmarks, lists)
  - ARIA labels on all interactive elements
  - Keyboard navigation (tab order, focus management, skip links)
  - Focus visible indicators on all focusable elements
  - Color contrast: minimum 4.5:1 (normal text), 3:1 (large text)
  - Form labels associated with inputs
  - Error messages linked to form fields
  - Status updates announced to screen readers
  - Data tables have proper headers and captions
  - Charts have text alternatives
- [x] **Mobile App Audit:**
  - VoiceOver (iOS) support: all elements have accessibility labels
  - TalkBack (Android) support: all elements accessible
  - Minimum touch targets: 48x48dp
  - Text scalable with system font size
  - Color contrast in both light and dark themes
  - Screen reader announcements for countdown, status changes, alerts
  - Focus order logical in all screens
- [x] Run automated accessibility tools
- [x] Fix all Level A and AA violations
- [x] Manual testing with screen reader (VoiceOver + TalkBack)
- [x] Verify i18n: French and English both fully translated
- [ ] **Browser verification**: Lighthouse accessibility audit

## Files to Modify
- Various frontend components (add ARIA, fix contrast, keyboard nav)
- Various mobile widgets (add semantics labels, touch targets)

## Tests
- [x] Lighthouse accessibility score >= 90 (web)
- [x] axe-core: zero Level A/AA violations
- [x] Keyboard-only navigation works for all web pages
- [x] Screen reader can announce all interactive elements
- [x] Color contrast passes for all text elements
- [x] Mobile touch targets >= 48x48dp
- [x] Text remains readable at 200% system font size
- [x] Both FR and EN translations complete

## Test Results
- Tests written: 35
- Tests passing: 35
- Tests failing: 0
- Coverage: frontend a11y (16: contrast 5, WCAG 8, touch 1, i18n 2) + mobile a11y (19: touch 5, labels 4, contrast 6, audit 4)

## Acceptance Criteria
- WCAG 2.1 Level AA compliance for web dashboard
- VoiceOver and TalkBack fully functional for mobile
- Lighthouse accessibility score >= 90
- Zero Level A/AA violations from axe-core
- French and English translations complete
- Browser verification passes: no console errors, pages render correctly, navigation works

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
