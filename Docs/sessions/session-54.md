# Session 54 — Mobile API Backend

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-04|Session 04]], [[sessions/session-09|Session 09]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08

## Objective
Create backend API endpoints, database models, and Alembic migration for mobile trip booking, FCM device registration, and offline data manifests.

## Tasks
- [x] Database models: TripBooking, DeviceRegistration, PushNotification
- [x] Alembic migration: j5k6l7m8n9o0_add_mobile_models.py (3 tables, 8 indexes)
- [x] Mobile API router (8 endpoints under /api/v1/mobile/)
- [x] 30-minute modification/cancellation window enforcement
- [x] Offline manifest generation (profile, trips, site, point_arrets)
- [x] Pydantic v2 schemas + services
- [x] Router registered in api/v1/__init__.py

## Files Created
- `backend/app/models/trip_booking.py` — TripBooking (tenant, employee, route, departure, status, seat, pickup, shift)
- `backend/app/models/device_registration.py` — DeviceRegistration (user, token, platform, last_seen)
- `backend/app/models/push_notification.py` — PushNotification (tenant, user, title, body, type, sent_at, read_at)
- `backend/alembic/versions/j5k6l7m8n9o0_add_mobile_models.py`
- `backend/app/schemas/trip_booking.py` — TripBookingCreate/Update/Response/ListResponse
- `backend/app/schemas/device_registration.py` — DeviceRegisterRequest/Response
- `backend/app/services/trip_booking_service.py` — create/update/cancel_booking, get_my/upcoming_trips
- `backend/app/services/offline_manifest_service.py` — generate_offline_manifest
- `backend/app/api/v1/mobile.py` — 8 endpoints
- `backend/tests/test_mobile_api.py` — 16 tests

## Files Modified
- `backend/app/models/__init__.py` — Added TripBooking, DeviceRegistration, PushNotification
- `backend/app/api/v1/__init__.py` — Registered mobile_router

## API Endpoints Added
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/mobile/trips/book | Create trip booking |
| PUT | /api/v1/mobile/trips/{id} | Modify booking (>30min) |
| DELETE | /api/v1/mobile/trips/{id} | Cancel booking (>30min) |
| GET | /api/v1/mobile/trips/my | All user trips |
| GET | /api/v1/mobile/trips/upcoming | Future confirmed trips |
| POST | /api/v1/mobile/devices/register | Register/update FCM token |
| DELETE | /api/v1/mobile/devices/{token} | Unregister FCM token |
| GET | /api/v1/mobile/offline-manifest | Offline data package |

## Tests
- Backend tests written: 16 | passing: 16
- Mobile tests: 223 passing (unchanged)
- Total: 239 tests passing, 0 failing
