# Session 46 — Mobile Auth Flow

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-04|Session 04]], [[sessions/session-45|Session 45]]
## Complexity: High
> Previous: [[sessions/session-45|Session 45]] | Next: [[sessions/session-47|Session 47]]

## Objective
Implement a complete authentication flow using Auth0/Keycloak OIDC, including secure token storage, automatic refresh, and MFA support, to enable secure user access to the mobile application.

---

## Tasks
- [ ] Implement Auth0/Keycloak OIDC login flow
- [ ] Create AuthService with login, logout, token storage, and auto-refresh capabilities
- [ ] Store tokens securely in flutter_secure_storage
- [ ] Create LoginScreen with SSO button, email/password fallback, and MFA input
- [ ] Create SplashScreen with auto-login check
- [ ] Handle token expiry with auto-refresh and force re-login fallback
- [ ] Create AuthProvider (Riverpod) for managing auth state across the app

## Files to Create/Modify
- `mobile/lib/services/auth_service.dart`
- `mobile/lib/providers/auth_provider.dart`
- `mobile/lib/screens/login_screen.dart`
- `mobile/lib/screens/splash_screen.dart`
- `mobile/lib/models/auth_token.dart`
- `mobile/lib/models/user.dart`
- `mobile/lib/config/auth_config.dart`
- `mobile/lib/config/routes.dart`

## Tests
- [ ] Login flow completes successfully with valid credentials
- [ ] Token is stored securely in flutter_secure_storage
- [ ] Auto-refresh triggers before token expiry
- [ ] Logout clears all stored tokens and navigates to LoginScreen
- [ ] MFA input is prompted when required
- [ ] SplashScreen redirects to Home when valid token exists
- [ ] SplashScreen redirects to Login when no valid token exists

## Acceptance Criteria
- Users can log in via SSO (Auth0/Keycloak OIDC)
- Users can fall back to email/password login
- MFA challenge is handled correctly
- Tokens are stored securely and never exposed in logs
- Expired tokens trigger automatic refresh without user intervention
- Failed refresh forces user back to login screen
- AuthProvider exposes current auth state to all screens via Riverpod
- SplashScreen performs auto-login check on app launch

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
