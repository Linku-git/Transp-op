# Transpop — Development Roadmap

> See also: [[PROGRESS]] | [[ARCHITECTURE]] | [[agents]]

## Timeline Overview

| Phase | Duration | Sessions | Start | End | Dependencies |
|-------|----------|----------|-------|-----|-------------|
| Phase 0 — Setup | 4 weeks | [[sessions/session-01|Sessions 01]]-[[sessions/session-05|05]] | Week 1 | Week 4 | None |
| Phase 1 — MVP Core | 14 weeks | [[sessions/session-06|Sessions 06]]-[[sessions/session-30|30]] | Week 5 | Week 18 | Phase 0 |
| Phase 2 — Financial | 14 weeks | [[sessions/session-31|Sessions 31]]-[[sessions/session-44|44]] | Week 19 | Week 32 | Phase 1 |
| Phase 3 — Mobile | 10 weeks | [[sessions/session-45|Sessions 45]]-[[sessions/session-56|56]] | Week 19 | Week 28 | Phase 1 (can parallel Phase 2) |
| Phase 4 — Security & RTI | 8 weeks | [[sessions/session-57|Sessions 57]]-[[sessions/session-66|66]] | Week 29 | Week 36 | Phase 1, Phase 3 |
| Phase 5 — Valorization | 8 weeks | [[sessions/session-67|Sessions 67]]-[[sessions/session-76|76]] | Week 33 | Week 40 | Phase 2, Phase 3 |
| Phase 6 — Integrations | 8 weeks | [[sessions/session-77|Sessions 77]]-[[sessions/session-86|86]] | Week 37 | Week 44 | Phase 1 |
| Phase 7 — Stabilization | 4 weeks | [[sessions/session-87|Sessions 87]]-[[sessions/session-92|92]] | Week 45 | Week 48 | All phases |

**Total: ~48 weeks (12 months) with parallelization**

---

## Phase 0 — Cadrage & Setup (Weeks 1-4)

### Milestone: Development Environment Ready

```
Session 01 -----> Session 02 -----> Session 03
(Docker/Infra)    (Backend)         (Frontend)
                       \               /
                        v             v
                      Session 04 --------> Session 05
                      (Auth/RBAC)          (CI/CD)
```

**Deliverables:**
- Docker Compose dev environment (PostgreSQL, Redis, OSRM)
- FastAPI skeleton with health endpoint
- React scaffold with routing and layout
- Auth middleware (JWT validation, RBAC)
- GitHub Actions CI pipeline
- Test infrastructure (pytest, vitest)

---

## Phase 1 — MVP Core (Weeks 5-18)

### Milestone: Functional Optimization Platform

```
Module A (Sites)          Module B (Employees)
Sessions 06-08            Sessions 09-14
     |                         |
     +------> Module C (Modal) |
              Sessions 15-17   |
                    |          |
                    v          v
              Module D (Optimization)
              Sessions 18-25
                    |
                    v
         Scenarios & Export
         Sessions 26-30
```

**Deliverables:**
- Site CRUD with map-based management
- Employee data management with Excel import
- Modal analysis with charts and insights
- Full optimization engine (clustering, routing, CVRP)
- Interactive map with routes, clusters, meeting zones
- Weather integration and scenario simulation
- PDF/Excel/CSV/GeoJSON exports

**Key Milestones:**
- Week 6: Sites + Employees functional
- Week 10: Excel import working
- Week 14: Optimization engine producing results
- Week 16: Full map visualization
- Week 18: Scenarios and exports complete

---

## Phase 2 — Financial & Reporting (Weeks 19-32)

### Milestone: Financial Decision Support Tool

```
Financial Models (31) --> TCO Engine (32) --> ROI Engine (33)
                              |                    |
                              v                    v
                      Comparator (34) --> Financial Dashboard (35-36)
                              |
                              v
                   Cost/Trip + Breakeven (37) --> DAF Export (38)

HR Dashboard (39-40) --> RSE Dashboard (41) --> Reports (42-43) --> KPIs (44)
```

**Deliverables:**
- TCO calculator (per-vehicle, per-fleet, by motorization)
- ROI calculator (4 levers: absenteeism, retention, fleet, journey)
- Investment model comparator (CAPEX vs mise-a-dispo vs OPEX)
- HR dashboard (mobility coverage, absenteeism correlation)
- RSE dashboard (CO2, modal shift, ZFE, DPEF)
- Enhanced reporting engine (8 report types)
- KPI historical tracking

---

## Phase 3 — Mobile MVP (Weeks 19-28)

**Can run in parallel with Phase 2** (different team/skillset: Flutter vs React)

### Milestone: Employee Mobile App

```
Flutter Setup (45) --> Auth (46) --> Onboarding (47)
                                        |
                                        v
                    Home (48) --> Trip Booking (49-50)
                       |              |
                       v              v
                    RTI (51) --> Push (52) --> Profile (53)
                                                  |
                                                  v
                              Backend API (54) --> Stats (55) --> Offline (56)
```

**Deliverables:**
- Flutter app (iOS + Android)
- SSO authentication
- Onboarding wizard (preferences + security questionnaire)
- Home screen with next departure countdown
- Trip booking, modification, cancellation
- Real-time vehicle tracking (WebSocket)
- Push notifications (FCM)
- Offline mode with local caching
- Profile and preferences management

---

## Phase 4 — Security & RTI (Weeks 29-36)

### Milestone: Security-Hardened Transport with RTI Guarantee

```
Risk Scoring (57) --> RTI Backend (58) --> Adaptive Sizing (59)
                           |
                           v
                    RTI Dashboard (60)

Questionnaire (61) --> Scoring Engine (62) --> Constrained Pooling (63)
                                                      |
                                                      v
                           Security Dashboard (64) --> Night Mode (65)
                                                           |
                                                           v
                                                Emergency System (66)
```

**Deliverables:**
- Stop risk scoring algorithm
- RTI backend with compliance tracking
- Adaptive sizing with buffer vehicles
- RTI monitoring dashboard
- Security questionnaire + scoring
- Security-constrained pooling (night rules)
- Mobile night mode + emergency button
- Emergency alert routing

---

## Phase 5 — Journey Valorization (Weeks 33-40)

### Milestone: Commute Time Valorization

```
Content Model (67) --> Content Frontend (68) --> Delivery Engine (69)
                                                       |
                                                       v
           Mobile Feed (70) --> Training Player (71) --> Surveys (72-73)
                                                              |
                                                              v
                                    LMS Integration (74) --> Analytics (75)
                                                                   |
                                                                   v
                                                    Value Measurement (76)
```

**Deliverables:**
- Content management system (web)
- Content feed on mobile app
- Micro-training player (video, audio, quiz)
- Survey/poll system
- LMS integration (Cornerstone, 360Learning)
- Engagement analytics dashboard
- Value measurement (hours recovered, monetary estimate)

---

## Phase 6 — Enterprise Integrations (Weeks 37-44)

### Milestone: Enterprise-Ready Integrations

```
SIRH Framework (77) --> SAP (78) --> Workday (79) --> Talentsoft/Sage (80)
                                                            |
                                                            v
                                                   Sync Dashboard (81)

Operator Export (82) --> Via/SWVL (83) --> Operator Portal (84)

ERP Export (85) --> Payment (86)
```

**Deliverables:**
- SIRH sync framework (delta updates, conflict resolution)
- SAP SuccessFactors, Workday, Talentsoft, Sage connectors
- SIRH sync dashboard
- Operator sizing plan export (JSON/XML/PDF)
- Via & SWVL API integration
- Operator portal (web, read-only)
- ERP finance export (SAP FI, Sage, Cegid)
- Stripe payment + Navigo/Edenred transport pass

---

## Phase 7 — Stabilization & Scale (Weeks 45-48)

### Milestone: Production-Ready Platform

```
Performance (87) --> Load Testing (88) --> Security (89)
                                               |
                                               v
                          RGPD Audit (90) --> Accessibility (91) --> App Store (92)
```

**Deliverables:**
- Query optimization, caching, connection pooling
- Load test passing (10K concurrent users)
- Penetration test completed (OWASP Top 10)
- RGPD compliance audit passed
- WCAG 2.1 AA accessibility audit
- App Store + Play Store publication
- Final documentation and deployment guide

---

## Parallelization Opportunities

| Parallel Track A | Parallel Track B | Weeks |
|-----------------|-----------------|-------|
| Phase 2 (Financial) | Phase 3 (Mobile) | 19-28 |
| Phase 4 (Security) | Phase 5 (Valorization, partial) | 33-36 |
| Phase 6 (SIRH connectors) | Phase 6 (Operator + ERP) | 37-44 |

With 2 parallel developers/teams, the timeline compresses from 70 weeks (sequential) to ~48 weeks.

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OSRM routing quality | Medium | Fallback to Google Maps API |
| Auth0/Keycloak complexity | Medium | Start with simple JWT, add SSO later |
| OR-Tools optimization performance | High | Profile early, consider Celery workers, caching |
| Flutter WebSocket stability | Medium | Fallback polling mode for RTI |
| SIRH API availability | Low | CSV/Excel fallback always available |
| PostGIS query performance | Medium | Spatial indexes, query optimization in Phase 7 |

---
## Related Documentation
- [[PROGRESS]] — Current implementation status
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database schema
- [[API_ENDPOINTS]] — API endpoints
- [[FRONTEND_PAGES]] — Web pages
- [[MOBILE_PAGES]] — Mobile screens
