# Session 18 — Clustering Engine

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-09|Session 09]]

> Previous: [[sessions/session-17|Session 17]] | Next: [[sessions/session-19|Session 19]]

## Complexity: High

## Objective
Implement the clustering engine using DBSCAN, KMeans, and hierarchical clustering with configurable parameters.

---

## Tasks

- [x] Create `backend/app/models/optimization.py` — Optimization, Cluster models
- [x] Create Alembic migration for optimization and cluster tables
- [x] Create `backend/app/services/clustering.py` — Clustering engine:
  - DBSCAN clustering (eps from meeting_radius, min_samples configurable)
  - KMeans clustering (k auto-determined or configurable)
  - Hierarchical clustering (scipy linkage)
  - Custom distance-based clustering (via configurable max_cluster_size splitting)
- [x] Implement per-site clustering (employees clustered within their site)
- [x] Implement PMR-aware clustering (flag PMR employees in clusters)
- [x] Implement configurable parameters:
  - Meeting radius (50m-5000m via eps_meters)
  - Max employees per cluster (auto-split via KMeans sub-clustering)
- [x] Calculate cluster centroids (geographic center)
- [x] Create `backend/app/schemas/optimization.py` — Pydantic schemas:
  - `ClusteringRequest` — site_id, algorithm, params
  - `ClusterResponse` — cluster with employees, centroid, PMR count
- [x] Create `backend/app/api/v1/clusters.py` — Endpoints:
  - POST `/clusters/generate` — Run clustering
  - GET `/clusters` — Get saved clusters (site_id filter)
  - GET `/clusters/{id}` — Single cluster with employees
- [x] Register clusters router
- [x] Create `backend/tests/test_clustering.py`

## Files to Create/Modify
- `backend/app/models/optimization.py` (create)
- `backend/app/services/clustering.py` (create)
- `backend/app/schemas/optimization.py` (create)
- `backend/app/api/v1/clusters.py` (create)
- `backend/app/models/__init__.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_clustering.py` (create)

## Tests
- [x] `test_dbscan_clustering` — Known data produces expected clusters
- [x] `test_kmeans_clustering` — Known data produces expected clusters
- [x] `test_hierarchical_clustering` — Produces valid clusters
- [x] `test_per_site_clustering` — Employees only clustered within their site
- [x] `test_pmr_flagging` — PMR employees flagged in cluster
- [x] `test_meeting_radius_effect` — Different radii produce different cluster counts
- [x] `test_max_cluster_size` — No cluster exceeds max employees
- [x] `test_centroid_calculation` — Centroid is geographic center
- [x] `test_empty_site_clustering` — No employees returns empty clusters
- [x] `test_generate_endpoint` — API generates and saves clusters
- [x] `test_get_clusters` — API returns saved clusters

## Test Results
- Tests written: 11
- Tests passing: 11
- Tests failing: 0
- Full suite: 88 passed

## Acceptance Criteria
- All 3 clustering algorithms produce valid results
- Per-site isolation works
- PMR employees flagged correctly
- Configurable radius affects cluster size
- Centroids are geographic centers of cluster members
- All 11 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
