# Security Rules

## Authentication (JWT)
- All endpoints require JWT except `/health`, `/`, `/auth/login`, `/auth/register`
- Access token expiry: 15 minutes
- Refresh token expiry: 7 days, rotate on use
- Store refresh tokens server-side (Redis or DB), never client-only
- MFA: TOTP-based, AES-256 encrypted secret storage

## Authorization (RBAC)
- 5 roles: admin, drh, daf, salarie, operateur
- Check role in route handler via dependency injection
- Never trust client-side role claims
- Operateur: read-only access to assigned data only
- Salarie: own data only (enforce `user_id` filter)
- Multi-tenant: always filter by `tenant_id`

## Rate Limiting
| Role | Limit |
|------|-------|
| Admin | 2000 req/min |
| DRH | 1000 req/min |
| DAF | 1000 req/min |
| Salarie | 500 req/min |
| Operateur | 100 req/min |

## Input Validation
- All input via Pydantic models (auto-sanitization)
- File uploads: validate MIME type, max 10MB, scan for malicious content
- URL parameters: validate UUIDs, reject path traversal
- Geospatial input: validate lat/lng ranges (-90/90, -180/180)

## Data Encryption
- At rest: AES-256 for `mfa_secret`, employee home addresses, personal phone numbers
- In transit: HTTPS/TLS 1.3 only
- Passwords: bcrypt with work factor 12
- Database: encrypted connections (SSL required)

## RGPD Compliance
- Geolocation: active-only, never background tracking
- Data retention: 30 days for logs, configurable per data type
- Right to deletion: cascade delete on employee removal
- Consent: explicit opt-in required for location sharing
- Data export: employee can request JSON export of all their data
- No PII in logs (mask email, phone, address in log output)

## Headers
Every response must include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

## CORS
- Allowed origins: explicit list (never `*` in production)
- Allowed methods: GET, POST, PUT, PATCH, DELETE
- Credentials: true (for JWT cookies)
