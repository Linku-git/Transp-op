# Session 63 — Security-Constrained Pooling

> Previous: [[sessions/session-62|Session 62 — Security Scoring Engine]] | Next: [[sessions/session-64|Session 64 — Security Dashboard Frontend]]

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-18|Session 18]], [[sessions/session-62|Session 62]] completed
## Complexity: High

## Objective
Extend the clustering engine to incorporate security constraints as a third dimension alongside geographic proximity and shift compatibility, enforcing stricter rules during night hours including minimum group sizes and risk stop avoidance.

---

## Tasks
- [ ] Modify clustering engine to integrate security constraints:
  - Add security scores as weighted constraints in the clustering algorithm
  - Employees with higher risk scores receive priority grouping (not left alone)
  - Security weight configurable per site
- [ ] Implement night-hour shift rules (20h00-6h30):
  - No isolated stops allowed during night hours
  - Larger group minimums enforced at night stops
  - Minimum group size for night stops: configurable, default 3
  - All night stops must have lighting_score above minimum threshold
- [ ] Implement high-risk stop avoidance during night hours:
  - Stops flagged as critical (from Session 57) excluded from night routes
  - Alternative stop suggestions when critical stops are on a night route
  - Re-routing logic to bypass high-risk stops
- [ ] Implement priority vehicle assignment for night routes:
  - Night routes receive priority in vehicle allocation
  - Prefer vehicles with GPS tracking and communication equipment
- [ ] Implement three-dimension pooling:
  - Dimension 1: Geographic proximity (existing)
  - Dimension 2: Shift compatibility (existing)
  - Dimension 3: Security criteria (new)
  - Configurable weights for each dimension
  - Combined objective function balancing all three dimensions

## Files to Create/Modify
- `backend/app/services/clustering.py` (modify existing)
- `backend/app/services/security_constraints.py`
- `backend/app/services/night_routing.py`
- `backend/app/schemas/clustering.py` (add security parameters)
- `backend/app/models/clustering_config.py` (add security weights)

## Tests
- [ ] Test night pooling produces groups with minimum size >= configured minimum (default 3)
- [ ] Test critical risk stops are avoided in night-hour route generation
- [ ] Test alternative stops are suggested when critical stops are on night routes
- [ ] Test security weights affect cluster composition (higher-risk employees grouped together)
- [ ] Test three-dimension pooling produces valid clusters balancing all criteria
- [ ] Test night routes receive priority vehicle assignment
- [ ] Test isolated stops are excluded from night-hour clusters
- [ ] Test configurable weights change clustering behavior appropriately
- [ ] Test day-hour clusters are not affected by night-specific constraints

## Acceptance Criteria
- Clustering engine integrates security scores as weighted constraints
- Night-hour shifts enforce stricter rules: no isolated stops, minimum group size of 3
- High-risk stops are avoided during night hours with alternative routing
- Night routes receive priority in vehicle assignment
- Three-dimension pooling balances geographic, shift, and security criteria
- Configurable weights allow per-site tuning of all three dimensions
- Day-hour clustering remains unaffected by night-specific constraints
- All tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
