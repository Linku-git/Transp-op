# Session 04 — Auth & RBAC Foundation

## Phase: 0 — Cadrage & Setup
## Prerequisites: [[sessions/session-02|Session 02]]

> Previous: [[sessions/session-03|Session 03]] | Next: [[sessions/session-05|Session 05]]

## Complexity: High

## Objective
Implement authentication (JWT), RBAC models (Tenant, User, Role, Permission), auth middleware, and basic user management API endpoints.

---

## Tasks

- [x] Create `backend/app/models/auth.py` — Tenant, User, Role, Permission, RolePermission models
- [x] Create Alembic migration for auth tables
- [x] Create `backend/app/schemas/auth.py` — Pydantic schemas (UserCreate, UserResponse, LoginRequest, TokenResponse, RoleCreate)
- [x] Create `backend/app/middleware/auth.py` — JWT token validation middleware (decode, verify expiry, extract user)
- [x] Create `backend/app/middleware/rbac.py` — Permission checker dependency (role + resource + action)
- [x] Create `backend/app/api/v1/auth.py` — Auth endpoints:
  - POST `/auth/login` — Validate credentials, issue JWT (dev mode with local auth; prod delegates to Auth0)
  - POST `/auth/logout` — Invalidate token (Redis blacklist)
  - POST `/auth/refresh` — Refresh access token
  - GET `/auth/me` — Get current user profile
- [x] Create `backend/app/api/v1/users.py` — User management endpoints:
  - GET `/users` — List users (admin only)
  - POST `/users` — Create user (admin only)
  - PUT `/users/{id}` — Update user
  - DELETE `/users/{id}` — Deactivate user
- [x] Create `backend/app/api/v1/roles.py` — Role endpoints:
  - GET `/roles` — List roles
  - POST `/roles` — Create role
  - PUT `/roles/{id}` — Update role permissions
- [x] Create `backend/app/api/v1/tenants.py` — Tenant endpoints:
  - GET `/tenants` — List tenants
  - POST `/tenants` — Create tenant
  - PUT `/tenants/{id}` — Update tenant config
- [x] Create seed data script: default tenant, admin user, 5 system roles (drh, daf, salarie, operateur, admin) with permissions
- [x] Create `backend/app/utils/security.py` — Password hashing (bcrypt), JWT encode/decode
- [x] Register all auth routers in `api/v1/__init__.py`
- [x] Create `backend/tests/test_auth.py` — Auth endpoint tests
- [x] Create `backend/tests/test_users.py` — User CRUD tests
- [x] Verify login returns valid JWT token
- [x] Verify protected endpoints reject requests without token
- [x] Verify RBAC blocks unauthorized role access

## Files to Create
- `backend/app/models/auth.py`
- `backend/app/schemas/auth.py`
- `backend/app/middleware/auth.py`
- `backend/app/middleware/rbac.py`
- `backend/app/api/v1/auth.py`
- `backend/app/api/v1/users.py`
- `backend/app/api/v1/roles.py`
- `backend/app/api/v1/tenants.py`
- `backend/app/utils/security.py`
- `backend/app/scripts/seed_data.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_users.py`
- `alembic/versions/xxxx_add_auth_tables.py`

## Tests
- [x] `test_login_success` — Valid credentials return JWT token
- [x] `test_login_invalid_password` — Returns 401
- [x] `test_login_nonexistent_user` — Returns 401
- [x] `test_protected_endpoint_no_token` — Returns 401
- [x] `test_protected_endpoint_expired_token` — Returns 401
- [x] `test_protected_endpoint_valid_token` — Returns 200
- [x] `test_rbac_admin_access` — Admin can access user management
- [x] `test_rbac_salarie_blocked` — Salarie cannot access user management
- [x] `test_create_user` — Admin creates user successfully
- [x] `test_get_me` — Returns current user profile
- [x] `test_refresh_token` — Returns new access token

## Acceptance Criteria
- Login endpoint returns valid JWT (access + refresh tokens)
- Auth middleware validates JWT on protected endpoints
- RBAC middleware enforces role-based permissions
- 5 system roles created with correct permissions
- All 11 tests pass

## Test Results
- Tests written: 11 (test_auth: 8, test_users: 3)
- Tests passing: 15 (11 new + 4 from session 02)
- Tests failing: 0
- Coverage: N/A

## Notes
- Pinned bcrypt==4.2.1 (passlib incompatible with bcrypt 5.x)
- Added pydantic[email] for EmailStr validation
- Fixed asyncpg connection pool issue in tests by using NullPool when TESTING=1
- `get_db` dependency uses `session.begin()` context for proper auto-commit/rollback
- Logout is a placeholder — Redis token blacklisting deferred to later session
- `employee_id` on User is a bare UUID (no FK) — FK added when Employee model arrives in session 09

## Related Documentation
- [[DATABASE_SCHEMA]] — Database schema
- [[API_ENDPOINTS]] — API endpoints
- [[PROGRESS]] — Progress tracker
- [[agents]] — Development rules
