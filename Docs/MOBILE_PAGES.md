# Transpop — Mobile App Pages (Flutter — iOS + Android)

> See also: [[FRONTEND_PAGES]] | [[API_ENDPOINTS]] | [[LOCAL_MOBILE_FUNCTIONALITY]] | [[agents]]

## App Architecture

- **State Management:** Riverpod (or Provider)
- **Navigation:** GoRouter (declarative routing)
- **Theme:** Light + Dark (Night Mode) with high contrast
- **Languages:** French (primary), English

---

## Screen Map

```
/splash                 -> SplashScreen
/login                  -> LoginScreen
/onboarding             -> OnboardingFlow (multi-step)
/home                   -> HomeScreen
/trips                  -> TripsScreen
/trips/book             -> TripBookingScreen
/trips/:id              -> TripDetailScreen
/trips/history          -> TripHistoryScreen
/tracking               -> RTITrackingScreen
/tracking/map           -> FullMapScreen
/content                -> ContentFeedScreen
/content/:id            -> ContentDetailScreen
/content/training/:id   -> TrainingPlayerScreen
/content/survey/:id     -> SurveyScreen
/profile                -> ProfileScreen
/profile/edit           -> EditProfileScreen
/profile/preferences    -> PreferencesScreen
/profile/security       -> SecurityQuestionnaireScreen
/stats                  -> StatisticsScreen
/emergency              -> EmergencyScreen (overlay)
/notifications          -> NotificationListScreen
```

---

## Screens by Flow

### 1. Authentication (Session 46)

#### SplashScreen `/splash`
- App logo animation
- Auto-login check (stored refresh token)
- Redirect to `/login` or `/home`

#### LoginScreen `/login`
- Company logo + app name
- "Login with SSO" button (Auth0/Keycloak OIDC)
- Email/password fallback option
- MFA challenge input (if required)
- Language selector bottom sheet (FR/EN)
- "Contact support" link

---

### 2. Onboarding (Session 47)

#### OnboardingFlow `/onboarding` (4-step wizard)

**Step 1: Welcome**
- App introduction carousel (3 slides)
- "What Transpop does for you" benefits

**Step 2: Transport Preferences**
- Current transport mode selector (icon grid)
- Interest in company transport (Oui/Non/Sous conditions)
- Has personal car toggle
- Volunteer driver toggle (if car = yes)
- Carpool seats available
- Max walking distance slider (200m-2km)
- Preferred pickup point (map picker)

**Step 3: Security Questionnaire**
- Overall safety perception (1-5 stars)
- Time slots feeling vulnerable (multi-select)
- Zones of concern (map pin placement)
- Night/early morning concerns (text input)
- Max walk distance at night slider

**Step 4: Permissions**
- Location permission request (active only, explain why)
- Notification permission request (explain benefit: D-2min alerts)
- "Get Started" button

---

### 3. Home Screen (Session 48)

#### HomeScreen `/home`
- **Top Bar:** Greeting ("Bonjour, {name}"), notification bell icon
- **Next Departure Card (prominent):**
  - Departure time (large font)
  - Time remaining countdown
  - Colored indicator: Green (>5min), Orange (2-5min), Red (<2min)
  - Pickup point name + walking time
  - Vehicle info (type, route name)
  - "View on Map" button
- **Quick Actions Row:**
  - Book Trip (icon + label)
  - View Map (icon + label)
  - My Trips (icon + label)
- **Content Carousel:**
  - Horizontal scroll cards (latest 5 content items)
  - Corporate news, training badges, safety reminders
  - Tap to open content detail
- **Night Mode:**
  - Emergency button (large, prominent) — visible only during night hours
  - Dark background, high contrast text
- **Bottom Navigation Bar:**
  - Home | Trips | Track | Content | Profile

---

### 4. Trip Management (Sessions 49-50)

#### TripBookingScreen `/trips/book`
- Date picker (today + next 7 days)
- Shift selector (from employee's site shifts)
- Pickup point:
  - Default: assigned gathering point
  - "Change pickup" -> map picker with nearby stops
- Summary card (date, shift, pickup, ETA)
- "Confirm Booking" button
- Cancellation policy notice (30 min before departure)

#### TripsScreen `/trips`
- **Upcoming tab:** Next booked trips (cards)
  - Each card: date, shift, pickup, status, modify/cancel buttons
- **Past tab:** Trip history (list)
  - Each item: date, route, duration, CO2 saved

#### TripDetailScreen `/trips/:id`
- Trip details card
- Mini-map: route from pickup to site
- Status timeline: Booked -> Confirmed -> In Progress -> Completed
- CO2 saved badge
- Cancel/modify buttons (if upcoming, >30 min)

#### TripHistoryScreen `/trips/history`
- Monthly grouped trip list
- Stats header: total trips, total CO2 saved, total km
- Filter: month picker

---

### 5. RTI & Tracking (Session 51)

#### RTITrackingScreen `/tracking`
- **Vehicle Arrival Card:**
  - ETA countdown (seconds, large font)
  - Colored indicator: Green (<=90s) / Orange (90-180s) / Red (>180s)
  - Vehicle type + driver name
  - Route name
- **Mini Map:**
  - Current location (blue dot)
  - Gathering point (marker)
  - Approaching vehicle (animated marker)
  - Dashed line: employee -> gathering point
  - Solid line: vehicle route
- **Push alert trigger:** D-2 minutes notification
- "Full Map" button -> FullMapScreen

#### FullMapScreen `/tracking/map`
- Full-screen Google Maps
- Vehicle position (real-time, updated <=10s)
- Route polyline
- All stops on route with ETA labels
- Employee location
- Gathering point with walking directions
- Back button

---

### 6. Content & Training (Sessions 70-73)

#### ContentFeedScreen `/content` ✅ Session 70
- **Tabs:** All | News | Training | Safety | Surveys (FilterChip horizontal scroll)
- `ContentCard` widget: title, snippet (HTML-stripped), type badge with icon+color, date, media thumbnail or icon placeholder, "NEW" badge for undelivered, check icon for completed
- `ContentTabs` widget: horizontal filter chip tabs with icons
- Pull-to-refresh via `RefreshIndicator`
- `OfflineIndicator` banner when displaying Hive-cached content
- Loading/error/empty states
- Riverpod `ContentFeedProvider` with type filtering + offline fallback
- `ContentFeedService` with Hive caching (30-min TTL)

#### ContentDetailScreen `/content/:id` ✅ Session 70
- Full article view with `SingleChildScrollView`
- Type badge, title, date, media (image or video placeholder)
- Rich text body rendering (simple HTML-to-text with paragraph/heading/list support)
- "Mark as Read" auto-trigger at 90% scroll completion
- Records view + completion events with time_spent_seconds via engagement API
- `FutureProvider.family` for content detail loading

#### TrainingPlayerScreen `/content/training/:id` ✅ Session 71
- `TrainingMediaPlayer` widget: `video_player` integration with `VideoPlayerController.networkUrl`
  - Play/pause, seek forward/backward 10s, progress slider
  - Audio visual mode (icon + waveform placeholder) for .mp3/.wav
  - Loading/error states for media initialization
- Quiz section (appears after media completion):
  - `QuizSection` widget: multiple choice `QuizQuestionWidget` with radio-button selection
  - Progress counter (answered/total), submit button (disabled until all answered)
  - `ScoreDisplay` widget: trophy (pass) or retry (fail), score %, correct count, passing threshold
  - Retry button resets answers for failed quizzes
- Completion certificate link placeholder (if passed)
- Live time tracking in app bar (`StreamBuilder` with 1-second ticker, mm:ss format)
- `TrainingContent` model: title, body, mediaUrl, mediaType, questions, passingScore
- `TrainingService`: API fetch, quiz score submission, Hive offline caching
- `TrainingPlayerProvider`: Riverpod state for playback, quiz flow, time tracking

#### SurveyScreen `/content/survey/:id` ✅ Session 73
- Survey title + description display
- 5 question type widgets: `RadioQuestion` (RadioListTile), `CheckboxQuestion` (CheckboxListTile), `TextQuestion` (TextField), `RatingQuestion` (1-5 star icons), `SliderQuestion` (Slider with min/max/value labels)
- `SurveyProgress` widget: "Question X sur Y" + answered count + LinearProgressIndicator
- Submit button with required-field validation (disabled until all required answered)
- `AnonymousIndicator` banner with visibility_off icon for anonymous surveys
- Thank you confirmation screen (check_circle icon + "Merci !" + return button)
- `SurveyService`: API submit + Hive offline queue with `submitQueuedResponses()` auto-retry
- `SurveyScreenProvider`: Riverpod state for answers, validation, submission, offline fallback
- Loading/error/empty states

---

### 7. Profile & Preferences (Session 53)

#### ProfileScreen `/profile`
- Avatar + name + matricule
- Site name + shift
- Transport mode badge
- **Quick Stats:** Total trips, CO2 saved, training completed
- **Menu Items:**
  - Edit Profile
  - Transport Preferences
  - Security Questionnaire
  - Notification Settings
  - Language (FR/EN)
  - Night Mode toggle
  - About / Help
  - Logout

#### EditProfileScreen `/profile/edit`
- Phone number
- Preferred pickup address (map picker)
- PMR flag toggle
- Read-only fields: name, matricule, site (from SIRH)

#### PreferencesScreen `/profile/preferences`
- Transport mode selector
- Max walking distance slider
- Volunteer driver toggle
- Carpool seats slider
- Notification granularity:
  - RTI alerts: On/Off
  - Route changes: On/Off
  - Content notifications: On/Off
  - Weather alerts: On/Off
- Auto night mode toggle + custom hours

---

### 8. Security (Sessions 61, 65)

#### SecurityQuestionnaireScreen `/profile/security`
- Same form as onboarding step 3 (reusable)
- Overall safety rating
- Vulnerable time slots
- Map pin: zones of concern
- Night concerns text
- Last submitted date display
- "Update Questionnaire" button

#### EmergencyScreen `/emergency` (overlay)
- **Full screen red overlay**
- "EMERGENCY ACTIVATED" message
- Location sharing indicator (live GPS)
- "Sending alert to:" list (security contact, admin)
- "Call Emergency Services" button (direct dial)
- Cancel button (with confirmation: "Are you sure you're safe?")
- Auto-timeout: returns to normal after resolution

---

### 9. Statistics (Session 55)

#### StatisticsScreen `/stats`
- **Period selector:** This month / This year / All time
- **Cards:**
  - Total trips taken
  - Total distance (km)
  - CO2 saved (kg)
  - Training modules completed
  - Quiz average score
- **Charts:**
  - Monthly trips bar chart
  - CO2 savings trend line
  - Transport mode usage pie
- "Share my impact" button (generates shareable card)

---

### 10. Notifications (Session 52)

#### NotificationListScreen `/notifications`
- Grouped by date
- Types with icons:
  - RTI alert (bus icon)
  - Route change (map icon)
  - Weather (cloud icon)
  - Content (book icon)
  - Emergency (shield icon)
- Tap to navigate to relevant screen
- Swipe to dismiss
- "Mark all read" button

---

## Night Mode Specifics (Session 65)

When active (20h-6h30 or manual toggle):
- **Dark theme:** Dark background (#1a1a2e), high-contrast text (#e0e0e0)
- **Emergency button:** Always visible at bottom of home screen (red, large)
- **Reduced brightness** suggestion
- **Simplified UI:** Only essential info (next departure, tracking, emergency)
- **Battery optimization:** Reduced animations, darker colors

---

## Bottom Navigation

| Tab | Icon | Screen | Badge |
|-----|------|--------|-------|
| Home | house | HomeScreen | Upcoming trip indicator |
| Trips | calendar | TripsScreen | Pending bookings count |
| Track | location | RTITrackingScreen | Live tracking dot |
| Content | book | ContentFeedScreen | Unread count |
| Profile | person | ProfileScreen | — |

---

## Accessibility Requirements

- VoiceOver (iOS) and TalkBack (Android) full support
- All interactive elements have accessibility labels
- Minimum touch target: 48x48dp
- Text scalable (supports system font size)
- Color contrast: 4.5:1 minimum (7:1 for night mode)
- Screen reader announcements for status changes (countdown, alerts)

---
## Related Documentation
- [[FRONTEND_PAGES]] — Web dashboard pages (React)
- [[API_ENDPOINTS]] — Backend API endpoints
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline, caching, local storage
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Data models
- [[PROGRESS]] — Implementation status
