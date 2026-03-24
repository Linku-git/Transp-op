# Transpop — System Architecture

> See also: [[DATABASE_SCHEMA]] | [[API_ENDPOINTS]] | [[ROADMAP]] | [[agents]]

## High-Level Architecture

```
                    +-------------------+
                    |   Load Balancer   |
                    +-------------------+
                     /        |         \
            +-------+    +-------+    +----------+
            |  Web  |    |Mobile |    | Operator |
            | React |    |Flutter|    |  Portal  |
            +-------+    +-------+    +----------+
                 \           |           /
                  \          |          /
              +----------------------------+
              |      API Gateway           |
              |   (FastAPI + Middleware)    |
              +----------------------------+
              |  Auth  | RBAC | RateLimit  |
              +----------------------------+
                     |            |
          +----------+            +----------+
          |                                  |
    +-----------+                    +-------------+
    | REST API  |                    |  WebSocket  |
    | Endpoints |                    |  (RTI/Live) |
    +-----------+                    +-------------+
          |                                  |
    +-------------------------------------------+
    |          Service Layer                     |
    |  +-------------+ +------------------+     |
    |  | Optimization | | Financial Engine |     |
    |  | (OR-Tools,   | | (TCO, ROI,      |     |
    |  |  sklearn)    | |  Comparator)    |     |
    |  +-------------+ +------------------+     |
    |  +-------------+ +------------------+     |
    |  | Excel Parser | | Security Engine  |     |
    |  | (openpyxl)   | | (Risk Scoring)   |     |
    |  +-------------+ +------------------+     |
    +-------------------------------------------+
          |                    |
    +----------+        +-----------+
    |PostgreSQL|        |   Redis   |
    | +PostGIS |        | Cache +   |
    |          |        | Sessions  |
    +----------+        +-----------+
                              |
                        +-----------+
                        |  Celery   |
                        |  Workers  |
                        +-----------+
```

## Component Details

### 1. Backend API — FastAPI

**Base URL:** `http://localhost:8000/api/v1`

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI (Python 3.11+) | Async REST API + WebSocket |
| ORM | SQLAlchemy 2.0 + GeoAlchemy2 | Database access + geospatial |
| Validation | Pydantic v2 | Request/response schemas |
| Auth | JWT (Auth0/Keycloak) | Token-based authentication |
| Task Queue | Celery + Redis | Async heavy computation |
| API Docs | OpenAPI 3.0 (auto-generated) | Swagger UI at `/docs` |

**Key Design Decisions:**
- Stateless API (JWT auth, no server-side sessions for API)
- Redis for session store, caching, and Celery broker
- All geospatial operations via PostGIS (not application-level)
- Async endpoints for I/O-bound operations
- Celery for optimization runs, TCO calculations, report generation

### 2. Frontend Web — React + TypeScript

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18+ (strict mode) | UI components |
| Build | Vite | Fast dev server + build |
| Styling | TailwindCSS | Utility-first CSS |
| State | Zustand | Lightweight state management |
| Charts | Recharts | Analytics visualizations |
| Maps | Leaflet + react-leaflet | Interactive maps |
| HTTP | Axios | API communication |
| i18n | react-i18next | French/English |
| Testing | Vitest + RTL | Unit + integration tests |

**Key Design Decisions:**
- Zustand over Redux (simpler for this scope)
- Leaflet over Mapbox (open-source, no API key for dev)
- TailwindCSS over CSS modules (faster UI development)
- Recharts over D3 (React-native, simpler API)

### 3. Mobile App — Flutter

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Flutter (Dart) | Cross-platform mobile |
| Maps | Google Maps Flutter | Vehicle tracking, routes |
| Push | Firebase FCM | Notifications |
| Offline | Hive + SQLite | Local data persistence |
| Auth | Auth0 Flutter SDK | SSO/OIDC login |
| Real-time | WebSocket (socket_io_client) | RTI vehicle positions |
| State | Riverpod / Provider | State management |

**Key Design Decisions:**
- Flutter for single codebase (iOS + Android)
- Hive for fast key-value offline storage
- SQLite for structured offline queries (trip history)
- Active-only geolocation (never background — RGPD)

### 4. Database — PostgreSQL + PostGIS

| Aspect | Detail |
|--------|--------|
| Version | PostgreSQL 15+ |
| Extension | PostGIS (geospatial) |
| Migrations | Alembic |
| Table Groups | 10 groups, 35+ tables |
| Spatial Operations | ST_Distance, ST_DWithin, ST_MakePoint |

**Schema Groups:**
1. Core — see [[DATABASE_SCHEMA#Group 2 Core — Sites|Sites]], [[DATABASE_SCHEMA#Group 3 Core — Employees|Employees]], [[DATABASE_SCHEMA#Group 4 Core — Vehicles|Vehicles]]
2. Optimization — see [[DATABASE_SCHEMA#Group 6 Optimization|Optimization]]
3. Modal — see [[DATABASE_SCHEMA#Group 3 Core — Employees|EmployeeModal & EmployeeLeave]]
4. Financial — see [[DATABASE_SCHEMA#Group 8 Financial|Financial]]
5. Content — see [[DATABASE_SCHEMA#Group 9 Content|Content]]
6. RTI — see [[DATABASE_SCHEMA#Group 10 RTI|RTI]]
7. Security — see [[DATABASE_SCHEMA#Group 11 Security|Security]]
8. Auth — see [[DATABASE_SCHEMA#Group 1 Auth & Multi-Tenant|Auth & Multi-Tenant]]
9. SIRH — see [[DATABASE_SCHEMA#Group 12 SIRH|SIRH]]
10. Mobile/Operator — see [[DATABASE_SCHEMA#Group 13 Mobile|Mobile]], [[DATABASE_SCHEMA#Group 14 Operator|Operator]], [[DATABASE_SCHEMA#Group 15 Reporting|Reporting]]

### 5. Redis

| Usage | Key Pattern | TTL |
|-------|------------|-----|
| Session store | `session:{user_id}` | 24h |
| Site config cache | `site:{id}:config` | 1h |
| Vehicle catalog cache | `vehicles:catalog` | 30min |
| RTI positions | `rti:vehicle:{id}:pos` | 30s |
| Rate limiting | `ratelimit:{ip}:{endpoint}` | 1min |
| Celery broker | `celery:*` | — |

### 6. Celery Workers

| Task | Queue | Priority | Timeout | Session |
|------|-------|----------|---------|---------|
| Optimization run | `optimization` | High | 5min | (see [[sessions/session-23]]) |
| TCO calculation | `financial` | Medium | 30s | (see [[sessions/session-32]]) |
| ROI calculation | `financial` | Medium | 30s | (see [[sessions/session-32]]) |
| Report generation | `reports` | Low | 2min | |
| Excel import | `imports` | Medium | 1min | |
| SIRH sync | `sync` | Low | 5min | |
| Weather refresh | `external` | Low | 30s | |
| Push notification | `notifications` | High | 10s | |

### 7. External Service Integration

```
+-------------------+     +-------------------+
|   OSRM / Google   |     |  OpenWeatherMap   |
|   Maps / HERE     |     |  Meteo-France     |
| (Routing + ETA)   |     | (3-day forecast)  |
+-------------------+     +-------------------+

+-------------------+     +-------------------+
|  Nominatim /      |     | Auth0 / Keycloak  |
|  Google Geocoding |     | (SSO, JWT, MFA)   |
+-------------------+     +-------------------+

+-------------------+     +-------------------+
|  SIRH APIs        |     | Firebase FCM      |
| (SAP, Workday,    |     | (Push notifs)     |
|  Talentsoft, Sage)|     +-------------------+
+-------------------+
                          +-------------------+
+-------------------+     | Stripe            |
| LMS APIs          |     | (Payments)        |
| (Cornerstone,     |     +-------------------+
|  360Learning)     |
+-------------------+
```

### 8. Infrastructure

#### Development
```yaml
# docker-compose.yml services
services:
  backend:     FastAPI app (port 8000)
  frontend:    React dev server (port 5173)
  db:          PostgreSQL 15 + PostGIS (port 5432)
  redis:       Redis 7 (port 6379)
  celery:      Celery worker
  celery-beat: Celery scheduler
  osrm:        OSRM routing engine (port 5000)
```

#### Production (Kubernetes)
- **Namespace:** `transpop-prod`
- **Deployments:** api (3 replicas), celery-worker (2), celery-beat (1)
- **StatefulSets:** PostgreSQL (primary + replica), Redis (sentinel)
- **Ingress:** NGINX with TLS termination
- **HPA:** Auto-scale API pods on CPU >70%
- **Secrets:** External secrets from Vault/AWS Secrets Manager
- **Monitoring:** Grafana + Prometheus + Loki (logs)

### 9. Security Architecture

```
Client -> TLS 1.3 -> Load Balancer -> API Gateway
                                        |
                                   JWT Validation
                                        |
                                   RBAC Middleware
                                        |
                                   Rate Limiter
                                        |
                                   Input Validation (Pydantic)
                                        |
                                   ORM (parameterized queries)
                                        |
                                   AES-256 encrypted DB
```

**Key Security Measures:**
- TLS 1.3 for all communications
- AES-256 at-rest encryption for sensitive data
- JWT tokens: 15min access, 7-day refresh
- MFA mandatory for DRH, DAF, Admin
- RBAC per-endpoint authorization
- Rate limiting: 1000/500/100 req/min by role
- CORS whitelist
- RGPD: active-only geolocation, 30-day retention, consent management

### 10. Data Flow Diagrams

#### Optimization Flow
```
Excel Import / SIRH Sync
        |
        v
  Employee Data (DB)
        |
        v
  Clustering Engine (sklearn)
        |
        v
  Meeting Zone Optimizer
        |
        v
  Vehicle Assignment (bin-packing)
        |
        v
  Route Optimization (OR-Tools CVRP + OSRM)
        |
        v
  RTI Constraint Validation
        |
        v
  Results (clusters, routes, metrics) -> DB
        |
        v
  Dashboard (Web) / Export (PDF/Excel)
```

#### RTI Real-Time Flow
```
GPS Tracker -> POST /rti/vehicle-position
                      |
                      v
                Redis (rti:vehicle:{id}:pos)
                      |
                      v
              WebSocket broadcast to:
              - Mobile app (employee countdown)
              - Web dashboard (supervisor view)
                      |
                      v
              RTIEvent logged to DB (compliance tracking)
```

---
## Related Documentation
- [[DATABASE_SCHEMA]] — Complete table definitions
- [[API_ENDPOINTS]] — All REST & WebSocket endpoints
- [[FRONTEND_PAGES]] — Web dashboard pages
- [[MOBILE_PAGES]] — Mobile app screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline capabilities
- [[ROADMAP]] — Development timeline
- [[PROGRESS]] — Implementation status
