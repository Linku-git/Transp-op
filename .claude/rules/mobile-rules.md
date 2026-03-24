# Mobile Rules (Flutter/Dart)

## File Structure
- Screens: `mobile/lib/screens/<flow>/` — full screens
- Widgets: `mobile/lib/widgets/` — reusable widgets
- Models: `mobile/lib/models/` — data models
- Services: `mobile/lib/services/` — API, auth, push, location
- Providers: `mobile/lib/providers/` — Riverpod state providers

## Conventions
- Dart strong typing (no `dynamic` unless justified)
- Riverpod for state management
- GoRouter for navigation
- Google Maps for Flutter for all map displays
- Hive for key-value offline storage, SQLite for relational offline queries
- Firebase FCM for push notifications
- Active-only geolocation (never background tracking — RGPD compliance)
- Support Light + Dark (Night Mode) themes
- Localization: French (primary), English

## Offline-First
- Cache critical data locally (see `Docs/LOCAL_MOBILE_FUNCTIONALITY.md`)
- Degrade gracefully when offline
- Show cached data with staleness indicator
- Queue mutations for sync when connection returns

## Testing
- Test directory: `mobile/test/` mirroring `lib/` structure
- Test naming: `<widget>_test.dart`
- Widget tests for all screens
