# Session 125 — Contractor Dashboard (Dash+Plotly)

> Previous: [[sessions/session-124|Session 124 — Driver Portal (React)]] | Next: [[sessions/session-126|Session 126 — Observability Stack (Prometheus+Grafana+Loki)]]

## Phase: 8 — SOTREG Modules (M1-M8)
## Prerequisites: Sessions 82-84 (Operator model), Session 115 (roles)
## Complexity: High

## Objective
Build the contractor dashboard as a separate Dash+Plotly micro-frontend with SLA compliance tracking, financial reconciliation in MAD currency, fleet status monitoring, and KPI visualization. The dashboard authenticates against the Transpop API using JWT tokens and runs as an independent Docker service on port 8050.

---

## Tasks

- [x] **Create contractor-dashboard/ with Dash application:**
  - Dash 2.x with Plotly for interactive charts
  - Multi-page layout with dash-bootstrap-components (DARKLY theme)
  - JWT authentication flow (login page -> token storage)
  - Session management with flask-caching
  - Responsive layout for desktop and tablet
- [x] **KPI page:**
  - trips_completed: total and trend (Plotly indicator + sparkline)
  - on_time_pct: OTP percentage gauge (target >95%)
  - satisfaction: average satisfaction score (1-5 scale)
  - utilization: fleet utilization percentage
  - Date range selector (today/week/month/quarter)
  - KPI cards with delta vs previous period
- [x] **SLA compliance page:**
  - OTP vs target line chart (daily over 30 days)
  - Penalty calculation: 500 MAD per % below 95% target
  - Penalty amount in MAD based on contract terms
  - Trend analysis with Plotly scatter + OLS trendline
  - Export SLA report as CSV
- [x] **Financial reconciliation page:**
  - Invoiced vs actual trips DataTable (grouped by ligne)
  - Payment status per invoice: paid (green), pending (amber), disputed (red) with conditional formatting
  - Monthly revenue bar chart in MAD
  - Discrepancy highlighting (invoiced != actual)
  - Total amounts in MAD with currency formatting
- [x] **Fleet status page:**
  - Vehicle positions map (Plotly scattermapbox centered on Casablanca 33.57, -7.59)
  - Vehicle list with status: active/maintenance/idle
  - Maintenance schedule calendar
  - Availability percentage doughnut chart per vehicle type
- [x] **Integrate with Transpop API:**
  - httpx client with JWT bearer token
  - API endpoints: /sotreg/operators, /sotreg/lignes, /rti/vehicles
  - Token refresh on 401 response
  - Fallback demo data when API unavailable
- [x] **Docker service in docker-compose.yml:**
  - Dockerfile for contractor-dashboard
  - Port 8050, environment variables for API URL and secrets
  - Health check endpoint
  - Volume mount for static assets
- [x] **Tests:**
  - 26 tests across 4 files (test_kpi, test_sla, test_financial, test_api_client)

## Files to Create/Modify
- `contractor-dashboard/app.py` (create)
- `contractor-dashboard/pages/kpi.py` (create)
- `contractor-dashboard/pages/sla.py` (create)
- `contractor-dashboard/pages/financial.py` (create)
- `contractor-dashboard/pages/fleet.py` (create)
- `contractor-dashboard/services/api_client.py` (create)
- `contractor-dashboard/services/auth.py` (create)
- `contractor-dashboard/components/kpi_card.py` (create)
- `contractor-dashboard/Dockerfile` (create)
- `contractor-dashboard/requirements.txt` (create)
- `docker-compose.yml` (modify — add contractor-dashboard service)
- `contractor-dashboard/tests/test_kpi.py` (create)
- `contractor-dashboard/tests/test_sla.py` (create)
- `contractor-dashboard/tests/test_financial.py` (create)
- `contractor-dashboard/tests/test_api_client.py` (create)

## Tests
- [x] Dash app initializes and serves on port 8050
- [x] Login page authenticates and stores JWT token
- [x] KPI page renders all 4 KPI cards with mock data
- [x] KPI delta calculation shows correct change vs previous period
- [x] SLA page renders OTP line chart with target threshold
- [x] Penalty calculation matches expected MAD amount
- [x] Financial page renders invoiced vs actual trips table
- [x] Discrepancy highlighting flags mismatched trip counts
- [x] Fleet page renders vehicle positions on map
- [x] API client handles 401 with token refresh
- [x] Health check endpoint returns 200
- [x] MAD currency formatting displays correctly (e.g., 15,000.00 MAD)

## Test Results
- Tests written: 26 (12 logical groups)
- Tests passing: 26
- Tests failing: 0
- Coverage: all acceptance criteria met

## Acceptance Criteria
- Contractor dashboard runs as independent Dash application on port 8050
- JWT authentication integrates with Transpop backend API
- KPI page displays trips, OTP, satisfaction, and utilization with trends
- SLA compliance tracks OTP vs target with penalty calculations in MAD
- Financial reconciliation compares invoiced vs actual trips with payment status
- Fleet status shows vehicle positions and maintenance schedule
- Docker service is configured in docker-compose.yml with health check
- All 12 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v5.0
- [[ARCHITECTURE]] — System architecture
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[DATABASE_SCHEMA]] — Database tables
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
