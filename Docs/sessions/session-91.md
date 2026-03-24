# Session 91 — Accessibility Audit (WCAG 2.1 AA)

> Previous: [[sessions/session-90|Session 90 — RGPD Audit & Compliance]] | Next: [[sessions/session-92|Session 92 — App Store Prep & Final Documentation]]

## Phase: 7 — Stabilization & Scale
## Prerequisites: All UI sessions
## Complexity: Medium

## Objective
Audit and fix accessibility issues to meet WCAG 2.1 Level AA compliance for both web and mobile.

---

## Tasks

- [ ] **Web Dashboard Audit:**
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
- [ ] **Mobile App Audit:**
  - VoiceOver (iOS) support: all elements have accessibility labels
  - TalkBack (Android) support: all elements accessible
  - Minimum touch targets: 48x48dp
  - Text scalable with system font size
  - Color contrast in both light and dark themes
  - Screen reader announcements for countdown, status changes, alerts
  - Focus order logical in all screens
- [ ] Run automated accessibility tools:
  - Web: axe-core, Lighthouse accessibility audit
  - Mobile: Flutter accessibility inspector
- [ ] Fix all Level A and AA violations
- [ ] Manual testing with screen reader (VoiceOver + TalkBack)
- [ ] Verify i18n: French and English both fully translated

## Files to Modify
- Various frontend components (add ARIA, fix contrast, keyboard nav)
- Various mobile widgets (add semantics labels, touch targets)

## Tests
- [ ] Lighthouse accessibility score >= 90 (web)
- [ ] axe-core: zero Level A/AA violations
- [ ] Keyboard-only navigation works for all web pages
- [ ] Screen reader can announce all interactive elements
- [ ] Color contrast passes for all text elements
- [ ] Mobile touch targets >= 48x48dp
- [ ] Text remains readable at 200% system font size
- [ ] Both FR and EN translations complete

## Acceptance Criteria
- WCAG 2.1 Level AA compliance for web dashboard
- VoiceOver and TalkBack fully functional for mobile
- Lighthouse accessibility score >= 90
- Zero Level A/AA violations from axe-core
- French and English translations complete

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
