# Session 45 — Flutter Project Setup

## Phase: 3 — Mobile MVP
## Prerequisites: None (independent)
## Complexity: Medium
## Status: COMPLETE
## Date: 2026-04-08
> Previous: [[sessions/session-44|Session 44]] | Next: [[sessions/session-46|Session 46]]

## Objective
Initialize the Flutter mobile project in the `mobile/` directory with organized folder structure, core dependencies, theming, routing, and base widgets to establish the foundation for all mobile development. The app connects to the existing Transpop FastAPI backend hosted on Replit.

---

## Tasks
- [x] Initialize Flutter project in `mobile/` directory
- [x] Set up folder structure: `lib/config`, `models`, `services`, `providers`, `screens`, `widgets`, `utils`, `l10n`
- [x] Add dependencies in `pubspec.yaml`:
  - `google_maps_flutter` — maps and route display
  - `firebase_messaging` — push notifications
  - `hive` + `hive_flutter` — offline key-value storage
  - `sqflite` — offline structured queries
  - `dio` — HTTP client for Transpop API
  - `flutter_riverpod` — state management
  - `go_router` — declarative routing
  - `flutter_secure_storage` — JWT token storage
  - `connectivity_plus` — network state detection
  - `socket_io_client` — WebSocket for RTI real-time
- [x] Configure `dio` base URL to point to Replit production API: `https://transpop.replit.app/api/v1`
  - Uses `const` for base URL in `lib/config/api_config.dart`
  - Dev override: `http://localhost:8000/api/v1` via `--dart-define=API_BASE_URL=...`
- [x] Create app theme with light and dark/night mode support using design system colors
  - Primary: `#0058be` (Azure Blue) — matches web platform
  - Font: Inter via `google_fonts` package (runtime loading)
- [x] Define color scheme and typography in `lib/config/colors.dart` and `lib/config/typography.dart`
- [x] Create `routes.dart` with GoRouter configuration for all Phase 3 screens (17 routes)
- [x] Create base widgets: `AppScaffold`, `LoadingIndicator`, `ErrorWidget`, `EmptyState`
- [x] Create bottom navigation bar with 5 tabs: Home, Trips, Track, Content, Profile

## Files Created
- `mobile/pubspec.yaml` — 111 dependencies resolved
- `mobile/lib/main.dart` — App entry point with Riverpod + MaterialApp.router
- `mobile/lib/config/api_config.dart` — API base URL with `--dart-define` override
- `mobile/lib/config/theme.dart` — Light + dark Material 3 themes
- `mobile/lib/config/colors.dart` — Full color system (light, dark, night mode, semantic)
- `mobile/lib/config/typography.dart` — Inter font via google_fonts
- `mobile/lib/config/routes.dart` — GoRouter with 17 routes (ShellRoute + standalone)
- `mobile/lib/screens/placeholder_screen.dart` — Placeholder for unbuilt screens
- `mobile/lib/widgets/app_scaffold.dart` — Shell layout with bottom nav
- `mobile/lib/widgets/bottom_nav_bar.dart` — 5-tab NavigationBar (Accueil, Trajets, Suivi, Contenu, Profil)
- `mobile/lib/widgets/loading_indicator.dart` — Circular progress with optional message
- `mobile/lib/widgets/error_widget.dart` — Error display with retry button
- `mobile/lib/widgets/empty_state.dart` — Empty state with icon/title/subtitle/action

## Tests
- Tests written: 22
- Tests passing: 22
- Tests failing: 0

### Test files:
- `test/widget_test.dart` — App launch, MaterialApp present
- `test/config/api_config_test.dart` — Base URL, auth paths, timeouts, token keys
- `test/config/theme_test.dart` — Colors (primary #0058be, error, surfaces, dark, night, semantic)
- `test/widgets/bottom_nav_bar_test.dart` — 5 tabs render, onTap callback
- `test/widgets/base_widgets_test.dart` — LoadingIndicator, AppErrorWidget, EmptyState

## Implementation Notes
- **Flutter version:** 3.38.5 (Dart 3.10.4)
- **Hive pinned to ^2.2.3** (v4.0.0 does not exist on pub.dev)
- **Removed `riverpod_generator` and `hive_generator`** from dev_dependencies to avoid analyzer version conflicts; can be added later when needed
- **Inter font loaded at runtime** via `google_fonts` package (not bundled as assets) — avoids missing asset errors, works seamlessly
- **Night mode colors** pre-defined in `AppColors` for Session 65 (nightBackground, nightSurface, nightText, nightEmergency)

## Acceptance Criteria
- [x] Flutter project initializes and builds on iOS 15+ and Android API 29+
- [x] All dependencies resolve without conflicts (111 packages)
- [x] Folder structure follows the defined convention (8 directories)
- [x] Light and dark themes use `#0058be` primary color with Material 3
- [x] GoRouter handles all 17 defined routes
- [x] Bottom navigation bar displays 5 tabs and switches between them
- [x] `dio` is pre-configured with the Transpop API base URL
- [x] All base widgets render correctly
- [x] `flutter analyze` reports 0 issues
- [x] All 22 tests pass

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
