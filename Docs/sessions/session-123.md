# Session 123 — ML Dashboard & Retraining UI

> Previous: [[sessions/session-122|Session 122 — Real-Time Operations Frontend]] | Next: [[sessions/session-124|Session 124 — Driver Portal (React)]]

## Phase: 8 — SOTREG Modules (M1-M8)
## Prerequisites: Sessions 116, 119, 120
## Complexity: Medium

## Objective
Build the ML operations dashboard for model monitoring, retraining triggers, and feature importance visualization. The dashboard provides a centralized view of all registered ML models (LSTM demand, RandomForest driver risk, IsolationForest maintenance), their versions and metrics, and allows operators to trigger retraining and compare old vs new model performance.

---

## Tasks

- [x] **Create MLDashboardPage with tabs:**
  - Tab 1: Models (registry overview)
  - Tab 2: Features (importance and distributions)
  - Tab 3: Retraining (pipeline control)
  - Page header with last-updated timestamp and model health summary
- [x] **Create ModelRegistryTable component:**
  - List all models with columns: name, version, status (staging/production/retired), metrics
  - Promote button (staging -> production)
  - Retire button (production -> retired)
  - Version history expandable per model
  - Status badge color: staging=blue, production=green, retired=gray
- [x] **Create ModelMetricsChart component:**
  - Recharts LineChart showing metric evolution across versions
  - Support multiple metrics (MAE, RMSE, accuracy, F1)
  - Version selector to compare specific versions
  - Threshold line showing acceptable metric range
- [x] **Create FeatureImportanceChart component:**
  - Horizontal BarChart for RF/IF feature importances
  - Sorted descending by importance value
  - Color gradient from high (primary blue) to low (gray)
  - Model selector to switch between RF and IF features
- [x] **Create RetrainingPanel component:**
  - Trigger retraining button per model type
  - Progress indicator (Celery task status polling)
  - Side-by-side comparison: old model metrics vs new model metrics
  - Auto-promote toggle with improvement threshold input
  - Retraining history log with timestamps and outcomes
- [x] **Create PredictionMonitor component:**
  - Live chart showing prediction accuracy vs actual values
  - Rolling window (last 24h / 7d / 30d)
  - Drift detection indicator (when accuracy drops below threshold)
  - Model-specific: demand forecast MAE, driver risk accuracy
- [x] **Extend sotreg.ts API client:**
  - fetchModelRegistry(), promoteModel(), retireModel()
  - triggerRetraining(), getRetrainingStatus()
  - fetchFeatureImportance(), fetchPredictionAccuracy()
- [x] **Frontend tests:**
  - Component render tests for all 6 components

## Files to Create/Modify
- `frontend/src/pages/sotreg/MLDashboardPage.tsx` (create)
- `frontend/src/components/sotreg/ModelRegistryTable.tsx` (create)
- `frontend/src/components/sotreg/ModelMetricsChart.tsx` (create)
- `frontend/src/components/sotreg/FeatureImportanceChart.tsx` (create)
- `frontend/src/components/sotreg/RetrainingPanel.tsx` (create)
- `frontend/src/components/sotreg/PredictionMonitor.tsx` (create)
- `frontend/src/api/sotreg.ts` (extend)
- `frontend/src/pages/sotreg/__tests__/MLDashboardPage.test.tsx` (create)

## Tests
- [x] MLDashboardPage renders with 3 tabs (Models, Features, Retraining)
- [x] ModelRegistryTable renders model rows with version and status
- [x] ModelRegistryTable promote button triggers API call
- [x] ModelMetricsChart renders LineChart with version data
- [x] FeatureImportanceChart renders horizontal bars sorted by importance
- [x] RetrainingPanel renders trigger button and progress indicator
- [x] PredictionMonitor renders rolling accuracy chart
- [x] Tab switching displays correct panel content

## Test Results
- Tests written: 8
- Tests passing: 8
- Tests failing: 0
- Coverage: all acceptance criteria met

## Acceptance Criteria
- ML dashboard displays all registered models with versions and status
- Model promotion and retirement workflows function correctly
- Metrics chart shows metric evolution across model versions
- Feature importance chart displays ranked features for RF and IF models
- Retraining can be triggered from UI with progress tracking
- Prediction monitor shows rolling accuracy with drift detection
- All 8 tests pass

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
