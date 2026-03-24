# Session 90 — RGPD Audit & Compliance

> Previous: [[sessions/session-89|Session 89 — Security Hardening & Penetration Testing]] | Next: [[sessions/session-91|Session 91 — Accessibility Audit (WCAG 2.1 AA)]]

## Phase: 7 — Stabilization & Scale
## Prerequisites: All previous phases
## Complexity: Medium

## Objective
Verify full RGPD compliance: consent management, data retention, deletion rights, audit trails, and AIPD documentation.

---

## Tasks

- [ ] Implement employee consent mechanism:
  - Explicit opt-in for geolocation (active-only, never background)
  - Consent record stored with timestamp
  - Consent withdrawal mechanism
- [ ] Implement data retention policy:
  - Location data: max 30 days in active database
  - Automated cleanup job (Celery beat) for expired data
  - Archive policy for historical data
- [ ] Implement right to access:
  - Employee data export endpoint (JSON + CSV format)
  - GET `/employees/{id}/export-data` — full personal data package
- [ ] Implement right to deletion:
  - Employee data deletion on request
  - Cascade: delete leaves, modal, trips, content delivery, security data
  - Audit trail preserved (anonymized)
  - DELETE `/employees/{id}/gdpr-delete`
- [ ] Implement right to portability:
  - Standard format export (JSON, CSV)
  - Machine-readable format
- [ ] Verify geolocation: active mode only, never background
- [ ] Verify audit logging covers all personal data access
- [ ] Create cookie consent for web dashboard
- [ ] Draft privacy policy document (for App Store / Play Store)
- [ ] Complete RGPD compliance checklist (Appendix D of PRD)
- [ ] Prepare AIPD (Data Protection Impact Assessment) document

## Files to Create/Modify
- `backend/app/api/v1/gdpr.py` (create — RGPD endpoints)
- `backend/app/services/gdpr.py` (create — data export, deletion)
- `backend/app/tasks/cleanup_tasks.py` (create — retention cleanup)
- `frontend/src/components/CookieConsent.tsx` (create)

## Tests
- [ ] `test_data_export` — Returns complete personal data package
- [ ] `test_gdpr_delete` — Deletes all personal data, preserves anonymized audit
- [ ] `test_consent_record` — Consent stored with timestamp
- [ ] `test_consent_withdrawal` — Withdrawal stops data collection
- [ ] `test_retention_cleanup` — Expired location data cleaned up
- [ ] `test_no_background_location` — Verify no background geolocation code

## Acceptance Criteria
- All RGPD rights implemented (access, rectification, deletion, portability)
- Consent mechanism operational
- Data retention automatically enforced
- Audit trail complete for personal data access
- Privacy policy document ready
- RGPD checklist from PRD Appendix D fully checked

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
