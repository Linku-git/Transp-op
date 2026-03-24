# Session 18 — Clustering Engine

## Phase: 1 — MVP Core (Module D)
## Prerequisites: [[sessions/session-09|Session 09]]

> Previous: [[sessions/session-17|Session 17]] | Next: [[sessions/session-19|Session 19]]

## Complexity: High

## Objective
Implement the clustering engine using DBSCAN, KMeans, and hierarchical clustering with configurable parameters.

---

## Tasks

- [ ] Create `backend/app/models/optimization.py` — Optimization, Cluster models
- [ ] Create Alembic migration for optimization and cluster tables
- [ ] Create `backend/app/services/clustering.py` — Clustering engine:
  - DBSCAN clustering (eps from meeting_radius, min_samples configurable)
  - KMeans clustering (k auto-determined or configurable)
  - Hierarchical clustering (scipy linkage)
  - Custom distance-based clustering
- [ ] Implement per-site clustering (employees clustered within their site)
- [ ] Implement PMR-aware clustering (flag PMR employees in clusters)
- [ ] Implement configurable parameters:
  - Meeting radius (200m / 500m / 1km)
  - Max walking distance
  - Max employees per cluster
- [ ] Calculate cluster centroids (geographic center)
- [ ] Create `backend/app/schemas/optimization.py` — Pydantic schemas:
  - `ClusteringRequest` — site_id, algorithm, params
  - `ClusterResponse` — cluster with employees, centroid, PMR count
- [ ] Create `backend/app/api/v1/clusters.py` — Endpoints:
  - POST `/clusters/generate` — Run clustering
  - GET `/clusters` — Get saved clusters (site_id filter)
  - GET `/clusters/{id}` — Single cluster with employees
- [ ] Register clusters router
- [ ] Create `backend/tests/test_clustering.py`

## Files to Create/Modify
- `backend/app/models/optimization.py` (create)
- `backend/app/services/clustering.py` (create)
- `backend/app/schemas/optimization.py` (create)
- `backend/app/api/v1/clusters.py` (create)
- `backend/app/models/__init__.py` (modify)
- `backend/app/api/v1/__init__.py` (modify)
- `backend/tests/test_clustering.py` (create)

## Tests
- [ ] `test_dbscan_clustering` — Known data produces expected clusters
- [ ] `test_kmeans_clustering` — Known data produces expected clusters
- [ ] `test_hierarchical_clustering` — Produces valid clusters
- [ ] `test_per_site_clustering` — Employees only clustered within their site
- [ ] `test_pmr_flagging` — PMR employees flagged in cluster
- [ ] `test_meeting_radius_effect` — Different radii produce different cluster counts
- [ ] `test_max_cluster_size` — No cluster exceeds max employees
- [ ] `test_centroid_calculation` — Centroid is geographic center
- [ ] `test_empty_site_clustering` — No employees returns empty clusters
- [ ] `test_generate_endpoint` — API generates and saves clusters
- [ ] `test_get_clusters` — API returns saved clusters

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
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Web pages
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
