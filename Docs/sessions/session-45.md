# Session 45 — Flutter Project Setup

## Phase: 3 — Mobile MVP
## Prerequisites: None (independent)
## Complexity: Medium
> Previous: [[sessions/session-44|Session 44]] | Next: [[sessions/session-46|Session 46]]

## Objective
Initialize the Flutter project with a well-organized folder structure, core dependencies, theming, routing, and base widgets to establish the foundation for all mobile development.

---

## Tasks
- [ ] Initialize Flutter project in `mobile/` directory
- [ ] Set up folder structure: `lib/config`, `models`, `services`, `providers`, `screens`, `widgets`, `utils`, `l10n`
- [ ] Add dependencies: `google_maps_flutter`, `firebase_messaging`, `hive`, `sqflite`, `dio`, `riverpod`, `go_router`, `flutter_secure_storage`, `connectivity_plus`, `socket_io_client`
- [ ] Create app theme with light and dark/night mode support
- [ ] Define color scheme and typography
- [ ] Create `routes.dart` with GoRouter configuration
- [ ] Create base widgets: `AppScaffold`, `LoadingIndicator`, `ErrorWidget`, `EmptyState`
- [ ] Create bottom navigation bar with 5 tabs: Home, Trips, Track, Content, Profile

## Files to Create/Modify
- `mobile/pubspec.yaml`
- `mobile/lib/main.dart`
- `mobile/lib/config/theme.dart`
- `mobile/lib/config/colors.dart`
- `mobile/lib/config/typography.dart`
- `mobile/lib/config/routes.dart`
- `mobile/lib/widgets/app_scaffold.dart`
- `mobile/lib/widgets/loading_indicator.dart`
- `mobile/lib/widgets/error_widget.dart`
- `mobile/lib/widgets/empty_state.dart`
- `mobile/lib/widgets/bottom_nav_bar.dart`

## Tests
- [ ] App launches without errors
- [ ] Navigation between all 5 tabs works correctly
- [ ] Light theme applies correctly
- [ ] Dark/night mode theme applies correctly

## Acceptance Criteria
- Flutter project initializes and builds successfully on both iOS and Android
- All dependencies resolve without conflicts
- Folder structure follows the defined convention
- Light and dark themes switch correctly
- GoRouter handles all defined routes
- Bottom navigation bar displays 5 tabs and switches between them
- All base widgets render correctly

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
- [[MOBILE_PAGES]]
- [[LOCAL_MOBILE_FUNCTIONALITY]]
- [[API_ENDPOINTS]]
