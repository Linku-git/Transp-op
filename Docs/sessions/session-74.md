# Session 74 — LMS Integration

> Previous: [[sessions/session-73|Session 73 — Mobile Survey Interface]] | Next: [[sessions/session-75|Session 75 — Engagement Analytics Dashboard]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-69|Session 69]] completed
## Complexity: Medium

## Objective
Integrate with external Learning Management Systems to synchronize training catalogs and completion records bidirectionally.

---

## Tasks
- [ ] Create TrainingModule model with fields: content_id, lms_external_id, duration_minutes, is_mandatory, certification_name
- [ ] Generate Alembic migration for the TrainingModule table
- [ ] Build LMS connector for Cornerstone
- [ ] Build LMS connector for 360Learning
- [ ] Build LMS connector for TalentLMS
- [ ] Implement bidirectional sync: import training catalog from LMS
- [ ] Implement bidirectional sync: export completion records to LMS
- [ ] Implement POST `/training/sync-lms` endpoint to trigger sync
- [ ] Implement GET `/training/completions` endpoint for completion records
- [ ] Implement webhook handling for real-time completion updates from LMS

## Files to Create/Modify
- `backend/app/models/training_module.py`
- `backend/app/schemas/training_module.py`
- `backend/app/api/endpoints/training.py`
- `backend/app/services/lms/__init__.py`
- `backend/app/services/lms/base_connector.py`
- `backend/app/services/lms/cornerstone_connector.py`
- `backend/app/services/lms/360learning_connector.py`
- `backend/app/services/lms/talentlms_connector.py`
- `backend/app/services/lms/sync_service.py`
- `backend/app/api/endpoints/webhooks.py`
- `backend/alembic/versions/xxx_create_training_module_table.py`
- `backend/app/api/router.py`

## Tests
- [ ] Test training catalog import from each LMS connector
- [ ] Test completion record export to each LMS connector
- [ ] Test POST `/training/sync-lms` triggers full sync cycle
- [ ] Test GET `/training/completions` returns correct completion records
- [ ] Test webhook handling processes real-time completion updates
- [ ] Test TrainingModule model persists all fields correctly
- [ ] Test sync handles duplicate and updated records gracefully

## Acceptance Criteria
- TrainingModule model links content to external LMS training via lms_external_id
- Connectors for Cornerstone, 360Learning, and TalentLMS implement a common interface
- Catalog import creates or updates TrainingModule records from the LMS
- Completion export sends local completion data back to the LMS
- Sync endpoint triggers both import and export in a single call
- Webhooks process real-time completion events and update ContentDelivery records
- Completions endpoint returns records with employee, module, and completion details

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
