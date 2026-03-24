# Performance Rules

## Database Queries
- Always run `EXPLAIN ANALYZE` on new queries touching >1000 rows
- Create indexes for columns used in WHERE, JOIN, ORDER BY
- Use `GIST` indexes for all PostGIS geometry columns
- Use `selectinload()` or `joinedload()` to prevent N+1 queries
- Never use `SELECT *` — specify only needed columns
- Limit result sets: max 100 rows per API request
- Use `EXISTS` instead of `COUNT(*)` for existence checks

## Connection Pooling (SQLAlchemy)
- `pool_size=10`
- `max_overflow=20`
- `pool_timeout=30`
- `pool_recycle=3600`

## Caching (Redis)
- Cache read-heavy, write-light data
- Always set TTL (never cache indefinitely)
- Use cache invalidation on writes (delete key on mutation)
- Cache key pattern: `{entity}:{tenant_id}:{id_or_filter}`
- Never cache user-specific sensitive data without encryption

## API Response Times
| Endpoint Type | Target | Max |
|--------------|--------|-----|
| Simple CRUD | <100ms | 500ms |
| List with filters | <200ms | 1s |
| Dashboard aggregations | <500ms | 2s |
| Optimization (small) | <5s | 10s |
| Optimization (large) | Async (Celery) | 5min |
| Report generation | Async (Celery) | 10min |

## Async Tasks (Celery)
- Any operation >5 seconds must be a Celery task
- Return task ID immediately, poll via `/tasks/{id}/status`
- Set hard timeout: optimization=300s, reports=600s
- Use result backend (Redis) with 1-hour expiry

## Frontend Performance
- Initial bundle: <500KB gzipped
- Code split routes with `React.lazy()`
- Lazy-load images with `loading="lazy"`
- Memoize expensive computations with `useMemo`/`React.memo`
- Limit Recharts data points to 1000 per chart
- Debounce search inputs (300ms)

## PostGIS Spatial
- Always use `ST_DWithin()` (uses spatial index) not `ST_Distance() < X`
- Index pattern: `CREATE INDEX idx_{table}_geom ON {table} USING GIST(geom)`
- Transform to metric SRID (e.g., 2154 for France) for distance calculations
- `CLUSTER {table} USING idx_{table}_geom` for range query optimization

## Monitoring Thresholds
- API p99 latency >2s: investigate
- Database query >1s: log as slow query
- Redis operation >50ms: investigate
- Celery task queue depth >100: scale workers
- Memory usage >80%: alert
