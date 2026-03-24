# Session 66 — Emergency Alert System

> Previous: [[sessions/session-65|Session 65 — Mobile Night Mode & Emergency]] | Next: [[sessions/session-67|Session 67 — Content Model & CRUD API]]

## Phase: 4 — Security & RTI
## Prerequisites: [[sessions/session-04|Session 04]], [[sessions/session-65|Session 65]] completed
## Complexity: Medium

## Objective
Build the backend emergency alert system with alert triggering, multi-channel responder notification, real-time GPS location sharing, resolution tracking, and full audit logging.

---

## Tasks
- [ ] Create `EmergencyAlert` model with fields:
  - `id` — primary key
  - `employee_id` — foreign key to employee
  - `triggered_at` — timestamp of alert activation
  - `location` — PostGIS geometry point (employee GPS coordinates at trigger time)
  - `alert_type` — enum (panic, medical, vehicle_incident, other)
  - `responders_notified` — JSON array of notified responder IDs and notification timestamps
  - `resolved_at` — timestamp of resolution (null if unresolved)
  - `resolution_notes` — text, notes from resolver
  - `created_at` / `updated_at` — timestamps
- [ ] Create Alembic migration for EmergencyAlert
- [ ] Implement `POST /security/emergency` — trigger emergency alert (from mobile app):
  - Accept employee_id, location coordinates, alert_type
  - Create EmergencyAlert record
  - Initiate alert routing to responders
- [ ] Implement alert routing:
  - Notify site security contact (based on employee's site)
  - Notify admin users
  - Notify emergency services (configurable per alert type)
  - Record all notification deliveries in responders_notified
- [ ] Implement push notification to responders:
  - Send push notification with alert details and employee location
  - Include direct link to employee's live location
- [ ] Implement location sharing:
  - Employee GPS coordinates shared with responders in real-time
  - Continuous location updates until alert is resolved
- [ ] Implement `GET /security/emergency/history` — retrieve alert history log:
  - Filterable by date range, alert_type, resolution status
  - Paginated results
- [ ] Implement `PUT /security/emergency/{id}/resolve` — resolve an active alert:
  - Set resolved_at timestamp
  - Accept resolution_notes
  - Stop location sharing
- [ ] All emergency activations logged for audit:
  - Log trigger, all notifications sent, resolution actions
  - Immutable audit trail

## Files to Create/Modify
- `backend/app/models/emergency_alert.py`
- `backend/app/schemas/emergency_alert.py`
- `backend/app/api/endpoints/emergency.py`
- `backend/app/services/emergency_routing.py`
- `backend/app/services/emergency_notification.py`
- `backend/app/services/location_sharing.py`
- `backend/alembic/versions/xxx_create_emergency_alert.py`
- `backend/app/api/router.py` (register new endpoints)

## Tests
- [ ] Test emergency trigger creates EmergencyAlert record with correct fields
- [ ] Test alert routing notifies site security contact
- [ ] Test alert routing notifies admin users
- [ ] Test responders_notified JSON is populated with notification timestamps
- [ ] Test push notification is sent to responders with alert details
- [ ] Test location sharing sends employee GPS to responders
- [ ] Test resolve endpoint sets resolved_at and stops location sharing
- [ ] Test resolution_notes are stored
- [ ] Test GET /security/emergency/history returns filtered paginated results
- [ ] Test all activations create immutable audit log entries
- [ ] Test concurrent alerts from different employees are handled independently

## Acceptance Criteria
- EmergencyAlert model exists with all specified fields and migration
- POST /security/emergency triggers alert and initiates responder notification
- Alert routing notifies site security, admins, and emergency services as configured
- Push notifications are sent to all designated responders
- Employee GPS location is shared with responders until alert resolution
- GET /security/emergency/history returns filterable, paginated alert log
- PUT /security/emergency/{id}/resolve closes the alert and stops location sharing
- All activations are logged in an immutable audit trail
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
