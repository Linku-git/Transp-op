# Session 49 — Trip Booking Screens

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-48|Session 48]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-48|Session 48]] | Next: [[sessions/session-50|Session 50]]

## Objective
Create the trip booking flow allowing employees to select a date, shift, and pickup point, review a summary, and confirm their booking via the backend API.

---

## Tasks
- [x] Create TripBookingScreen with full booking flow
- [x] Implement DatePickerStrip supporting today + 7 days (horizontal scroll, French day/month abbreviations)
- [x] Implement ShiftSelector populated from employee's site shifts (radio-style cards with times)
- [x] Display default assigned pickup point with a "Changer" option opening a bottom sheet picker
- [x] Create BookingSummaryCard showing selected date, shift, pickup point
- [x] Add confirm button (disabled until shift + pickup selected) to submit booking via POST `/trips/book`
- [x] Display cancellation policy notice ("Annulation possible jusqu'à 30 minutes avant le départ")
- [x] Integrate with TripBookingNotifier (Riverpod) for state management

## Files Created
- `mobile/lib/models/trip_booking.dart` — TripBooking, Shift, PickupPoint, BookingConfirmation models
- `mobile/lib/services/trip_service.dart` — TripService (getSiteShifts, getNearbyPickupPoints, bookTrip)
- `mobile/lib/providers/trip_booking_provider.dart` — TripBookingNotifier with state: date, shifts, pickup, submit
- `mobile/lib/widgets/date_picker_strip.dart` — Horizontal date strip (today+7), French abbreviations, selected highlight
- `mobile/lib/widgets/shift_selector.dart` — Radio-style shift cards with entry/exit times, loading/empty states
- `mobile/lib/widgets/pickup_point_picker.dart` — Pickup display card + bottom sheet picker with walking time
- `mobile/lib/widgets/booking_summary_card.dart` — Summary with date, shift, pickup in accent card
- `mobile/lib/screens/trips/trip_booking_screen.dart` — Full booking flow composing all widgets

## Files Modified
- `mobile/lib/config/routes.dart` — Replaced trips/book placeholder with real `TripBookingScreen`

## Tests
- Tests written: 30 (session 49)
- Tests passing: 142 (total)
- Tests failing: 0

### Test files:
- `test/models/trip_booking_test.dart` — TripBooking toJson (date format, coords), Shift fromJson, PickupPoint fromJson, BookingConfirmation defaults
- `test/providers/trip_booking_provider_test.dart` — State defaults, canConfirm logic, selectedShift lookup, activePickupPoint preference, copyWith
- `test/screens/trip_booking_screen_test.dart` — Title, date/shift sections, cancellation policy, confirm button, button disabled
- `test/widgets/date_picker_strip_test.dart` — Renders today, onDateSelected callback
- `test/widgets/shift_selector_test.dart` — Shifts render with times, onShiftSelected, loading, empty state
- `test/widgets/booking_summary_card_test.dart` — Header, shift info, pickup point display

## Implementation Notes
- **DatePickerStrip** uses static French day/month abbreviations (LUN-DIM, JAN-DÉC) to avoid `intl` locale initialization issues in tests
- **BookingSummaryCard** uses DD/MM/YYYY format instead of `DateFormat` for same reason
- **ShiftSelector** shows radio-button style with entry/exit time ranges
- **PickupPointPicker** uses `showModalBottomSheet` for point selection with walking time display
- **canConfirm** requires both `selectedShiftId` and `activePickupPoint` to be non-null
- **Cancellation policy** displayed as warning-colored info banner
- **Booking confirmation** shown via SnackBar with success color, then `context.pop()`

## Acceptance Criteria
- [x] Users can select a date from today up to 7 days in advance
- [x] Shift options loaded and displayed with entry/exit times
- [x] Default pickup point pre-selected and displayed with walking time
- [x] Users can change pickup point via bottom sheet picker
- [x] Summary card reflects all selections before confirmation
- [x] Confirm button submits to POST `/trips/book` (disabled until ready)
- [x] Cancellation policy notice clearly visible
- [x] Successful booking shows confirmation SnackBar
- [x] `flutter analyze` reports 0 issues
- [x] All 142 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[MOBILE_PAGES]] — Mobile screens
