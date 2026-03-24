# Session 54 — Mobile API Backend

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-04|Session 04]], [[sessions/session-09|Session 09]]
## Complexity: Medium
> Previous: [[sessions/session-53|Session 53]] | Next: [[sessions/session-55|Session 55]]

## Objective
Create the backend API endpoints, database models, and migrations required to support mobile trip booking, device registration, push notifications, and offline data manifests.

---

## Tasks
- [ ] Create database models: TripBooking, DeviceRegistration, PushNotification
- [ ] Create Alembic migrations for new models
- [ ] Implement mobile API endpoints:
  - [ ] POST `/trips/book` — create a new trip booking
  - [ ] PUT `/trips/{id}` — modify an existing trip booking
  - [ ] DELETE `/trips/{id}` — cancel a trip booking
  - [ ] GET `/trips/my` — get current user's trips
  - [ ] GET `/trips/upcoming` — get upcoming trips for current user
  - [ ] POST `/devices/register` — register a device token for push notifications
  - [ ] DELETE `/devices/{token}` — unregister a device token
  - [ ] GET `/mobile/offline-manifest` — generate offline data manifest
- [ ] Implement trip validation: cancel/modify only allowed >30 minutes before departure
- [ ] Implement offline manifest generation: user profile, upcoming trips, site info, content

## Files to Create/Modify
- `backend/app/models/trip_booking.py`
- `backend/app/models/device_registration.py`
- `backend/app/models/push_notification.py`
- `backend/alembic/versions/xxx_add_mobile_models.py`
- `backend/app/api/routes/trips.py`
- `backend/app/api/routes/devices.py`
- `backend/app/api/routes/mobile.py`
- `backend/app/schemas/trip_booking.py`
- `backend/app/schemas/device_registration.py`
- `backend/app/services/trip_service.py`
- `backend/app/services/offline_manifest_service.py`

## Tests
- [ ] POST `/trips/book` creates a booking and returns confirmation
- [ ] PUT `/trips/{id}` modifies booking when >30 min before departure
- [ ] PUT `/trips/{id}` returns error when <30 min before departure
- [ ] DELETE `/trips/{id}` cancels booking when >30 min before departure
- [ ] DELETE `/trips/{id}` returns error when <30 min before departure
- [ ] GET `/trips/my` returns all trips for the authenticated user
- [ ] GET `/trips/upcoming` returns only future trips
- [ ] POST `/devices/register` stores device token
- [ ] DELETE `/devices/{token}` removes device token
- [ ] GET `/mobile/offline-manifest` returns complete manifest with profile, trips, site info, and content

## Acceptance Criteria
- All database models are created with proper relationships and constraints
- Alembic migrations run without errors
- Trip booking CRUD operations work correctly with proper validation
- 30-minute modification/cancellation window is enforced
- Device registration stores and removes FCM tokens
- Offline manifest includes user profile, upcoming trips, site information, and latest content
- All endpoints require authentication
- Proper error responses for invalid requests (400, 403, 404)
- API responses follow consistent schema patterns

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
