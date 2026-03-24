# Session 26 — Weather API Integration

## Phase: 1 — MVP Core
## Prerequisites: [[sessions/session-06|Session 06]]

> Previous: [[sessions/session-25|Session 25]] | Next: [[sessions/session-27|Session 27]]

## Complexity: Low

## Objective
Integrate weather API (OpenWeatherMap) for 3-day forecasts per site and store forecast snapshots.

---

## Tasks

- [ ] Create `backend/app/models/weather.py` — WeatherForecast model
- [ ] Create Alembic migration for weather_forecast table
- [ ] Create `backend/app/services/weather.py` — Weather service:
  - Fetch 3-day forecast for site (lat/lng) from OpenWeatherMap API
  - Parse response into WeatherForecast records
  - Store snapshots for reproducibility
  - Generate scenario suggestions from forecast (rain -> suggest rain scenario)
- [ ] Create `backend/app/schemas/weather.py` — Pydantic schemas
- [ ] Create `backend/app/api/v1/weather.py` — Endpoints:
  - GET `/weather/{site_id}` — Get stored forecasts
  - POST `/weather/{site_id}/refresh` — Refresh from provider
  - POST `/weather/refresh-all` — Refresh all sites
  - GET `/weather/{site_id}/suggestions` — Scenario suggestions
- [ ] Register weather router
- [ ] Create `backend/tests/test_weather.py` (mock external API)

## Files to Create/Modify
- `backend/app/models/weather.py` (create)
- `backend/app/services/weather.py` (create)
- `backend/app/schemas/weather.py` (create)
- `backend/app/api/v1/weather.py` (create)
- `backend/tests/test_weather.py` (create)

## Tests
- [ ] `test_fetch_forecast` — Mocked API returns valid forecast
- [ ] `test_store_snapshot` — Forecast saved to database
- [ ] `test_get_forecasts` — Returns stored forecasts for site
- [ ] `test_scenario_suggestions` — Rain forecast suggests rain scenario
- [ ] `test_refresh_all_sites` — Refreshes all sites

## Acceptance Criteria
- Weather data fetched and stored per site
- 3-day forecast available for each site
- Scenario suggestions generated from forecast
- External API mocked in tests
- All 5 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
