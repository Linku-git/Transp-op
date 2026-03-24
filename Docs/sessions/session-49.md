# Session 49 — Trip Booking Screens

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-48|Session 48]]
## Complexity: Medium
> Previous: [[sessions/session-48|Session 48]] | Next: [[sessions/session-50|Session 50]]

## Objective
Create the trip booking flow allowing employees to select a date, shift, and pickup point, review a summary, and confirm their booking via the backend API.

---

## Tasks
- [ ] Create TripBookingScreen with full booking flow
- [ ] Implement date picker supporting today + 7 days
- [ ] Implement shift selector populated from employee's site shifts
- [ ] Display default assigned pickup point with a "Change" option opening a map picker
- [ ] Create summary card showing selected date, shift, pickup point, and estimated times
- [ ] Add confirm button to submit booking
- [ ] Display cancellation policy notice on booking screen
- [ ] Integrate with backend API: POST `/trips/book`

## Files to Create/Modify
- `mobile/lib/screens/trip_booking_screen.dart`
- `mobile/lib/widgets/date_picker_strip.dart`
- `mobile/lib/widgets/shift_selector.dart`
- `mobile/lib/widgets/pickup_point_picker.dart`
- `mobile/lib/widgets/booking_summary_card.dart`
- `mobile/lib/services/trip_service.dart`
- `mobile/lib/providers/trip_booking_provider.dart`
- `mobile/lib/models/trip_booking.dart`

## Tests
- [ ] Booking flow renders all steps correctly
- [ ] Date picker only allows today through 7 days ahead
- [ ] Shift selector displays employee's available shifts
- [ ] Pickup point map picker opens and allows selection
- [ ] Summary card reflects all selected options
- [ ] API call to POST `/trips/book` is made with correct payload
- [ ] Success confirmation is shown after booking
- [ ] Error state is handled gracefully

## Acceptance Criteria
- Users can select a date from today up to 7 days in advance
- Shift options are loaded from the employee's assigned site shifts
- Default pickup point is pre-selected and displayed
- Users can change pickup point via an interactive map picker
- Summary card accurately reflects all booking selections before confirmation
- Confirm button submits booking to POST `/trips/book`
- Cancellation policy notice is clearly visible
- Successful booking shows confirmation and navigates back
- Invalid or past dates are rejected with clear feedback

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
