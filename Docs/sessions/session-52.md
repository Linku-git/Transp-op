# Session 52 — Push Notification Service

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-45|Session 45]]
## Complexity: Medium
> Previous: [[sessions/session-51|Session 51]] | Next: [[sessions/session-53|Session 53]]

## Objective
Set up Firebase Cloud Messaging for both iOS and Android, implement a notification service that handles registration, incoming notifications, and navigation, and create a notification list screen.

---

## Tasks
- [ ] Set up Firebase Cloud Messaging (FCM) for iOS and Android platforms
- [ ] Create PushNotificationService:
  - [ ] Request notification permission from user
  - [ ] Register device token with backend via POST `/devices/register`
  - [ ] Handle incoming notifications in foreground
  - [ ] Handle incoming notifications in background
  - [ ] Navigate to relevant screen on notification tap
- [ ] Define notification types: `rti_alert`, `route_change`, `weather`, `content`, `emergency`
- [ ] Create NotificationListScreen with notifications grouped by date and swipe-to-dismiss
- [ ] Handle token refresh and re-registration

## Files to Create/Modify
- `mobile/lib/services/push_notification_service.dart`
- `mobile/lib/screens/notification_list_screen.dart`
- `mobile/lib/models/notification_item.dart`
- `mobile/lib/providers/notification_provider.dart`
- `mobile/lib/config/notification_channels.dart`
- `mobile/android/app/google-services.json`
- `mobile/ios/Runner/GoogleService-Info.plist`
- `mobile/lib/main.dart`

## Tests
- [ ] Device token is registered with backend on app launch
- [ ] Foreground notifications display correctly
- [ ] Background notifications are received and stored
- [ ] Tapping a notification navigates to the correct screen based on type
- [ ] NotificationListScreen renders notifications grouped by date
- [ ] Swipe-to-dismiss removes notification from list
- [ ] Token refresh triggers re-registration with backend

## Acceptance Criteria
- FCM is configured and functional on both iOS and Android
- Users are prompted for notification permission on first launch
- Device token is sent to backend via POST `/devices/register`
- Foreground notifications appear as in-app banners
- Background notifications appear in the system notification tray
- Tapping notifications routes to the appropriate screen (RTI, content, etc.)
- All 5 notification types (`rti_alert`, `route_change`, `weather`, `content`, `emergency`) are handled
- NotificationListScreen shows all received notifications grouped by date
- Notifications can be dismissed via swipe gesture
- Token refresh is handled seamlessly without user action

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
