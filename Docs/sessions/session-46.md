# Session 46 — Mobile Auth Flow

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-04|Session 04]], [[sessions/session-45|Session 45]]
## Complexity: High
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-45|Session 45]] | Next: [[sessions/session-47|Session 47]]

## Objective
Implement a complete JWT authentication flow using the existing Transpop FastAPI backend (`POST /api/v1/auth/login`). Include secure token storage, automatic refresh, and a polished login screen.

---

## Tasks
- [x] Implement `AuthService` using `dio` against the existing backend JWT endpoints:
  - `POST /api/v1/auth/login` — email + password → `{access_token, refresh_token, token_type}`
  - `POST /api/v1/auth/refresh` — refresh token → new `access_token`
  - `POST /api/v1/auth/logout` — invalidate token server-side
  - `GET /api/v1/auth/me` — fetch current user profile
- [x] Store JWT tokens securely in `flutter_secure_storage`:
  - Key `access_token` — 15-minute access JWT
  - Key `refresh_token` — 7-day refresh JWT
  - Key `user_id` — cached user UUID
  - Key `biometric_enabled` — biometric preference flag
- [x] Implement auto-refresh: `dio` interceptor intercepts 401 responses, attempts refresh with separate Dio instance, retries original request on success, clears tokens and forces logout on failure
- [x] Create `AuthNotifier` (Riverpod `StateNotifier`) managing auth state: `initial`, `loading`, `authenticated`, `unauthenticated`, `error`
- [x] Create `LoginScreen`:
  - Transpop gradient logo + "Plateforme Mobilité RH" tagline
  - Email + password fields with validation (empty check, @ format check)
  - "Se connecter" primary button with loading spinner
  - Error banner handling Pydantic v2 error format (`detail` as string or array)
  - Password visibility toggle
- [x] Create `SplashScreen`:
  - Branded splash with Transpop logo on primary background
  - Checks for stored refresh token via `AuthNotifier.checkSession()`
  - If valid refresh token: silently refresh → navigate to `/home`
  - If refresh fails or no token: navigate to `/login`
- [x] Update `routes.dart` to use real `SplashScreen` and `LoginScreen` instead of placeholders
- [x] Create `ApiClient` with dio base configuration and token interceptor
- [x] Create `extractApiError()` utility matching frontend's `extractApiError()` pattern

## Files Created
- `mobile/lib/models/user.dart` — User model matching backend `UserResponse` schema (id, email, first_name, last_name, role_id, tenant_id, mfa_enabled, is_active, displayName)
- `mobile/lib/models/auth_token.dart` — AuthToken model (access_token, refresh_token, token_type)
- `mobile/lib/services/api_client.dart` — Dio client with Bearer token injection and auto-refresh interceptor
- `mobile/lib/services/auth_service.dart` — AuthService (login, tryRefresh, logout, getProfile, clearSession, biometric prefs)
- `mobile/lib/providers/auth_provider.dart` — AuthNotifier (StateNotifier) + apiClientProvider + authServiceProvider
- `mobile/lib/utils/api_error.dart` — Pydantic v2 error extractor (handles string detail, array detail, timeout, connection errors)
- `mobile/lib/screens/auth/splash_screen.dart` — Auto-login splash with branding
- `mobile/lib/screens/auth/login_screen.dart` — Login form with validation and error display

## Files Modified
- `mobile/lib/config/routes.dart` — Replaced placeholder screens with real `SplashScreen` and `LoginScreen`

## Auth Flow
```
App Launch
  → SplashScreen
    → checkSession()
      → hasStoredSession()? (reads refresh_token from flutter_secure_storage)
        → YES: tryRefresh() → POST /api/v1/auth/refresh
          → Success: getProfile() → GET /api/v1/auth/me → navigate to /home
          → Failure: clearSession() → navigate to /login
        → NO: navigate to /login

Login
  → LoginScreen
    → Submit form → AuthNotifier.login(email, password)
      → POST /api/v1/auth/login → store tokens → getProfile() → navigate to /home
      → Error: show error banner with extractApiError()

Authenticated API calls
  → ApiClient.dio injects Bearer token on every request
  → On 401: auto-refresh with separate Dio instance → retry original request
  → If refresh fails: clear tokens → force logout
```

## Interceptor Design
- **Request interceptor:** Reads access_token from `flutter_secure_storage`, adds `Authorization: Bearer <token>` header
- **Error interceptor:** On 401 (non-auth endpoints), uses a separate `Dio` instance to POST `/auth/refresh`, stores new tokens, retries original request with `dio.fetch(requestOptions)`. Prevents infinite loops by skipping refresh for `/auth/login` and `/auth/refresh` endpoints. Uses `_isRefreshing` mutex to prevent concurrent refreshes.

## Tests
- Tests written: 28 (session 46) + 22 (session 45) = 50 total
- Tests passing: 50
- Tests failing: 0

### Test files:
- `test/models/user_test.dart` — fromJson, null handling, displayName (full name, email fallback), toJson
- `test/models/auth_token_test.dart` — fromJson, default token_type
- `test/utils/api_error_test.dart` — String detail, Pydantic v2 array detail, connection timeout, connection error, custom fallback, string passthrough, default fallback
- `test/providers/auth_provider_test.dart` — AuthState (initial, authenticated, loading, copyWith), AuthStatus enum
- `test/screens/login_screen_test.dart` — Logo/title render, email/password fields, login button, empty email validation, empty password validation, invalid email format, password visibility toggle
- `test/screens/splash_screen_test.dart` — Branding render, loading indicator, bus icon (with mocked AuthNotifier)

## Implementation Notes
- **Biometric unlock** (local_auth) is prepared in `AuthService` (setBiometricEnabled/isBiometricEnabled) but not wired into UI — biometric prompt will be added in a future session when `local_auth` is added to pubspec
- **Auth tests** use `_NoOpAuthNotifier` pattern to override `checkSession()` and avoid `flutter_secure_storage` platform channel errors in widget tests
- **Error extraction** mirrors frontend's `extractApiError()` from `@/lib/apiError.ts` — handles both `detail: "string"` and `detail: [{type, loc, msg}]` Pydantic v2 formats
- **Token refresh** uses a **separate Dio instance** (not the main one) to avoid interceptor loops
- **French UI:** All user-facing text in French (Connexion, Se connecter, Veuillez saisir, Réessayer, etc.)

## Acceptance Criteria
- [x] Users authenticate against `POST /api/v1/auth/login` with email/password
- [x] JWT access + refresh tokens stored in `flutter_secure_storage`
- [x] `dio` interceptor auto-refreshes on 401 without user intervention
- [x] Failed refresh forces re-login (clears all stored tokens)
- [x] `AuthNotifier` exposes current auth state to all screens via Riverpod
- [x] `SplashScreen` performs auto-login check on app launch
- [x] Biometric unlock prepared in service layer (UI deferred)
- [x] Pydantic v2 error format handled (string and array detail)
- [x] `flutter analyze` reports 0 issues
- [x] All 50 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference (`/api/v1/auth/login`, `/api/v1/auth/refresh`, `/api/v1/auth/me`)
- [[ARCHITECTURE]] — System architecture
