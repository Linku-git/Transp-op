# Session 52 — Push Notification Service

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-45|Session 45]]
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-51|Session 51]] | Next: [[sessions/session-53|Session 53]]

## Objective
Set up Firebase Cloud Messaging, implement notification service with device registration, foreground/background handling, navigation routing, and a notification list screen.

## Tasks
- [x] FCM setup (firebase_messaging in pubspec from Session 45)
- [x] PushNotificationService: permission, token register, foreground/background/tap handling, token refresh
- [x] 5 notification types: rti_alert, route_change, weather, content, emergency
- [x] NotificationListScreen with date groups, swipe dismiss, "Tout lire", type icons, unread dots
- [x] NotificationNotifier with markAsRead, markAllAsRead, dismiss, groupedByDate
- [x] Notification channel config for Android
- [x] Token refresh + re-registration

## Files Created
- `mobile/lib/models/notification_item.dart`
- `mobile/lib/config/notification_channels.dart`
- `mobile/lib/services/push_notification_service.dart`
- `mobile/lib/providers/notification_provider.dart`
- `mobile/lib/screens/notifications/notification_list_screen.dart`

## Files Modified
- `mobile/lib/config/routes.dart`

## Tests
- Tests written: 15 (session 52)
- Tests passing: 206 (total)
- Tests failing: 0

## Acceptance Criteria
- [x] All 5 notification types handled
- [x] Grouped-by-date list with swipe dismiss
- [x] Token registration + refresh
- [x] `flutter analyze` 0 issues, 206 tests pass
