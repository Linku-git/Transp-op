# Session 89 — Security Hardening & Penetration Testing

> Previous: [[sessions/session-88|Session 88 — Load Testing]] | Next: [[sessions/session-90|Session 90 — RGPD Audit & Compliance]]

## Phase: 7 — Stabilization & Scale
## Prerequisites: All previous phases
## Complexity: High

## Objective
Harden security against OWASP Top 10 vulnerabilities and prepare for penetration testing.

---

## Tasks

- [ ] Audit all API endpoints for OWASP Top 10:
  - A01: Broken Access Control — verify RBAC on every endpoint
  - A02: Cryptographic Failures — verify TLS, encryption at rest, password hashing
  - A03: Injection — verify all inputs use ORM (no raw SQL), Pydantic validation
  - A04: Insecure Design — review data flow for sensitive data exposure
  - A05: Security Misconfiguration — verify CORS, headers, debug mode off
  - A06: Vulnerable Components — run `pip audit`, `npm audit`
  - A07: Auth Failures — verify JWT validation, MFA enforcement, session management
  - A08: Data Integrity Failures — verify file upload validation, deserialization
  - A09: Logging Failures — verify audit logging on sensitive operations
  - A10: SSRF — verify no user-controlled URLs passed to server-side requests
- [ ] Add security headers middleware (X-Content-Type-Options, X-Frame-Options, CSP, HSTS)
- [ ] Implement audit logging for all write operations (user, timestamp, action, resource)
- [ ] Verify rate limiting is enforced per role
- [ ] Verify CORS whitelist is configured (no wildcards in production)
- [ ] Verify file upload validation (type check, size limit, content scanning)
- [ ] Verify JWT token validation (signature, expiry, audience, issuer)
- [ ] Scan dependencies for known vulnerabilities
- [ ] Prepare pentest scope document
- [ ] Fix all critical and high vulnerabilities found

## Files to Modify
- `backend/app/middleware/security_headers.py` (create)
- `backend/app/middleware/audit_log.py` (create)
- `backend/app/main.py` (add security middleware)

## Tests
- [ ] All RBAC tests pass (no unauthorized access)
- [ ] SQL injection attempt returns 422 (not executed)
- [ ] XSS payload in input is sanitized
- [ ] CSRF token required for session endpoints
- [ ] File upload rejects executables and oversized files
- [ ] Rate limit returns 429 when exceeded
- [ ] Security headers present in all responses
- [ ] Audit log captures write operations
- [ ] No critical vulnerabilities in dependency scan

## Acceptance Criteria
- Zero critical/high OWASP vulnerabilities
- Security headers on all responses
- Audit logging operational
- Dependency vulnerabilities patched
- Pentest scope document ready

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
