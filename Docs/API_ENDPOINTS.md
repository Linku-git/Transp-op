# Transpop — API Endpoints Reference

> Base URL: `http://localhost:8000/api/v1`
> Auth: JWT Bearer tokens (Auth0/Keycloak)
> Docs: OpenAPI 3.0 at `/docs`
>
> See also: [[ARCHITECTURE]] | [[DATABASE_SCHEMA]] | [[FRONTEND_PAGES]] | [[MOBILE_PAGES]] | [[agents]]

## Conventions

- **Pagination:** `?page=1&page_size=20` -> `{data: [], total, page, pages}`
- **Errors:** `{"detail": "message", "code": "ERROR_CODE", "field": "field_name"}`
- **Rate limits:** Web 1000/min, Mobile 500/min, Operator 100/min
- **Content-Type:** `application/json` (default), `multipart/form-data` (uploads)

---

## 1. Health & Info

| Method | Endpoint | Description | Auth | Session |
|--------|----------|-------------|------|---------|
| GET | `/` | API welcome message | No | 02 |
| GET | `/health` | Health check (DB, Redis, Celery) | No | 02 |

---

## 2. Auth & Users (27.18)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/auth/login` | Login (delegates to Auth0/Keycloak) | No | All | 04 |
| POST | `/auth/logout` | Logout, invalidate token | Yes | All | 04 |
| POST | `/auth/refresh` | Refresh access token | Yes | All | 04 |
| GET | `/auth/me` | Get current user profile | Yes | All | 04 |
| GET | `/users` | List users | Yes | Admin | 04 |
| POST | `/users` | Create user | Yes | Admin | 04 |
| PUT | `/users/{id}` | Update user | Yes | Admin, Self | 04 |
| DELETE | `/users/{id}` | Deactivate user | Yes | Admin | 04 |
| GET | `/roles` | List roles | Yes | Admin | 04 |
| POST | `/roles` | Create custom role | Yes | Admin | 04 |
| PUT | `/roles/{id}` | Update role permissions | Yes | Admin | 04 |
| GET | `/tenants` | List tenants | Yes | Platform Admin | 04 |
| POST | `/tenants` | Create tenant | Yes | Platform Admin | 04 |
| PUT | `/tenants/{id}` | Update tenant config | Yes | Platform Admin | 04 |

---

## 3. Sites (27.1)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/sites` | List sites (filters: city, zfe_zone) | Yes | DRH, DAF, Admin | 06 |
| GET | `/sites/{id}` | Get single site | Yes | DRH, DAF, Admin | 06 |
| GET | `/sites/code/{code}` | Get site by code | Yes | DRH, DAF, Admin | 06 |
| POST | `/sites` | Create site | Yes | DRH, Admin | 06 |
| PUT | `/sites/{id}` | Update site | Yes | DRH, Admin | 06 |
| DELETE | `/sites/{id}` | Delete site | Yes | DRH, Admin | 06 |
| GET | `/sites/{id}/summary` | Site summary (employees, vehicles, PMR) | Yes | DRH, DAF, Admin | 08 |

---

## 4. Employees (27.2)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/employees` | List (filters: site_id, is_pmr, quartier, shift, department, active) | Yes | DRH, Admin | 09 |
| GET | `/employees/{id}` | Get single employee | Yes | DRH, Admin, Self | 09 |
| POST | `/employees` | Create employee (inline transport_profile) | Yes | DRH, Admin | 09 |
| PUT | `/employees/{id}` | Update employee | Yes | DRH, Admin | 09 |
| DELETE | `/employees/{id}` | Soft-delete employee | Yes | DRH, Admin | 09 |
| POST | `/employees/upload` | Bulk CSV upload | Yes | DRH, Admin | 09 |
| POST | `/employees/geocode` | Geocode addresses | Yes | DRH, Admin | 09 |
| GET | `/employees/summary` | Summary with site/PMR breakdowns | Yes | DRH, Admin | 09 |

---

## 5. Employee Modal (27.3)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/employees/{id}/modal` | Get transport data | Yes | DRH, Admin | 15 |
| PUT | `/employees/{id}/modal` | Create/update modal data | Yes | DRH, Admin | 15 |
| DELETE | `/employees/{id}/modal` | Delete modal data | Yes | DRH, Admin | 15 |
| GET | `/modal/stats` | Global modal distribution | Yes | DRH, DAF, Admin | 15 |
| GET | `/modal/shift-analysis` | Modal shift analysis + disruption/weather | Yes | DRH, Admin | 17 |
| GET | `/modal/mobility-scores` | Mobility scores + group/timeslot aggregation | Yes | DRH, Admin | 17 |
| GET | `/modal/shadow-zones` | Shadow zone employees (no transport solution) | Yes | DRH, Admin | 17 |
| GET | `/modal/carpool-potential` | Carpool supply vs demand per site | Yes | DRH, Admin | 17 |

---

## 6. Employee Leave (27.4)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/leaves` | Create leave period | Yes | DRH, Admin | 12 |
| GET | `/leaves` | List (filters: employee_id, site_id, dates) | Yes | DRH, Admin | 12 |
| GET | `/leaves/{id}` | Get single leave | Yes | DRH, Admin | 12 |
| PUT | `/leaves/{id}` | Update leave | Yes | DRH, Admin | 12 |
| DELETE | `/leaves/{id}` | Delete leave | Yes | DRH, Admin | 12 |

---

## 7. Vehicles (27.5)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/vehicles` | List with pagination (filters: site_id, pmr, condition, motorization, zfe) | Yes | DRH, DAF, Admin | 20 |
| POST | `/vehicles` | Create vehicle | Yes | DRH, Admin | 20 |
| PUT | `/vehicles/{id}` | Update vehicle | Yes | DRH, Admin | 20 |
| DELETE | `/vehicles/{id}` | Delete vehicle | Yes | DRH, Admin | 20 |
| GET | `/vehicles/fleet-summary` | Fleet overview by type, condition, motorization, site | Yes | DRH, DAF, Admin | 20 |

---

## 8. Constraints (27.6)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/constraints` | List (optional category filter) | Yes | Admin, DRH | 29 |
| POST | `/constraints` | Create constraint | Yes | Admin | 29 |
| PUT | `/constraints/{id}` | Update constraint | Yes | Admin | 29 |
| DELETE | `/constraints/{id}` | Delete constraint | Yes | Admin | 29 |
| POST | `/constraints/bulk` | Bulk import | Yes | Admin | 29 |

---

## 9. Excel Import (27.7)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/import/excel` | Upload and import full template | Yes | DRH, Admin | 13 |
| POST | `/import/excel/preview` | Preview without importing | Yes | DRH, Admin | 13 |
| POST | `/import/excel/sheet` | Import single sheet | Yes | DRH, Admin | 13 |

---

## 10. Optimization (27.8)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/optimize` | Run optimization | Yes | DRH, Admin | 23 |
| GET | `/optimize/{id}` | Get result with metrics | Yes | DRH, DAF, Admin | 23 |
| GET | `/optimize/{id}/status` | Get progress | Yes | DRH, Admin | 23 |
| GET | `/optimize/latest/result` | Most recent optimization | Yes | DRH, DAF, Admin | 23 |
| GET | `/optimize/history/list` | Past runs | Yes | DRH, Admin | 23 |

---

## 11. Clustering (27.9)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/clusters/generate` | Run clustering (DBSCAN/KMeans/hierarchical) | Yes | DRH, Admin | 18 |
| GET | `/clusters` | Get saved clusters (filters: site_id, optimization_id) | Yes | DRH, Admin | 18 |
| GET | `/clusters/{id}` | Single cluster with employee details | Yes | DRH, Admin | 18 |
| POST | `/clusters/generate-with-zones` | Clustering + meeting zone optimization | Yes | DRH, Admin | 19 |

---

## 12. Vehicle Assignment (27.10)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/vehicle-assignments/assign` | Assign vehicles to clusters | Yes | DRH, Admin | 21 |
| POST | `/vehicle-assignments/split-cluster/{id}` | Split cluster | Yes | DRH, Admin | 21 |
| POST | `/vehicle-assignments/merge-clusters` | Merge clusters | Yes | DRH, Admin | 21 |

---

## 13. Routes (27.11)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/routes` | Get routes (filters: site_id, optimization_id, vehicle_id) | Yes | DRH, Admin, Operateur | 22 |
| GET | `/routes/{id}` | Single route with geometry | Yes | DRH, Admin, Operateur | 22 |

---

## 14. Weather (27.12)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/weather/{site_id}` | Get stored forecasts | Yes | DRH, Admin | 26 |
| POST | `/weather/{site_id}/refresh` | Refresh from provider | Yes | DRH, Admin | 26 |
| POST | `/weather/refresh-all` | Refresh all sites | Yes | Admin | 26 |
| GET | `/weather/{site_id}/suggestions` | Scenario suggestions | Yes | DRH, Admin | 26 |

---

## 15. Scenarios (27.13)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/scenarios/simulate` | Run scenario | Yes | DRH, Admin | 27 |
| GET | `/scenarios` | List scenarios | Yes | DRH, DAF, Admin | 27 |
| GET | `/scenarios/{id}` | Get scenario | Yes | DRH, DAF, Admin | 27 |
| DELETE | `/scenarios/{id}` | Delete scenario | Yes | DRH, Admin | 27 |
| POST | `/scenarios/compare` | Compare 2+ scenarios | Yes | DRH, DAF, Admin | 27 |

---

## 16. Financial Engineering (27.14)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/financial/scenarios` | Create financial scenario | Yes | DRH, DAF | 31 |
| GET | `/financial/scenarios` | List scenarios | Yes | DRH, DAF, Admin | 31 |
| GET | `/financial/scenarios/{id}` | Get with results | Yes | DRH, DAF, Admin | 31 |
| PUT | `/financial/scenarios/{id}` | Update scenario | Yes | DRH, DAF | 31 |
| DELETE | `/financial/scenarios/{id}` | Delete scenario | Yes | DRH, DAF | 31 |
| POST | `/financial/tco/calculate` | Calculate TCO | Yes | DRH, DAF | 32 |
| POST | `/financial/roi/calculate` | Calculate ROI | Yes | DRH, DAF | 33 |
| POST | `/financial/compare` | Compare investment models | Yes | DRH, DAF | 34 |
| GET | `/financial/vehicle-references` | Vehicle reference catalog | Yes | DRH, DAF, Admin | 31 |
| POST | `/financial/export/daf` | DAF-compatible export | Yes | DAF, Admin | 38 |

---

## 17. Journey Valorization (27.15)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/content` | Create content | Yes | DRH, Admin | 67 |
| GET | `/content` | List content | Yes | DRH, Admin | 67 |
| GET | `/content/{id}` | Get content | Yes | DRH, Admin | 67 |
| PUT | `/content/{id}` | Update content | Yes | DRH, Admin | 67 |
| DELETE | `/content/{id}` | Delete content | Yes | DRH, Admin | 67 |
| POST | `/content/{id}/publish` | Publish content | Yes | DRH, Admin | 67 |
| GET | `/content/feed` | Personalized feed (mobile) | Yes | Salarie | 69 |
| GET | `/content/{id}/engagement` | Engagement metrics | Yes | DRH, Admin | 69 |
| GET | `/content/analytics` | Aggregate analytics | Yes | DRH, Admin | 75 |
| POST | `/surveys/{id}/respond` | Submit survey response | Yes | Salarie | 72 |
| GET | `/training/completions` | Training completion records | Yes | DRH, Admin | 74 |
| POST | `/training/sync-lms` | Trigger LMS sync | Yes | Admin | 74 |
| GET | `/valorization/metrics` | Journey valorization KPIs | Yes | DRH, DAF, Admin | 76 |

---

## 18. RTI (27.16)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/rti/vehicle-position` | Update vehicle position | Yes | System/Operator | 58 |
| GET | `/rti/vehicle-position/{vehicle_id}` | Current position | Yes | DRH, Salarie, Operateur | 58 |
| GET | `/rti/stop/{stop_id}/eta` | ETA for next vehicle | Yes | Salarie | 58 |
| GET | `/rti/compliance` | RTI compliance metrics | Yes | DRH, Admin | 58 |
| GET | `/rti/risk-stops` | List risk-scored stops | Yes | DRH, Admin | 57 |
| PUT | `/rti/risk-stops/{id}` | Update risk assessment | Yes | DRH, Admin | 57 |
| GET | `/rti/config/{site_id}` | Get RTI config | Yes | DRH, Admin | 59 |
| PUT | `/rti/config/{site_id}` | Update RTI config | Yes | DRH, Admin | 59 |

---

## 19. Security (27.17)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/security/questionnaire` | Submit questionnaire | Yes | Salarie | 61 |
| GET | `/security/questionnaire/{employee_id}` | Get latest | Yes | DRH, Admin, Self | 61 |
| GET | `/security/scores` | Get scores (filters) | Yes | DRH, Admin | 62 |
| GET | `/security/scores/{employee_id}` | Individual score | Yes | DRH, Admin, Self | 62 |
| GET | `/security/risk-map` | Risk map data | Yes | DRH, Admin | 64 |
| POST | `/security/emergency` | Trigger emergency | Yes | Salarie | 66 |
| GET | `/security/emergency/history` | Alert history | Yes | DRH, Admin | 66 |
| PUT | `/security/emergency/{id}/resolve` | Resolve alert | Yes | DRH, Admin | 66 |

---

## 20. SIRH Sync (27.19)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/sirh/connections` | Configure connection | Yes | DRH, Admin | 77 |
| GET | `/sirh/connections` | List connections | Yes | DRH, Admin | 77 |
| PUT | `/sirh/connections/{id}` | Update config | Yes | DRH, Admin | 77 |
| DELETE | `/sirh/connections/{id}` | Remove connection | Yes | Admin | 77 |
| POST | `/sirh/sync/{connection_id}` | Trigger sync | Yes | DRH, Admin | 77 |
| GET | `/sirh/sync/status` | Sync status/history | Yes | DRH, Admin | 81 |
| GET | `/sirh/sync/conflicts` | Unresolved conflicts | Yes | DRH, Admin | 81 |
| PUT | `/sirh/sync/conflicts/{id}/resolve` | Resolve conflict | Yes | DRH, Admin | 81 |

---

## 21. Mobile (27.20)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| POST | `/trips/book` | Book a trip | Yes | Salarie, DRH | 54 |
| PUT | `/trips/{id}` | Modify booking | Yes | Salarie | 54 |
| DELETE | `/trips/{id}` | Cancel booking | Yes | Salarie | 54 |
| GET | `/trips/my` | My trip history | Yes | Salarie | 54 |
| GET | `/trips/upcoming` | Upcoming booked trips | Yes | Salarie | 54 |
| POST | `/devices/register` | Register for push | Yes | Salarie | 54 |
| DELETE | `/devices/{token}` | Unregister device | Yes | Salarie | 54 |
| GET | `/mobile/offline-manifest` | Offline data package | Yes | Salarie | 54 |

---

## 22. Export & Reports (27.21)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/export/pdf` | PDF driver sheets | Yes | DRH, Admin | 30 |
| GET | `/export/excel` | Multi-sheet Excel | Yes | DRH, Admin | 30 |
| GET | `/export/csv/stops` | CSV stop order | Yes | DRH, Admin | 30 |
| GET | `/export/csv/employees` | CSV employee assignments | Yes | DRH, Admin | 30 |
| GET | `/export/geojson` | GeoJSON FeatureCollection | Yes | DRH, Admin | 30 |
| GET | `/export/modal-report` | Modal analysis report | Yes | DRH, Admin | 42 |
| GET | `/export/fleet-report` | Fleet utilization | Yes | DRH, Admin | 42 |
| GET | `/export/volunteer-report` | Volunteer driver report | Yes | DRH, Admin | 42 |
| POST | `/export/financial/tco` | TCO report | Yes | DAF, Admin | 38 |
| POST | `/export/financial/roi` | ROI report | Yes | DAF, Admin | 38 |
| POST | `/export/financial/daf` | DAF ERP export | Yes | DAF, Admin | 38 |
| POST | `/export/rse/dpef` | DPEF environmental report | Yes | DRH, Admin | 41 |
| POST | `/export/sizing-plan` | Operator sizing plan | Yes | DRH, Admin | 82 |
| POST | `/export/hr-mobility` | HR mobility report | Yes | DRH, Admin | 42 |
| GET | `/export/history` | Generated report history | Yes | DRH, DAF, Admin | 43 |

---

## 23. Dashboard KPIs (27.22)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/kpis/operations` | Operations KPIs | Yes | DRH, Admin | 25 |
| GET | `/kpis/hr` | HR dashboard KPIs | Yes | DRH, DAF, Admin | 39 |
| GET | `/kpis/rse` | RSE KPIs | Yes | DRH, DAF, Admin | 41 |
| GET | `/kpis/rti` | RTI compliance KPIs | Yes | DRH, Admin | 60 |
| GET | `/kpis/security` | Security metrics | Yes | DRH, Admin | 64 |
| GET | `/kpis/financial` | Financial KPIs | Yes | DAF, Admin | 35 |
| GET | `/kpis/valorization` | Valorization KPIs | Yes | DRH, DAF, Admin | 76 |
| POST | `/kpis/snapshot` | Save KPI snapshot | Yes | Admin | 44 |

---

## 24. Settings (27.23)

| Method | Endpoint | Description | Auth | Roles | Session |
|--------|----------|-------------|------|-------|---------|
| GET | `/settings` | Get or create default optimization settings | Yes | Admin, DRH | 29 |
| PUT | `/settings` | Partial update optimization settings | Yes | Admin | 29 |

---

## WebSocket Endpoints

| Endpoint | Description | Auth | Session |
|----------|-------------|------|---------|
| `ws://localhost:8000/ws/rti/{vehicle_id}` | Vehicle position stream | JWT | 58 |
| `ws://localhost:8000/ws/optimization/{id}` | Optimization progress | JWT | 23 |

---

## Total Endpoint Count: ~125 endpoints across 24 groups
