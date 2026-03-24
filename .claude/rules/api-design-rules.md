# API Design Rules

## Versioning
- All endpoints under `/api/v1/`
- Breaking changes require new version (`/api/v2/`)
- Deprecation: 3-month notice via `Sunset` header

## URL Convention
- Plural nouns: `/api/v1/sites`, `/api/v1/employees`
- Nested resources: `/api/v1/sites/{site_id}/employees`
- Actions as verbs: `/api/v1/scenarios/{id}/optimize`
- Query params for filtering: `?status=active&department=IT`
- Always use UUID for resource IDs

## Request/Response Format

### Success Response
```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "pages": 10,
    "total": 200,
    "page_size": 20
  }
}
```

### Error Response
```json
{
  "detail": "Human-readable error message",
  "code": "RESOURCE_NOT_FOUND",
  "field": "email"
}
```

### Error Codes
- `VALIDATION_ERROR` — 422 (Pydantic validation failure)
- `RESOURCE_NOT_FOUND` — 404
- `RESOURCE_ALREADY_EXISTS` — 409
- `UNAUTHORIZED` — 401 (no token or expired)
- `FORBIDDEN` — 403 (insufficient role)
- `RATE_LIMITED` — 429
- `INTERNAL_ERROR` — 500

## Pagination
- Default: `page_size=20`, `page=1`
- Max: `page_size=100`
- Always return `total`, `page`, `pages` in meta
- Use offset-based pagination (not cursor)

## Filtering & Sorting
- Filter: `?status=active&created_after=2025-01-01`
- Sort: `?sort=created_at&order=desc`
- Search: `?q=search+term` (full-text search)
- Multiple values: `?status=active,pending`

## Rate Limit Headers
Every response includes:
- `X-RateLimit-Limit: 1000`
- `X-RateLimit-Remaining: 999`
- `X-RateLimit-Reset: 1234567890`

## HTTP Methods
| Method | Use Case | Idempotent |
|--------|----------|------------|
| GET | Read resource(s) | Yes |
| POST | Create resource | No |
| PUT | Full update | Yes |
| PATCH | Partial update | Yes |
| DELETE | Remove resource | Yes |

## OpenAPI
- Every endpoint must have OpenAPI docstring
- Include request/response examples
- Tag endpoints by module (sites, employees, optimization, etc.)
- Swagger UI available at `/docs` (dev only)
