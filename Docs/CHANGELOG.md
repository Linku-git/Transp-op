# Transpop — Changelog

> All notable changes to this project are documented here.
> Format follows [Keep a Changelog](https://keepachangelog.com/).
> See also: [[PROGRESS]] | [[ROADMAP]]

---

## [Session-74] — 2026-04-09
### Added
- `TrainingModule` model: content_id, lms_provider, lms_external_id, duration_minutes, is_mandatory, certification_name, lms_metadata, last_synced_at
- Alembic migration `u6v7w8x9y0z1` with 4 indexes including unique (tenant, provider, external_id)
- `BaseLMSConnector` abstract class: fetch_catalog, export_completion, handle_webhook, test_connection
- `CornerstoneConnector`: Cornerstone OnDemand integration (OData API stubs)
- `Learning360Connector`: 360Learning integration (programs API stubs)
- `TalentLMSConnector`: TalentLMS integration (courses API stubs)
- Connector factory: `get_connector(provider)` with registry pattern
- `sync_service`: bidirectional sync (catalog import + completion export), full_sync, get_completions
- `POST /training/sync-lms` — trigger full bidirectional sync
- `GET /training/completions` — completion records with training module enrichment
- `POST /training/webhook/{provider}` — real-time LMS webhook processing
- `LMSCourse`, `LMSCompletion` standardized dataclasses
- 22 backend tests (model, schemas, connectors, webhooks)

## [Session-73] — 2026-04-09
### Added
- `SurveyScreen`: full survey interface with dynamic question rendering, progress bar, submit with validation
- 5 question type widgets: `RadioQuestion` (single choice), `CheckboxQuestion` (multiple choice), `TextQuestion`, `RatingQuestion` (1-5 stars), `SliderQuestion`
- `SurveyProgress` widget: question X of Y counter with linear progress bar
- `AnonymousIndicator` widget: visibility_off icon with anonymous notice
- Thank you confirmation screen after successful submission
- `SurveyData`, `SurveyQuestion`, `SurveyOption`, `SurveyAnswer` models
- `SurveyService`: API integration, Hive offline queue with auto-retry
- `SurveyScreenProvider`: Riverpod state for answers, validation, submission, offline queue
- Offline queue: stores responses in Hive when offline, `submitQueuedResponses()` on reconnect
- Route: `/content/survey/:id` → SurveyScreen (replaced placeholder)
- 25 mobile tests (models, question widgets, survey widgets, provider state)

## [Session-72] — 2026-04-09
### Added
- `Survey` model: content_id, title, description, questions (JSONB), response_count, is_anonymous, is_active
- `SurveyResponse` model: survey_id, employee_id (nullable for anonymous), responses (JSONB), submitted_at
- Alembic migration `t5u6v7w8x9y0` with 6 indexes across both tables
- 5 question types: single_choice, multiple_choice, text, rating (1-5), slider (0-100)
- `POST /surveys` — create survey linked to content
- `GET /surveys` — list surveys with pagination
- `GET /surveys/{id}` — get survey details
- `PUT /surveys/{id}` — update survey
- `POST /surveys/{id}/respond` — submit response with schema validation
- `GET /surveys/{id}/aggregation` — response aggregation (counts, averages, distributions, text responses)
- Response validation: type checking, range validation, option validation, required field enforcement
- Anonymous survey support (employee_id cleared automatically)
- Duplicate response prevention for non-anonymous surveys
- `SurveyService` with create, list, submit, validate, aggregate functions
- 26 backend tests (models, schemas, validation, aggregation)

## [Session-71] — 2026-04-09
### Added
- `TrainingPlayerScreen`: full-featured micro-training player with video/audio playback
- `TrainingMediaPlayer` widget: video_player integration with play/pause/seek/forward/backward controls, progress slider, audio visual mode
- `QuizSection` widget: multiple choice questions with answer selection, progress counter, submit button
- `ScoreDisplay` widget: pass/fail result with trophy/retry, score percentage, certificate link placeholder
- `TrainingContent` model: media_url, media_type, quiz questions, passing_score
- `QuizQuestion`, `QuizOption`, `QuizResult` models with score calculation
- `TrainingService`: API integration, Hive offline caching, quiz score submission
- `TrainingPlayerProvider`: Riverpod state for playback, quiz flow, time tracking
- Live time tracking display in app bar (seconds spent on training)
- Route: `/content/training/:id` → TrainingPlayerScreen (replaced placeholder)
- Added `video_player` and `chewie` Flutter packages
- 28 mobile tests (models, quiz widgets, score display, provider state)

## [Session-70] — 2026-04-09
### Added
- `ContentFeedScreen`: tabbed content feed with All/News/Training/Safety/Surveys filter chips
- `ContentDetailScreen`: full article view with rich text rendering, media display, auto "Mark as Read" on scroll completion
- `ContentCard` widget: title, snippet, type badge, date, media thumbnail, NEW badge, completion indicator
- `ContentTabs` widget: horizontal filter chip tabs for content types
- `OfflineIndicator` widget: banner for cached content display
- `FeedContent` model: extended content model with delivery/view/completion status, HTML snippet extraction
- `ContentFeedService`: API integration with Hive-based offline caching (30-min TTL)
- `ContentFeedProvider`: Riverpod state management with type filtering, offline fallback
- Route registration: `/content` → ContentFeedScreen, `/content/:id` → ContentDetailScreen
- 27 mobile tests (model, widgets, screen state, feed filtering)

## [Session-69] — 2026-04-08
### Added
- `ContentDelivery` model: content_id, employee_id, delivered_at, viewed_at, completed_at, quiz_score, time_spent_seconds
- Alembic migration `s4t5u6v7w8x9` with 4 indexes including unique content+employee constraint
- `GET /content/feed`: personalized feed filtered by employee's site, department, shift; excludes expired/unpublished
- `GET /content/{id}/engagement`: aggregated metrics (deliveries, views, completions, rates, avg quiz/time)
- `POST /content/{id}/deliver`: record delivery event
- `POST /content/{id}/view`: record view event
- `POST /content/{id}/complete`: record completion with optional quiz score and time spent
- `EngagementService` with get_or_create_delivery, record_delivery/view/completion, metrics aggregation, personalized feed
- Auto-delivery tracking when content appears in feed
- 18 backend tests (model, schemas, engagement metrics, feed personalization)

## [Session-68] — 2026-04-08
### Added
- Content management frontend: 4 CRUD pages (list, create, edit, detail)
- `ContentListPage`: table with type/status filters, pagination, publish/unpublish actions
- `ContentCreatePage`: form with rich text editor, audience targeting, media URL, schedule
- `ContentEditPage`: pre-filled form from existing content
- `ContentDetailPage`: read-only view with audience info, dates, engagement metrics placeholder
- `RichTextEditor` component: TipTap-based with bold, italic, lists, headings toolbar
- `AudienceTargeting` component: multi-select for sites, departments, shifts with chip UI
- `ContentForm` shared component with validation and preview button
- Zustand store (`contentStore`), API client, TypeScript types for content module
- Sidebar navigation: "Contenu" added to Outils group
- Routes: /content, /content/new, /content/:id, /content/:id/edit
- 26 frontend tests (6 test files, all passing)

## [Session-67] — 2026-04-08 (Phase 5 Start)
### Added
- `Content` model: title, body (rich text), content_type (news/training/safety/survey), media_url, JSONB audience targeting (sites/departments/shifts), published_at, expires_at, is_active
- Alembic migration `r3s4t5u6v7w8` with 4 indexes
- CRUD API: POST/GET/GET{id}/PUT/DELETE + POST /content/{id}/publish
- `ContentService` with create, list (filtered+paginated), get, publish functions
- Audience targeting: JSONB contains filtering by site_id
- 12 backend tests (model, schemas, audience targeting)

## [Session-66] — 2026-04-08 (Phase 4 Complete!)
### Added
- **Emergency Alert System**: full backend for emergency alert lifecycle
- `EmergencyAlert` model: PostGIS location (GIST index), alert_type (panic/medical/vehicle_incident/other), responders_notified JSONB, resolution tracking
- `POST /security/emergency` — trigger alert, auto-route to responders, start GPS location sharing
- `PUT /security/emergency/{id}/resolve` — close alert, stop location sharing, store resolution notes
- `GET /security/emergency/history` — paginated + filterable alert history log
- Emergency routing service: panic→emergency_services+site_security+admin, medical→medical_service+site_security+admin, other→site_security+admin
- Location sharing service: start/update/stop with active session tracking
- Emergency notification stubs (push + SMS) ready for Firebase/Twilio integration
- Alembic migration `q2r3s4t5u6v7` with 4 indexes including GIST spatial
- 18 backend tests (model, schemas, routing, location sharing)

### Phase 4 — Security & RTI: COMPLETE (10/10 sessions)

## [Session-65] — 2026-04-08
### Added
- **Mobile Night Mode**: `NightModeNotifier` (Riverpod) with auto/manual/off preferences, 1-minute re-evaluation timer, persisted via flutter_secure_storage
- **EmergencyScreen**: full red overlay (#DC2626), GPS location sharing, responder notification list, "Appeler les secours" button, cancel with confirmation dialog, haptic feedback on activation
- **SecurityQuestionnaireScreen**: safety rating (1-5 stars), vulnerable time slots, night walking distance slider, night concerns text — submits to POST /security/questionnaire
- **NightModeToggle** widget: switch with auto/manual label, dark/light mode icon
- Routes updated: /emergency → real EmergencyScreen, /profile/security → SecurityQuestionnaireScreen
- 5 new mobile tests (268 total mobile, 417 total project)

## [Session-64] — 2026-04-08
### Added
- **Security Dashboard** at `/dashboard/security` with KPI cards (avg score, employees, critical stops, incidents)
- `ScoreDistributionChart`: Recharts bar chart by risk level (green/orange/red/dark red)
- `RiskStopMap`: stop list with color indicators, map placeholder, critical/normal counts
- `NightShiftCoverage`: coverage % bar with optimal/partial/insufficient status
- `IncidentTimeline`: chronological timeline with severity-colored dots
- `EmergencyAlertLog`: filterable table (triggered/pending/resolved) with status badges
- `GET /security/risk-map`: all stops with scores and coordinates
- `GET /kpis/security`: avg score, risk distribution, night coverage, incidents
- Security API client with TypeScript interfaces
- 9 frontend tests

## [Session-63] — 2026-04-08
### Added
- Three-dimension security-constrained pooling: geographic (45%) + shift (30%) + security (25%) with configurable weights
- Night-hour constraints: minimum group size 3, no isolated stops, lighting threshold 0.4, critical stop avoidance
- `NightRouteResult` processing: filter critical/dark stops, suggest top-3 alternatives, validate route viability
- Priority vehicle assignment for night routes and high-risk employees
- `ClusteringConfig` model per site with all pooling parameters
- `SecurityConstraintConfig` dataclass for runtime configuration
- Alembic migration `p1q2r3s4t5u6`
- 18 backend tests (night grouping, stop filtering, alternatives, 3D scoring, priority vehicle, night routing)

## [Session-62] — 2026-04-08
### Added
- `SecurityScore` model: employee score (0-100), risk_level (low/medium/high/critical), contributing_factors JSONB
- Weighted scoring engine: questionnaire rating (35%) + vulnerable stop count (25%) + night commute exposure (25%) + stop isolation (15%)
- Risk classification: critical <=25, high <=50, medium <=75, low >75
- Night hour detection (20h00-6h30) with 80% risk elevation for night time slots
- 8-slot security heatmap generator with day/night distinction
- Group aggregation service by site/team/shift with risk distribution counts
- `GET /security/scores` (filtered by risk_level) + `GET /security/scores/{employee_id}` (detailed breakdown)
- Alembic migration `o0p1q2r3s4t5`
- 22 backend tests (scoring, classification, night detection, heatmap, aggregation, model)

## [Session-61] — 2026-04-08
### Added
- `SecurityQuestionnaire` model: employee_id, version (auto-increment), overall_safety_rating (1-5), responses JSONB, vulnerable_stops JSONB, night_concerns text, trigger_type (periodic/incident/initial)
- Alembic migration `n9o0p1q2r3s4` with 3 indexes
- `POST /security/questionnaire` — submit with auto-version per employee
- `GET /security/questionnaire/{employee_id}` — latest response + full history summary
- `POST /security/questionnaire/trigger-reassessment` — incident-triggered bulk reassessment
- `ReassessmentScheduler` service: quarterly (90d) / semi-annual (180d) / annual (365d) intervals, due detection, next due date calculation
- 18 backend tests (model, schema validation 1-5 rating, reassessment intervals, due detection)

## [Session-60] — 2026-04-08
### Added
- **RTI Monitoring Dashboard** at `/dashboard/rti` with 30-second auto-refresh
- `ComplianceGauge`: circular SVG gauge (green >=95%, yellow 85-95%, red <85%)
- `WaitTimeHeatmap`: per-stop risk bars with green→red gradient
- `RiskStopMapOverlay`: critical/normal stop legend, map placeholder, critical stop list
- `ViolationAlertList`: sortable violation table with severity badges (Élevé/Moyen/Faible)
- `ComplianceTrendChart`: Recharts line chart with target reference line, day/week/month period selector
- `GET /kpis/rti` backend endpoint: compliance_pct, avg_wait_seconds, active_violations, total_events, trend data
- RTI API client (`frontend/src/api/rti.ts`) with TypeScript interfaces
- KPI summary cards: avg wait time, active violations, total events
- 9 frontend tests + 3 backend tests (12 new, 345 total)

## [Session-59] — 2026-04-08
### Added
- `RTIConfig` model: per-site config (max_wait_seconds, compliance_target_pct, buffer_vehicle_count, night_mode hours) with unique (tenant, site) constraint
- Alembic migration `m8n9o0p1q2r3`
- `GET/PUT /rti/config/{site_id}` — read/update RTI configuration per site
- `GET /rti/adaptive-sizing/{site_id}` — sizing recommendation with compliance check
- `AdaptiveSizing` service: buffer calculation from breakdown rate (3%) + traffic delay factor (15%)
- `PoolRecomposition` service: triggers for employee_absence, shift_change, vehicle_breakdown, compliance_drop with vehicle reassignment estimate
- `RTIFallback` service: decision tree (compliant → no action, buffers available → activate, buffers exhausted → TAD request) with event logging
- 20 backend tests (model, schema, adaptive sizing, recomposition, fallback)

## [Session-58] — 2026-04-08
### Added
- **RTI Backend System**: Real-time vehicle tracking infrastructure
- `VehiclePosition` model with PostGIS POINT geometry (GIST index), heading, speed, recorded_at
- `RTIEvent` model for compliance tracking: event_type (arrival/departure/delay/breakdown), scheduled_at, actual_at, auto-computed wait_duration_seconds
- Alembic migration `l7m8n9o0p1q2` creating 2 tables with 6 indexes
- `POST /rti/vehicle-position` — GPS update stored in DB + Redis (30s TTL)
- `GET /rti/vehicle-position/{id}` — Redis-first lookup with DB fallback
- `GET /rti/stop/{id}/eta` — ETA via haversine distance + vehicle speed
- `POST /rti/events` — log event with auto wait_duration computation
- `GET /rti/compliance` — compliance % (arrivals within 90s threshold)
- WebSocket `ws://localhost:8000/ws/rti/{vehicle_id}` — broadcast positions to subscribed clients
- `EtaCalculator` with haversine great-circle distance, configurable speed (default 25 km/h urban)
- 14 backend tests (models, ETA, Redis serialization, schemas)

## [Session-57] — 2026-04-08 (Phase 4 Start)
### Added
- **StopRiskScore** model: PostGIS POINT geometry with GIST spatial index, 5 risk factor scores (isolation, lighting, TC frequency, night multiplier, employee perception), computed composite score, critical flag
- Weighted risk scoring algorithm: `Risk = w1*Isolation + w2*(1-Lighting) + w3*(1-TC) + w4*Night + w5*(1-Perception)` with configurable `RiskWeights` dataclass
- Critical threshold at 0.7 — stops above are auto-flagged
- `compute_and_flag()` evaluates both day and night scenarios, takes worst-case
- API endpoints: `GET /rti/risk-stops` (filter by site_id, is_critical), `POST /rti/risk-stops` (create with auto-score), `PUT /rti/risk-stops/{id}` (update + recompute)
- Alembic migration `k6l7m8n9o0p1` with GIST spatial index
- 20 backend tests (algorithm, critical flag, model, schemas)

## [Session-56] — 2026-04-08 (Phase 3 Complete!)
### Added
- **Offline Mode**: Comprehensive offline-first architecture for the mobile app
- `HiveStorageService`: user profile, trips, settings cache with TTL metadata per key
- `SqliteStorageService`: trip history, content library, notifications with indexed tables
- `CacheManager`: stale-while-revalidate pattern — serves stale cache immediately, refreshes in background when online
- `OfflineQueue`: priority-based write queue (critical/high/medium/low), auto-sync on reconnect, 3 retries max per action
- `ConnectivityService`: real-time online/offline/degraded state detection via connectivity_plus stream
- `OfflineManifestSync`: downloads profile+trips+site+points on launch and every 6h on WiFi
- `MapTileCache`: pre-cache strategy for home and site commute areas
- `CacheConfig`: configurable TTLs (profile 24h, trips 1h, content 6h, RTI 30s), storage limits (300MB total)
- `OfflineBanner`: displays "Vous êtes hors ligne" / degraded connection warning
- `StaleDataBadge`: shows "Mis à jour il y a Xh" for stale cached data
- `SyncSpinner`: animated sync indicator during queue processing
- 20 new tests (279 total passing: 263 mobile + 16 backend)

### Phase 3 — Mobile MVP: COMPLETE (12/12 sessions)

## [Session-55] — 2026-04-08
### Added
- `StatisticsScreen` with period selector (Ce mois / Cette année / Tout), pull-to-refresh, empty state
- `StatsSummaryCards`: 5 stat cards (trips, distance, CO2, training, quiz average)
- `TripsBarChart`: custom-painted monthly bar chart with counts and month labels
- `Co2TrendChart`: custom-painted line chart with area fill and date labels
- `TransportModePieChart`: custom-painted pie chart with color legend and percentages
- `ShareImpactCard`: blue impact card with trips/CO2/trees equivalent + share button
- `Co2Calculator`: car baseline (120g/km) vs bus (30g/passenger-km), formatCo2, treesEquivalent
- `StatisticsService` + `StatisticsNotifier` (Riverpod) with period filtering
- 20 new tests (259 total passing)

## [Session-54] — 2026-04-08
### Added
- **Backend**: 3 new database models: `TripBooking` (trip reservations), `DeviceRegistration` (FCM tokens), `PushNotification` (notification log)
- Alembic migration `j5k6l7m8n9o0` creating 3 tables with 8 indexes
- Mobile API router at `/api/v1/mobile/` with 8 endpoints: trip book/modify/cancel/list/upcoming, device register/unregister, offline manifest
- `TripBookingService` with 30-minute modification/cancellation window enforcement
- `OfflineManifestService` generating profile + trips + site + point_arrets package
- Pydantic v2 schemas: TripBookingCreate/Update/Response, DeviceRegisterRequest/Response
- 16 backend tests (models, schemas, 30-min validation)

## [Session-53] — 2026-04-08
### Added
- `ProfileScreen` with avatar (initials), name, matricule, site/shift chips, transport mode badge, quick stats (trips/CO2/training), 8 menu items, logout with confirmation dialog
- `EditProfileScreen` with phone, pickup address, PMR toggle, read-only SIRH fields
- `PreferencesScreen` with 8-mode transport selector, walking distance slider, volunteer driver, 4 notification toggles, auto night mode
- `UserProfile` model with fromJson, displayName, initials; `ProfileStats`, `NotificationPreferences`
- `ProfileService` (getProfile, updateProfile, updatePreferences, updateNotificationPreferences)
- `ProfileNotifier` (Riverpod) with load, updateProfile, updatePreferences, clearMessages
- `ProfileHeader` + `TransportModeBadge` + `QuickStatsRow` widgets
- 17 new tests (223 total passing)

## [Session-52] — 2026-04-08
### Added
- Push notification service: `PushNotificationService` with FCM permission, token registration (POST /devices/register), foreground/background/tap handling, token refresh
- `NotificationType` enum: 5 types (rti_alert, route_change, weather, content, emergency) with French labels, icons, target routes
- `NotificationItem` model with fromJson, fromFCM factory, copyWith, smart targetRoute routing
- `NotificationNotifier` (Riverpod) with stream subscription, markAsRead, markAllAsRead, dismiss, unreadCount, groupedByDate
- `NotificationListScreen` with date-grouped list (Aujourd'hui/Hier), type-colored icons, unread dots, swipe-to-dismiss, "Tout lire" button
- `NotificationChannels` config for Android notification channels
- 15 new tests (206 total passing)

## [Session-51] — 2026-04-08
### Added
- Real-time vehicle tracking: `RTITrackingScreen` with live ETA countdown (1s timer), color-coded (green <=90s, orange 90-180s, red >180s)
- `FullMapScreen` with ETA overlay, legend panel, LIVE indicator
- `VehicleArrivalCard` with countdown, vehicle info, "Carte complète" button
- `TrackingMiniMap` with legend (Vous, Arrêt, Véhicule) and EN DIRECT badge
- `WebSocketService` (socket_io_client) with auth token, vehicle subscription, position stream
- `VehicleTrackingService` REST fallback (getLatestPosition, getTrackingInfo)
- `TrackingNotifier` (Riverpod) with WebSocket primary + 10s polling fallback
- `MapUtils` for ETA color coding and formatting (formatEta, formatEtaShort)
- `VehiclePosition` + `TrackingInfo` models
- Connection status indicator (EN DIRECT / HORS LIGNE)
- 28 new tests (191 total passing)

## [Session-50] — 2026-04-08
### Added
- Trip management: `TripsScreen` with À venir / Passés tabs, pull-to-refresh, cancel confirmation dialog
- `TripDetailScreen` with FutureProvider, 4-step status timeline, detail card, CO2Badge, cancel action
- `TripHistoryScreen` with stats header (trips, CO2, distance) and monthly grouped trip list (French month names)
- `Trip` model (15 fields), `TripStatus` enum with French labels and fromString parsing, `TripStats` aggregate
- `TripCard` widget with status chip (color-coded), CO2 badge, conditional modify/cancel actions (>30min rule)
- `TripStatusTimeline` — 4-step visual progress (Réservé → Confirmé → En cours → Terminé)
- `Co2Badge` — green badge with eco icon
- `TripsNotifier` (Riverpod) with parallel load, cancelTrip, pastByMonth grouping
- Extended `TripService` with getUpcomingTrips, getPastTrips, getTripDetail, cancelTrip, modifyTrip
- 21 new tests (163 total passing)

## [Session-49] — 2026-04-08
### Added
- Trip booking flow (`TripBookingScreen`) with date picker, shift selector, pickup point, summary, and confirm
- `DatePickerStrip` — horizontal scroll (today + 7 days), French day/month abbreviations, selected highlight
- `ShiftSelector` — radio-style shift cards with entry/exit times, loading/empty states
- `PickupPointPicker` — current point display + bottom sheet picker with walking time
- `BookingSummaryCard` — accent-colored summary with date, shift, pickup point
- `TripBooking`, `Shift`, `PickupPoint`, `BookingConfirmation` models with JSON serialization
- `TripService` for site shifts, nearby pickup points, and trip booking API
- `TripBookingNotifier` (Riverpod) with canConfirm logic, submit flow, error handling
- Cancellation policy banner ("30 minutes avant le départ")
- 30 new tests (142 total passing)

## [Session-48] — 2026-04-08
### Added
- Home screen (`HomeScreen`) with personalized greeting (Bonjour/Bon après-midi/Bonsoir + user name)
- `NextDepartureCard` with live countdown timer (updates every second), color-coded (green >5min, orange 2-5min, red <2min), departure details (pickup, route, vehicle, driver)
- `QuickActionsRow` with 3 action cards: Réserver, Carte, Mes trajets
- `ContentCarousel` — horizontal scroll with type badges (Actualité, Formation, Sécurité, Sondage), unread indicators
- `EmergencyButton` — red emergency button for night mode (20h-6h30)
- `NightModeHelper` with configurable night hours and injectable DateTime for testing
- `Departure` and `ContentItem` models with JSON parsing
- `DepartureService` for next trip + latest content + notification count
- `HomeNotifier` (Riverpod) with parallel data loading and pull-to-refresh
- Notification bell with unread count badge (caps at 9+)
- Empty state when no upcoming trips
- 29 new tests (112 total passing)

## [Session-47] — 2026-04-08
### Added
- 4-step onboarding wizard (`OnboardingFlow`) using PageView with progress bar navigation
- Welcome carousel (3 slides: Transport optimisé, Suivi en temps réel, Impact positif)
- Transport preferences step: 8 transport mode chips, company transport/private car/volunteer driver switches, carpool seats slider, walking distance slider (200m-2km)
- Security questionnaire step: 5-star safety rating, 6 time slot chips, night walking distance slider, night concerns text input
- Permissions step: location + notification permission cards with grant status, RGPD privacy note
- `TransportPreferences` model (currentMode, hasPrivateCar, volunteerDriver, carpoolSeats, maxWalkingDistance, pickup lat/lng)
- `SecurityPreferences` model (safetyRating, vulnerableTimeSlots, concernZones, nightConcerns, maxNightWalkingDistance)
- `OnboardingService` for PATCH /employees/me/preferences
- `OnboardingNotifier` (Riverpod StateNotifier) managing wizard state across 4 steps
- 33 new tests (83 total passing)

## [Session-46] — 2026-04-08
### Added
- JWT authentication flow: `AuthService` (login, refresh, logout, getProfile)
- `ApiClient` with dio interceptor: auto-injects Bearer token, auto-refreshes on 401, retries original request
- `AuthNotifier` (Riverpod StateNotifier) with 5 states: initial, loading, authenticated, unauthenticated, error
- `SplashScreen`: auto-login check via stored refresh token, branded loading
- `LoginScreen`: email/password form, validation, error banner (Pydantic v2 format), password visibility toggle
- `User` model matching backend UserResponse schema
- `AuthToken` model (access_token, refresh_token, token_type)
- `extractApiError()` utility for Pydantic v2 error extraction
- 28 new tests (50 total passing)

## [Session-45] — 2026-04-08
### Added
- Flutter project initialized in `mobile/` (Flutter 3.38.5, Dart 3.10.4)
- 111 dependencies resolved: flutter_riverpod, go_router, dio, google_maps_flutter, firebase_messaging, hive, sqflite, flutter_secure_storage, connectivity_plus, socket_io_client, google_fonts
- Folder structure: `lib/config`, `models`, `services`, `providers`, `screens`, `widgets`, `utils`, `l10n`
- `ApiConfig` with base URL + `--dart-define` override for dev/prod
- `AppColors` with full color system (light, dark, night mode, semantic tokens)
- `AppTypography` using Inter via google_fonts
- `AppTheme` with Material 3 light + dark themes (primary #0058be)
- `GoRouter` configuration with 17 routes (ShellRoute for bottom nav + standalone)
- Bottom navigation bar: 5 tabs (Accueil, Trajets, Suivi, Contenu, Profil)
- Base widgets: `AppScaffold`, `LoadingIndicator`, `AppErrorWidget`, `EmptyState`
- 22 tests passing

## [Session-44] — 2026-04-02
### Added
- KPISnapshot SQLAlchemy model (tenant_id, site_id, snapshot_date, kpi_type, value JSONB) + Alembic migration
- KPI service: capture 6 KPI types per site (mobility_coverage, modal_distribution, occupancy_rate, co2_saved, rti_compliance, security_score)
- POST `/kpis/snapshot` endpoint — single site or all sites snapshot
- GET `/kpis/trend` endpoint — historical trend with kpi_type, site_id, date range filters (max 365 points)
- Celery scheduled task `daily_kpi_snapshot` for automated daily capture across all tenants/sites
- Reuses existing analytics (hr_analytics.compute_mobility_coverage, rse_analytics.compute_co2_savings)
- rti_compliance and security_score as placeholders (return 0 until Sessions 58/62)
- 7 tests in `backend/tests/test_kpi_snapshot.py`

### Changed
- `backend/app/api/v1/kpis.py` — Added snapshot + trend endpoints
- `backend/app/models/__init__.py` — Added KPISnapshot

---

## [Session-43] — 2026-04-02
### Added
- GET `/export/history` endpoint with pagination and report_type filter
- ReportListPage (`/reports`): history table with type filter, download buttons, pagination, empty state
- ReportGeneratorPage (`/reports/generate`): 2-step flow — select type → configure format → generate + download
- ReportTypeSelector: 7 report types in responsive card grid with selection state
- ParameterConfigPanel: PDF/Excel radio selector + generate button with loading spinner
- TypeScript types + API client for report history and generation
- i18n translations (fr + en)
- 6 frontend tests

### Changed
- `backend/app/api/v1/exports.py` — Added history endpoint
- `frontend/src/routes.tsx` — Added `/reports` and `/reports/generate` routes

---

## [Session-42] — 2026-04-02
### Added
- GeneratedReport SQLAlchemy model (tenant_id, report_type, params, file_url, format, generated_by) + Alembic migration
- 4 report generators in `report_engine.py`: modal analysis, fleet utilization, volunteer driver, HR mobility
- Each generator supports PDF (reportlab) and Excel (openpyxl) output
- GET endpoints: `/export/modal-report`, `/export/fleet-report`, `/export/volunteer-report`, `/export/hr-mobility`
- `_persist_report` helper stores GeneratedReport records in DB for each export
- 7 tests in `backend/tests/test_generated_report.py`

### Changed
- `backend/app/api/v1/exports.py` — Added 4 report endpoints + persistence helper
- `backend/app/models/__init__.py` — Added GeneratedReport export

---

## [Session-41] — 2026-04-02
### Added
- RSE analytics service: CO2 savings (baseline vs actual), private vehicles avoided, modal distribution (soft/electric/shared/individual with before/after), ZFE compliance (`backend/app/services/rse_analytics.py`)
- DPEF PDF report generator with reportlab (CO2, modal, ZFE, vehicles tables)
- GET `/kpis/rse` endpoint returning all RSE KPIs
- POST `/kpis/rse/dpef` endpoint for DPEF PDF download
- RSEDashboardPage at `/dashboard/rse`: 3 summary cards, CO2TrendLine, modal PieChart, ZFEComplianceGauge, ModalShiftComparison, DPEF export button
- CO2TrendLine: Recharts line chart with green trend
- ZFEComplianceGauge: SVG semicircle gauge (green/amber/red thresholds)
- ModalShiftComparison: grouped bar chart comparing before/after modal distribution
- TypeScript types + API client for RSE KPIs
- i18n translations (fr + en)
- 13 tests total (7 backend + 6 frontend)

### Changed
- `backend/app/api/v1/kpis.py` — Added RSE and DPEF endpoints
- `frontend/src/routes.tsx` — Added `/dashboard/rse` route

---

## [Session-40] — 2026-04-02
### Added
- HRDashboardPage at `/dashboard/hr` with full KPI visualization fetching from GET `/kpis/hr`
- HeatmapTable: reusable color-coded coverage table (red/amber/green thresholds)
- ScatterPlot: reusable Recharts scatter chart component
- RetentionImpactCard: savings estimate, turnover rate, departure with/without transport bar
- ShadowZonesList: employees beyond 30km threshold, limited to 20 with "voir plus"
- MobilityAlerts: critical/warning banners when coverage < 60% or shadow zones > 10%
- Mobility score evolution LineChart (Recharts)
- TypeScript types for HR KPIs + API client
- i18n translations for HR section (fr + en)
- Route for `/dashboard/hr` with lazy loading
- 8 tests in `frontend/src/pages/dashboard/__tests__/HRDashboard.test.tsx`

### Changed
- `frontend/src/routes.tsx` — Added HR dashboard route

---

## [Session-39] — 2026-04-02
### Added
- HR analytics service with 5 KPI functions (`backend/app/services/hr_analytics.py`):
  - Mobility coverage: % of employees with transport solution, breakdown by site, shift, department
  - Mobility score evolution: time-series from completed optimization runs
  - Absenteeism correlation: compare absence rates for transport-interest groups (with/without/maybe)
  - Retention impact: turnover analysis, departed with/without transport interest, estimated savings
  - Shadow zones: employees with distance >30km or no modal data, threshold-based flagging
- KPI router with GET `/kpis/hr` endpoint (`backend/app/api/v1/kpis.py`)
- 6 tests in `backend/tests/test_hr_analytics.py`

### Changed
- `backend/app/api/v1/__init__.py` — Registered kpis router

---

## [Session-38] — 2026-04-02
### Added
- DAF export engine: ERP-compatible CSV and XML with standard accounting columns (account code, label, debit, credit, journal) (`backend/app/services/daf_export.py`)
- 3 ERP format templates: SAP FI (BKPF/BSEG, BUKRS, HKONT, WRBTR), Sage (JournalCode, CompteNum, PieceRef), Cegid (SectionAnalytique, CodeAnalytique)
- TCO/ROI accounting entry builders from calculation results
- TCO PDF report with reportlab: summary table + vehicle breakdown
- ROI PDF report with reportlab: summary + lever breakdown table
- TCO Excel report with openpyxl: styled "Resume TCO" sheet with vehicle detail
- ROI Excel report with openpyxl: styled "Resume ROI" sheet with lever detail
- POST `/financial/export/daf` — ERP export (CSV or XML, configurable ERP format)
- POST `/financial/export/tco` — TCO report download (PDF or Excel)
- POST `/financial/export/roi` — ROI report download (PDF or Excel)
- Pydantic schemas: `DAFExportRequest`, `FinancialReportRequest`
- 10 tests in `backend/tests/test_daf_export.py`

### Changed
- `backend/app/api/v1/financial.py` — Added 3 export endpoints with file download responses

---

## [Session-37] — 2026-04-02
### Added
- Cost analysis engine: cost per available seat, per occupied seat, per employee, breakeven point (`backend/app/services/cost_analysis.py`)
- PRD example verified: 50-seat bus at 120K/year = 5.45 EUR/seat, 6.81 at 80% fill, breakeven at 73 employees
- Breakeven chart data generator with transport vs kilometric allowance curves
- Pydantic schemas: `CostAnalysisRequest`, `CostAnalysisResponse`, `BreakevenPoint`
- POST `/financial/cost-analysis` endpoint
- CostAnalysisPanel: form + 4 metric cards + breakeven badge
- BreakevenChart: Recharts LineChart with transport/allowance curves, reference line at breakeven
- TypeScript types + API function for cost analysis
- 8 tests (6 backend + 2 frontend)

### Changed
- `backend/app/api/v1/financial.py` — Added cost-analysis endpoint
- `backend/app/schemas/financial.py` — Added 3 cost analysis schemas

---

## [Session-36] — 2026-04-02
### Added
- WaterfallChart: Recharts BarChart showing 4 ROI levers (absenteisme, retention, flotte, trajet) + total
- PaybackSlider: color-coded payback indicator (green <12mo, yellow 12-24mo, red >24mo)
- CostPerTripGauge: SVG semicircle gauge with actual vs target cost per trip
- InvestmentComparatorCards: 3 model cards (CAPEX/MaD/OPEX) with recommended badge
- DAFExportButton: dropdown for CSV/Excel/PDF export (placeholder for Session 38)
- ROICalculatorTab: full 11-field form + results (waterfall, payback, summary cards)
- InvestmentComparatorTab: 4-field form + comparison cards + recommendation banner
- ROI and comparator TypeScript types + API functions (calculateROI, compareInvestments)
- 7 tests in `frontend/src/pages/financial/__tests__/FinancialROI.test.tsx`

### Changed
- `FinancialDashboardPage` — ROI and Comparator tabs now show real content (replaced placeholders)
- `frontend/src/types/financial.ts` — Added ROI + comparator interfaces
- `frontend/src/api/financial.ts` — Added 2 new API functions

---

## [Session-35] — 2026-04-02
### Added
- TypeScript interfaces for TCO calculation types (`frontend/src/types/financial.ts`)
- Financial API client: `calculateTCO`, `getVehicleReferences` (`frontend/src/api/financial.ts`)
- 5 financial chart/table components: TCOComparisonCards (vehicle cards with lowest highlight), TCOEvolutionChart (Recharts LineChart), MotorizationTable (comparison with green cheapest row), VehicleTCOBreakdown (stacked BarChart), FleetAggregation (summary card)
- TCOCalculatorPage (`/financial/tco`): fleet composition form, duration slider, calculate button, results display with all 5 components
- FinancialDashboardPage (`/financial`): tab navigation for TCO/ROI/Comparateur (ROI and Comparateur as placeholders)
- Routes for `/financial` and `/financial/tco` with lazy loading
- i18n translations for financial section (fr + en)
- 7 tests in `frontend/src/pages/financial/__tests__/FinancialTCO.test.tsx`

### Changed
- `frontend/src/routes.tsx` — Added financial routes

---

## [Session-34] — 2026-04-02
### Added
- Investment model comparator engine: CAPEX (own fleet), Mise a Disposition (rental), OPEX (full outsource) — each computing total cost, annual cost, cost per employee, cost per trip (`backend/app/services/investment_comparator.py`)
- Recommendation logic: heuristic based on fleet size/duration, overridden by >20% cost difference
- Sensitivity analysis: fuel price delta (±50%), headcount delta (±50%), fill rate (50-100%) — recomputes all 3 models and returns deltas vs baseline
- Pydantic schemas: `InvestmentCompareRequest/Response`, `SensitivityRequest/Response`, `InvestmentModelResult`, `SensitivityDelta`
- POST `/financial/compare` — side-by-side comparison with recommendation
- POST `/financial/compare/sensitivity` — sensitivity analysis endpoint
- 11 tests in `backend/tests/test_investment_comparator.py` (9 unit + 2 integration)

### Changed
- `backend/app/schemas/financial.py` — Added 8 comparison/sensitivity schemas
- `backend/app/api/v1/financial.py` — Added 2 compare endpoints, imported `Decimal`

---

## [Session-33] — 2026-04-02
### Added
- ROI calculator engine with 4 levers: absenteeism (rate × daily_cost × headcount × 220 working days), retention (turnover reduction × replacement cost), fleet optimization (current vs optimized fleet cost), journey productivity (travel hours × engagement × training cost) (`backend/app/services/roi_calculator.py`)
- Payback period in months: `(total_investment / annual_roi_total) × 12`
- ROI percentage: `(roi_total / total_investment) × 100`
- Edge case handling: zero investment returns 0% ROI, negative savings clamped to 0
- Pydantic schemas: `ROICalculateRequest` (13 input params), `ROICalculateResponse` (10 output fields + stored_id)
- POST `/financial/roi/calculate` endpoint with optional `scenario_id` to persist results in `ROICalculation` table
- 9 tests in `backend/tests/test_roi_calculator.py` (7 unit + 2 integration, including DB persistence)

### Changed
- `backend/app/schemas/financial.py` — Added 2 ROI calculation schemas
- `backend/app/api/v1/financial.py` — Added ROI calculate endpoint with DB persistence

---

## [Session-32] — 2026-04-02
### Added
- TCO calculator engine with core formula: `TCO = Purchase + (Maintenance × Duration) + (Energy/km × Annual_km × Duration) − Residual` (`backend/app/services/tco_calculator.py`)
- Per-vehicle and fleet-level TCO aggregation with quantity support
- Motorization comparison: computes TCO for all available motorizations per vehicle type, sorted cheapest-first
- Year-by-year evolution (1-10 years) showing monotonically increasing cumulative fleet TCO
- Default cost parameters per motorization with vehicle type multipliers (vehicule_leger through grand_bus)
- Custom cost override support — any default parameter can be overridden per vehicle in the fleet
- Pydantic schemas: `TCOCalculateRequest`, `TCOCalculateResponse`, `TCOFleetResult`, `TCOYearlyPoint`, `TCOMotorizationComparison`
- POST `/financial/tco/calculate` endpoint returning fleet TCO, evolution, and motorization comparisons
- 8 tests in `backend/tests/test_tco_calculator.py` (7 unit + 1 integration)

### Changed
- `backend/app/schemas/financial.py` — Added 8 TCO calculation schemas
- `backend/app/api/v1/financial.py` — Added TCO calculate endpoint

---

## [Session-31] — 2026-04-02
### Added
- FinancialScenario, TCOEntry, ROICalculation, VehicleReference SQLAlchemy models (`backend/app/models/financial.py`)
- Alembic migration for 4 financial tables (`backend/alembic/versions/c3d4e5f6a7b8_add_financial_tables.py`)
- Pydantic v2 schemas with validation: investment model types, vehicle types, positive costs, rate ranges (`backend/app/schemas/financial.py`)
- 8 API endpoints under `/financial/`: scenario CRUD (5), TCO entries (2), vehicle reference catalog (1) (`backend/app/api/v1/financial.py`)
- Vehicle reference seed script with 5 PRD vehicle types (minibus, midibus, bus_standard, grand_bus, vehicule_leger), idempotent, runs at app startup (`backend/app/db/seed_vehicles.py`)
- 7 tests in `backend/tests/test_financial_models.py` covering scenario CRUD, TCO entries, schema validation, vehicle catalog

### Changed
- `backend/app/api/v1/__init__.py` — Registered financial router with tags=["financial"]
- `backend/app/models/__init__.py` — Added 4 financial model exports
- `backend/app/main.py` — Added lifespan hook to seed vehicle references on startup

---

## [Session-30] — 2026-04-02
### Added
- ExportEngine service with 5 format generators: PDF, Excel, CSV stops, CSV employees, GeoJSON (`backend/app/services/export_engine.py`)
- PDF driver sheets using reportlab: cover page with metrics summary, per-route driver sheets with ordered stops tables, PMR indicators highlighted in blue with bold red text
- Multi-sheet Excel workbook using openpyxl: "Resume" summary sheet, per-site sheet with clusters/routes/employees sections, PMR rows highlighted in yellow
- CSV stop order export: route_number, stop_order, employee details, PMR flags, ETA, cumulative distance
- CSV employee assignments export: employee details with cluster/route/vehicle assignments
- GeoJSON FeatureCollection: route LineStrings (from polyline or stops), stop Points with PMR properties, cluster centroid Points
- 5 API endpoints under `/export/` prefix: GET pdf, excel, csv/stops, csv/employees, geojson — all require `optimization_id` query param (`backend/app/api/v1/exports.py`)
- Celery task wrapper for large async exports with Redis progress tracking, 120s timeout (`backend/app/tasks/export_tasks.py`)
- Google encoded polyline decoder helper for GeoJSON route geometry
- `reportlab>=4.4.3` dependency added to requirements.txt
- 22 tests in `backend/tests/test_exports.py` covering all formats + PMR indicators + polyline decoder

### Changed
- `backend/app/api/v1/__init__.py` — Registered exports router with tags=["exports"]

---

## [Session-29] — 2026-04-02
### Added
- OptimizationSettings SQLAlchemy model with tenant-scoped one-row-per-tenant pattern (UniqueConstraint on tenant_id), fields: meeting_radius_meters, max_walking_distance_meters, max_route_duration_seconds, fuel_cost_per_liter, fuel_consumption_l_per_100km, co2_kg_per_liter, rti_threshold_minutes, night_mode_start, night_mode_end, min_night_group_size (`backend/app/models/settings.py`)
- ConstraintParam SQLAlchemy model with UniqueConstraint on (tenant_id, key), fields: key, value, category, description, is_active (`backend/app/models/settings.py`)
- Alembic migration for optimization_settings and constraint_param tables (`backend/alembic/versions/b2c3d4e5f6a7_add_settings_tables.py`)
- Pydantic v2 schemas for settings and constraints CRUD (`backend/app/schemas/settings.py`)
- 2 settings API endpoints: GET `/settings` (get-or-create default), PUT `/settings` (partial update) (`backend/app/api/v1/settings.py`)
- 5 constraints API endpoints: GET `/constraints` (category filter), POST `/constraints`, PUT `/constraints/{id}`, DELETE `/constraints/{id}`, POST `/constraints/bulk` (`backend/app/api/v1/constraints.py`)
- Settings TypeScript interfaces (`frontend/src/types/settings.ts`)
- Settings API client with 7 functions (`frontend/src/api/settings.ts`)
- SettingsPage (`/settings`): form with range sliders for distance/duration, number inputs for costs, time inputs for night mode (`frontend/src/pages/settings/SettingsPage.tsx`)
- ConstraintsPage (`/settings/constraints`): data table with category filter, inline add/edit/delete, bulk import (`frontend/src/pages/settings/ConstraintsPage.tsx`)
- 6 backend tests in `test_settings.py` (150 total passing)
- 16 frontend tests across 2 test files (6 SettingsPage + 10 ConstraintsPage)

### Changed
- `backend/app/api/v1/__init__.py` -- Registered settings and constraints routers
- `backend/app/models/__init__.py` -- Added OptimizationSettings and ConstraintParam imports
- `frontend/src/routes.tsx` -- Added lazy imports and routes for `/settings` and `/settings/constraints`
- `frontend/src/i18n/fr.json` and `en.json` -- Added settings/constraints translations

---

## [Session-28] — 2026-04-02
### Added
- Scenario TypeScript types: Scenario, ScenarioMetrics, MetricDelta, ScenarioComparison, WeatherForecast, ScenarioSuggestion, WeatherSuggestions (`frontend/src/types/scenario.ts`)
- Scenario API client with 8 functions: simulateScenario, listScenarios, getScenario, deleteScenario, compareScenarios, getWeatherForecasts, refreshWeather, getWeatherSuggestions (`frontend/src/api/scenarios.ts`)
- ScenarioListPage (`/scenarios`): data table with condition chips, site filter, checkbox selection for multi-compare, delete actions (`frontend/src/pages/scenarios/ScenarioListPage.tsx`)
- ScenarioComparePage (`/scenarios/compare`): side-by-side metrics comparison with color-coded deltas (green=improvement, red=worse), recommendations panel, URL parameter support (`frontend/src/pages/scenarios/ScenarioComparePage.tsx`)
- WeatherWidget component: 3-day forecast display with condition icons, temp ranges, precipitation, scenario suggestion chips with one-click Apply button (`frontend/src/components/optimization/WeatherWidget.tsx`)
- 40 frontend tests across 3 test files (15 + 15 + 10)

### Changed
- `frontend/src/routes.tsx` — Added lazy imports and routes for `/scenarios` and `/scenarios/compare`
- `frontend/src/components/layout/Sidebar.tsx` — Added "Scenarios" navigation item
- `frontend/src/pages/optimization/OptimizationPage.tsx` — Integrated WeatherWidget below controls, added `transit_failure` to condition options, added `handleWeatherScenario` callback
- `frontend/src/components/optimization/index.ts` — Added WeatherWidget barrel export
- `frontend/src/pages/optimization/__tests__/OptimizationPage.test.tsx` — Fixed test compatibility with WeatherWidget addition

---

## [Session-27] — 2026-04-02
### Added
- Scenario SQLAlchemy model with tenant_id, site_id, baseline_optimization_id FK, condition_type, demand_multiplier, custom_params (JSONB), estimated_metrics (JSONB), name (`backend/app/models/scenario.py`)
- Alembic migration for scenario table with idx_scenario_tenant and idx_scenario_site indexes
- Scenario engine service with demand multipliers (normal=1.0, rain=1.15, strike=1.5, peak=1.3, night=0.8, transit_failure=1.4), metric estimation, and comparison delta calculation (`backend/app/services/scenarios.py`)
- Pydantic schemas: ScenarioRequest, ScenarioResponse, ScenarioComparisonRequest, MetricDelta, ScenarioComparisonResponse with French alias support (pluie, greve_transport, pic_activite, nuit, defaillance_tc) (`backend/app/schemas/scenario.py`)
- 5 API endpoints: POST `/scenarios/simulate`, GET `/scenarios`, GET `/scenarios/{id}`, DELETE `/scenarios/{id}`, POST `/scenarios/compare` (`backend/app/api/v1/scenarios.py`)
- 6 backend tests in `test_scenarios.py` (144 total passing)

### Changed
- `backend/app/schemas/optimization.py` — Added "transit_failure" to CONDITION_TYPES
- `backend/app/models/__init__.py` — Added Scenario import
- `backend/app/api/v1/__init__.py` — Registered scenarios router

---

## [Session-26] — 2026-04-02
### Added
- WeatherForecast model with unique constraint on (site_id, date, source)
- Weather service: OpenWeatherMap 5-day/3-hour fetch, daily aggregation, upsert, scenario suggestions
- 4 API endpoints: GET `/weather/{site_id}`, POST `/weather/{site_id}/refresh`, POST `/weather/refresh-all`, GET `/weather/{site_id}/suggestions`
- Pydantic schemas: WeatherForecastResponse, WeatherRefreshResponse, WeatherRefreshAllResponse, ScenarioSuggestion, WeatherSuggestionsResponse
- Alembic migration for weather_forecast table
- Config: `weather_api_key`, `weather_api_url` settings
- 5 backend tests with mocked external API (138 total passing)

---

## [Session-25] — 2026-04-02
### Added
- MetricsPanel: 6 KPI cards with inline SVG icons (vehicles, employees, occupancy gauge, distance, fuel cost, CO2)
- RouteList: expandable accordion showing per-vehicle stops with ETA and cumulative distance
- ClusterTable: borderless table with PMR chips and hover highlights
- SiteBreakdown: summary card with condition type chip and computed totals
- GaugeChart: SVG semicircle gauge with clamping, ARIA attributes, configurable size/color
- OptimizationResultPage (`/optimization/:id`): map + tabbed analytics panel + export buttons
- OptimizationHistoryPage (`/optimization/history`): table with status chips, pagination, view links
- 2 new lazy-loaded routes added to routes.tsx
- 35 new frontend tests (4 files)

---

## [Session-24] — 2026-04-01
### Added
- Optimization page (`/optimization`) with split layout: controls panel + Leaflet map
- TypeScript types for optimization entities, metrics, routes, meeting zones, layer visibility
- API client (5 functions) for optimization endpoints
- Zustand store with launch/poll/fetch, layer toggles, route selection
- ClusterRegion map component: circle overlay scaled by employee count
- RoutePolyline: Google encoded polyline decoder, 8-color palette, route popup with metrics
- MeetingZoneMarker: circle marker with PMR accessibility indicator
- AccessLeg: dashed walking path line (employee -> meeting zone)
- MapLegend: glassmorphism floating panel with 6 layer toggles + per-route selector
- Metrics bar: vehicles, employees, occupancy, distance, CO2
- Progress bar with step description for async optimization runs
- 15 new frontend tests (4 files)

---

## [Session-23] — 2026-04-01
### Added
- Full optimization pipeline orchestrator (`backend/app/services/optimization_pipeline.py`)
  - 7-step pipeline: filter → cluster → meeting zones → assign → route → metrics → save
  - Leave-aware employee filtering for target date
  - Metrics calculation: fuel (L), cost (MAD), CO2 (kg), time saved (hrs), occupancy rate
- Celery task wrapper with Redis progress tracking (`backend/app/tasks/optimization_tasks.py`)
  - 6-step progress updates (0%→100%) stored in Redis with 1h TTL
  - Graceful sync fallback when Celery broker unavailable
- 5 optimization pipeline schemas: RunRequest, MetricsResponse, StatusResponse, FullResponse, HistoryItem
- 5 API endpoints: POST `/optimize`, GET `/optimize/{id}`, GET `/optimize/{id}/status`, GET `/optimize/latest/result`, GET `/optimize/history/list`
- 8 unit tests in `test_optimization_pipeline.py`

---

## [Session-22] — 2026-04-01
### Added
- Route SQLAlchemy model with polyline, ordered stops JSONB, distance/time metrics (`backend/app/models/optimization.py`)
- Alembic migration for route table with spatial index
- OSRM table service (`osrm_table`) for NxN distance/time matrices with haversine fallback
- OSRM multi-waypoint route service (`osrm_route_multi`) with polyline and leg parsing
- OR-Tools CVRP solver with capacity dimension, time dimension (90min max), node dropping
- PATH_CHEAPEST_ARC first solution + GUIDED_LOCAL_SEARCH metaheuristic (10s time limit)
- Sequential fallback assignment when OR-Tools unavailable
- Two-leg route model: walking access leg + driving main leg
- ETA calculation per stop with cumulative distance tracking
- Route Pydantic schemas (`RouteResponse`, `RouteStopResponse`, `TwoLegResponse`)
- 2 API endpoints: GET `/routes` (with site/optimization/vehicle filters), GET `/routes/{id}`
- 10 unit tests in `test_routing.py`

---

## [Session-21] — 2026-04-01
### Added
- Vehicle assignment service with best-fit decreasing bin-packing algorithm (`backend/app/services/vehicle_assignment.py`)
- PMR-aware matching: clusters with PMR employees get PMR-accessible vehicles
- ZFE compliance enforcement for low-emission zone sites
- Cluster split (geographic bisection by latitude) for oversized clusters
- Cluster merge (greedy nearest-neighbor with haversine distance) for small clusters
- Volunteer driver integration as supplemental capacity
- Vehicle recommendations for unassigned clusters
- Pydantic v2 schemas for assignment request/response (`backend/app/schemas/vehicle_assignment.py`)
- 3 API endpoints: POST `/vehicle-assignments/assign`, `/vehicle-assignments/split-cluster/{id}`, `/vehicle-assignments/merge-clusters`
- 9 unit tests in `test_vehicle_assignment.py`

---

## [Mini-Changes] — 2026-04-01
### Added
- Frontend dev container in `docker-compose.yml` (node:20-alpine, Vite dev server with hot reload)
- `frontend_node_modules` named volume to isolate container deps from host
- Live Browser Check section in ui-review skill (Chrome console/visual verification)
- Browser test scope in run-tests skill
- Section 11 (Browser Verification) in `agents.md`

### Fixed
- Backend Docker healthcheck URL: `/health` → `/api/v1/health`
- Health-check skill: clarified which services exist vs future (celery/celery-beat)

### Changed
- deploy-local skill: added frontend container verification step
- health-check skill: added `docker compose ps frontend` and log checks

---

## [Session-20] — 2026-04-01
### Added
- Vehicle SQLAlchemy model with 17 fields (`backend/app/models/vehicle.py`)
- Alembic migration for vehicle table
- Pydantic schemas with enum validation: condition (Bon/Moyen/Mauvais), motorization (diesel/hybrid/electric/hydrogen/gnv), owner_type
- 5 API endpoints: GET/POST/PUT/DELETE `/vehicles` + GET `/vehicles/fleet-summary`
- Multi-filter support: site_id, is_pmr_accessible, condition, motorization, zfe_compliant
- Fleet summary aggregations: by type, condition, motorization, site with capacity/PMR/ZFE counts
- 11 tests in `test_vehicles.py`

---

## [Session-19] — 2026-04-01
### Added
- OSRM API client (`backend/app/services/osrm_client.py`) — nearest road snap, walking/driving routes, haversine fallback
- Meeting zone optimizer (`backend/app/services/meeting_zones.py`) — centroid snap-to-road, PMR accessibility check, walking distance constraint validation, per-employee access leg computation
- `POST /clusters/generate-with-zones` — combined clustering + meeting zone optimization endpoint
- Pydantic schemas: AccessLegResponse, MeetingZoneResponse, MeetingZonesResult
- 7 tests (5 unit + 2 OSRM mock integration)

---

## [Session-18] — 2026-04-01
### Added
- Optimization and Cluster SQLAlchemy models with PostGIS centroid geometry (`backend/app/models/optimization.py`)
- Alembic migration for optimization and cluster tables
- Clustering service with 3 algorithms: DBSCAN (haversine), KMeans, hierarchical/Ward (`backend/app/services/clustering.py`)
- Configurable params: eps_meters (50-5000m), min_samples, n_clusters, max_cluster_size
- PMR-aware clustering with pmr_count per cluster
- Auto-split oversized clusters via KMeans sub-clustering
- Pydantic schemas: ClusteringRequest, ClusterResponse, OptimizationResponse, ClusteringResponse (`backend/app/schemas/optimization.py`)
- 3 API endpoints: POST `/clusters/generate`, GET `/clusters`, GET `/clusters/{id}` (`backend/app/api/v1/clusters.py`)
- 11 tests (9 unit + 2 integration) in `test_clustering.py`

---

## [Session-17] — 2026-04-01
### Added
- Mobility scoring engine (`backend/app/services/mobility_scoring.py`) — per-employee score (0-100), group aggregation (site/dept/shift), time-slot bucketing, shadow zone identification
- Modal analytics service (`backend/app/services/modal_analytics.py`) — weather impact analysis, disruption vulnerability, carpool supply vs demand
- `GET /modal/shadow-zones` — identify employees without viable transport solutions
- `GET /modal/carpool-potential` — carpool supply vs demand per site
- 8 new Pydantic response schemas (GroupScore, TimeSlotScore, ShadowZoneEmployee, MobilityScoresResponse, WeatherImpact, DisruptionVulnerability, CarpoolPotential, ShiftAnalysisResponse)
- 6 new tests in `test_mobility_scoring.py`

### Changed
- `GET /modal/mobility-scores` — now returns group_scores and timeslot_scores alongside individual scores
- `GET /modal/shift-analysis` — enhanced with disruption vulnerability and weather impact data, added site_id filter
- Scoring algorithm rewritten: base=0 with weighted factors (distance, mode, interest, flexibility) replacing old base=50 approach

---

## [Session-16] — 2026-04-01
### Added
- ModalAnalysisPage — 5 dashboard cards: distribution pie chart, shift potential bar, distance histogram, mobility scores, shift analysis
- Reusable Recharts components: PieChart, BarChart, Histogram with design system tokens
- Modal API client and TypeScript types (`frontend/src/api/modal.ts`, `types/modal.ts`)
- Site filter dropdown for per-site analysis
- i18n translations (16 keys in `modal` namespace)
- 3 component tests with Recharts mocking

### Changed
- Sidebar — added "Analyse Modale" navigation link
- routes.tsx — added /modal-analysis route

---

## [Session-15] — 2026-04-01
### Added
- EmployeeModal SQLAlchemy model with 17 data columns, unique(employee_id) constraint (`backend/app/models/modal.py`)
- Alembic migration for employee_modal table
- Pydantic schemas with transport mode enum validation, stats/score models (`backend/app/schemas/modal.py`)
- 6 API endpoints: CRUD upsert for employee modal, distribution stats, shift analysis, mobility scores (`backend/app/api/v1/modal.py`)
- 9 test cases covering upsert, stats, scores, and mode validation

---

## [Session-14] — 2026-04-01
### Added
- ExcelImportPage — multi-step flow (upload -> preview -> import) with per-sheet tabs
- FileUpload — drag-and-drop component with .xlsx validation and loading state
- Tabs — horizontal tab navigation with badge counts
- ProgressBar — animated progress indicator with 3 variants
- SheetPreview — auto-column data table with truncation
- ValidationErrors — grouped error display with row/column references
- Import API client (preview, import, single-sheet) with FormData upload
- 5 component tests

### Changed
- Sidebar — added Import navigation link
- routes.tsx — added /import route

---

## [Session-13] — 2026-04-01
### Added
- ExcelImportService — multi-sheet parser for 6-sheet template (SITES, EFFECTIF, USAGES, CONTRAINTES, PARC, ABSENCES) with upsert, validation, preview mode (`backend/app/services/excel_parser.py`)
- Response schemas for import results (`backend/app/schemas/excel_import.py`)
- 3 API endpoints: full import, preview, single-sheet import (`backend/app/api/v1/excel_import.py`)
- 13 test cases with programmatic Excel fixture generation

---

## [Session-12] — 2026-04-01
### Added
- EmployeeLeave SQLAlchemy model with employee FK (CASCADE), date indexes (`backend/app/models/leave.py`)
- Alembic migration for employee_leave table
- Pydantic schemas with leave_type enum and date range validation (`backend/app/schemas/leave.py`)
- 5 CRUD endpoints with date range filtering, site_id filter via join, overlap detection (`backend/app/api/v1/leaves.py`)
- 8 test cases covering CRUD, validation, date filtering, and overlap conflict detection

---

## [Session-11] — 2026-04-01
### Added
- EmployeeMapPage — Full-screen Leaflet map with site-colored employee markers, glassmorphism filter panel, legend
- MapView, EmployeeMarker, SiteMarker — Reusable map components
- Bulk actions on EmployeeListPage: checkbox selection, CSV export, bulk soft-delete
- 2 component tests (MapView, EmployeeMapPage)

### Changed
- EmployeeListPage — Added selection state, bulk action bar, map view button

---

## [Session-10] — 2026-04-01
### Added
- Employee TypeScript types, API client (8 functions), Zustand store (`frontend/src/types/employee.ts`, `api/employees.ts`, `stores/employeeStore.ts`)
- EmployeeListPage — DataTable with 6 filters (site, shift, PMR, department, active, search), pagination, PMR/opt-in badges
- Shared EmployeeForm — 4 sections (identity, assignment, location/MapPicker, mobility with conditional carpool)
- EmployeeCreatePage, EmployeeEditPage (pre-filled), EmployeeDetailPage (dual-marker map + transport profile)
- i18n translations (70+ keys in `employees` namespace for FR/EN)
- 3 component tests

### Changed
- `frontend/src/routes.tsx` — Added /employees, /employees/new, /employees/:id, /employees/:id/edit

---

## [Session-09] — 2026-04-01
### Added
- Employee SQLAlchemy model with 30+ fields, PostGIS POINT geometry, GIST spatial index, unique (tenant_id, matricule) (`backend/app/models/employee.py`)
- Alembic migration for employee table with all indexes
- Pydantic schemas: EmployeeCreate/Update/Response, EmployeeSummary, CSVUploadResult (`backend/app/schemas/employee.py`)
- 8 API endpoints: list (7 filters + search + pagination), get, create (auto-geocode), update, soft-delete, CSV upload, batch geocode, summary (`backend/app/api/v1/employees.py`)
- Geocoding service via Nominatim with rate limiting (`backend/app/services/geocoding.py`)
- 13 test cases covering CRUD, filters, CSV upload, validation errors, PostGIS

### Changed
- `backend/requirements.txt` — added python-multipart for file uploads

---

## [Session-08] — 2026-04-01
### Added
- Badge component with 5 variants: success, warning, danger, info, neutral (`frontend/src/components/ui/Badge.tsx`)
- SiteSummaryCards — 3-column stat grid for employee/vehicle/PMR counts (`frontend/src/components/sites/SiteSummaryCards.tsx`)
- ShiftConfigPanel — Visual 24h shift timeline with proportional bars (`frontend/src/components/sites/ShiftConfigPanel.tsx`)
- 3 new component tests (Badge variants, summary counts, shift rendering)

### Changed
- SiteDetailPage — Full enhancement with summary API call, badges, shift panel, quick action links, notes section

---

## [Session-07] — 2026-04-01
### Added
- Site API client (`frontend/src/api/sites.ts`) — 7 functions for all CRUD operations
- Site TypeScript types (`frontend/src/types/site.ts`) — Site, SiteCreate, SiteUpdate, SiteSummary, SiteListParams
- Zustand site store (`frontend/src/stores/siteStore.ts`) — state + async actions for sites
- SiteListPage — DataTable with search bar, city/ZFE filters, pagination, action buttons
- SiteCreatePage + SiteForm — Full form with all fields organized in sections
- SiteEditPage — Pre-filled form reusing SiteForm
- SiteDetailPage — Read-only view with mini-map and summary cards
- MapPicker component — Leaflet click-to-place GPS picker with draggable marker
- i18n translations (fr/en) for all site-related strings
- 4 component tests with Leaflet mocking for jsdom

### Changed
- `frontend/src/routes.tsx` — Added /sites, /sites/new, /sites/:id, /sites/:id/edit routes

---

## [Session-06] — 2026-04-01
### Added
- Site SQLAlchemy model with PostGIS POINT geometry column and GIST spatial index (`backend/app/models/site.py`)
- Alembic migration for site table with GeoAlchemy2 geometry support
- Pydantic schemas: SiteCreate (with lat/lng/security_profile validation), SiteUpdate, SiteResponse, SiteSummary, SiteListResponse (`backend/app/schemas/site.py`)
- 7 CRUD API endpoints: list (paginated + city/ZFE filters), get by ID, get by code, create (with PostGIS ST_MakePoint), update (geom recalc), delete, summary (`backend/app/api/v1/sites.py`)
- 13 test cases covering all CRUD operations, validation, filters, and PostGIS geometry

---

## [Session-05] — 2026-04-01
### Added
- GitHub Actions CI pipeline (`.github/workflows/ci.yml`) — backend (ruff + mypy + pytest) and frontend (eslint + tsc + vitest)
- Ruff Python linting config (`backend/ruff.toml`) with FastAPI-compatible rules
- Mypy type checking config (`backend/mypy.ini`) with pydantic + sqlalchemy plugins
- Prettier config (`frontend/.prettierrc`) for consistent formatting
- Pre-commit hooks (`.pre-commit-config.yaml`) — ruff + prettier
- Backend scripts (`backend/scripts.sh`) — lint, format, test, seed, migrate commands
- Frontend scripts: `type-check`, `format`, `format:check` in package.json

### Fixed
- 3 B904 lint violations (raise-from-err) in auth middleware and endpoints
- 5 import sorting violations auto-fixed by ruff

---

## [Session-04] — 2026-04-01
### Added
- SQLAlchemy models: Tenant, User, Role, Permission, RolePermission (`backend/app/models/auth.py`)
- Alembic migration for all auth tables
- Pydantic v2 schemas for auth requests/responses (`backend/app/schemas/auth.py`)
- JWT auth middleware with OAuth2PasswordBearer (`backend/app/middleware/auth.py`)
- RBAC `require_role()` dependency factory (`backend/app/middleware/rbac.py`)
- Auth endpoints: POST login, POST logout, POST refresh, GET me (`backend/app/api/v1/auth.py`)
- User CRUD endpoints: GET list, POST create, PUT update, DELETE deactivate (`backend/app/api/v1/users.py`)
- Role CRUD endpoints: GET list, POST create, PUT update (`backend/app/api/v1/roles.py`)
- Tenant CRUD endpoints: GET list, POST create, PUT update (`backend/app/api/v1/tenants.py`)
- Password hashing (bcrypt) and JWT encode/decode utilities (`backend/app/utils/security.py`)
- Seed data script: default tenant, 5 system roles, admin user (`backend/app/scripts/seed_data.py`)
- 11 new tests: auth flow (8) + user management (3)

### Changed
- `backend/app/database.py` — `get_db` uses `session.begin()` context, NullPool in test mode
- `backend/requirements.txt` — added bcrypt==4.2.1, pydantic[email]

---

## [Session-03] — 2026-04-01
### Added
- Vite React TypeScript project with strict mode
- TailwindCSS v4 with full design system tokens (`@theme` block in index.css)
- Layout shell: `AppLayout`, `Sidebar` (NavLink-based navigation), `Header` (language toggle, user display)
- 7 base UI components: `Button` (4 variants), `Input`, `Card`, `DataTable` (generic typed), `Modal`, `Toast`, `Skeleton`
- Routing with lazy-loaded pages (`routes.tsx` using `createBrowserRouter`)
- Zustand auth store (`useAuthStore`) with localStorage persistence
- Axios API client with JWT interceptors
- i18n configuration (French default, English fallback) with translation stubs
- Placeholder pages: `DashboardPage`, `LoginPage`
- `frontend/Dockerfile` (multi-stage Node 18 build + nginx serve)
- Vitest test setup with jsdom + React Testing Library
- 8 tests: AppLayout render, Button variants/loading/disabled, Card render, routing navigation

---

## [Session-02] — 2026-04-01
### Added
- `backend/app/config.py` — Pydantic Settings loading from `.env`
- `backend/app/database.py` — SQLAlchemy async engine, session factory, `get_db` dependency
- `backend/app/models/base.py` — `BaseModel` with UUID pk + `TimestampMixin` (created_at, updated_at)
- `backend/app/api/v1/health.py` — Health endpoint checking DB and Redis connectivity
- `backend/app/api/v1/__init__.py` — API v1 router aggregation
- `backend/alembic.ini` + `alembic/env.py` — Async Alembic configured with PostGIS table exclusion
- `backend/tests/conftest.py` — Async test client fixture (httpx + ASGITransport)
- `backend/tests/test_health.py` — 4 tests (root, health, docs, openapi schema)
- `backend/pytest.ini` — Pytest async mode config

### Changed
- `backend/app/main.py` — Added lifespan events, API router inclusion, config-driven settings

---

## [Session-01] — 2026-04-01
### Added
- Monorepo directory structure (`backend/`, `frontend/`, `mobile/`)
- Backend FastAPI skeleton with `app/` package and all sub-modules (models, schemas, api, services, middleware, tasks, utils)
- `backend/requirements.txt` with all core dependencies (FastAPI, SQLAlchemy, GeoAlchemy2, Celery, OR-Tools, scikit-learn)
- `backend/Dockerfile` (Python 3.11 slim with PostGIS system dependencies)
- `backend/.env.example` with all environment variables
- `docker-compose.yml` with 4 services: PostgreSQL 15 + PostGIS 3.4, Redis 7, OSRM, FastAPI backend
- `.env` with default development values
- `frontend/package.json` placeholder scaffold
- Root `README.md` with quick start instructions and access URLs
- Minimal FastAPI app with `/` and `/health` endpoints

---

## [Session-00] — 2026-03-24
### Added
- Claude Code configuration (`.claude/` directory with settings, rules, agents, skills)
- `CLAUDE.md` root context file with `@import` directives
- Obsidian vault enhancements (`INDEX.md`, `CHANGELOG.md`, ADR template)
- `.gitignore` for Python, Node, Flutter, IDE, and secrets
- Git repository initialized
