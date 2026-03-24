# Transpop — Local Mobile Functionality (Offline, Caching, Storage)

> See also: [[MOBILE_PAGES]] | [[API_ENDPOINTS]] | [[ARCHITECTURE]] | [[agents]]

## Overview

The mobile app must function gracefully with degraded or no connectivity. Employees may be in areas with poor network coverage (industrial zones, rural areas) or underground (metro, parking). The offline strategy ensures critical trip information is always available.

---

## Storage Technologies

| Technology | Purpose | Data Type |
|-----------|---------|-----------|
| **Hive** | Fast key-value local storage | User profile, settings, cached API responses |
| **SQLite** | Structured relational queries | Trip history, content library, notifications |
| **Shared Preferences** | Simple flags and settings | Auth tokens, theme preference, language |
| **File System** | Media files | Downloaded training videos, images, PDFs |

---

## Offline Data Strategy

### Always Available Offline (pre-cached)

| Data | Storage | Refresh | Size Estimate |
|------|---------|---------|---------------|
| User profile | Hive | On login + on change | <1 KB |
| Current/next booked trip details | Hive | On booking + D-1 day | <5 KB |
| Assigned pickup point (GPS + name) | Hive | On optimization change | <1 KB |
| Site info (name, address, shifts) | Hive | Daily | <2 KB |
| Route info (stops, schedule) | SQLite | On optimization change | <10 KB |
| Last 30 days trip history | SQLite | On trip completion | <50 KB |
| Downloaded training content | File System | On user request | Variable (5-50 MB) |
| Offline content library (text) | SQLite | Daily sync | <500 KB |
| Notification history (last 50) | SQLite | On new notification | <20 KB |
| Emergency contacts | Hive | On change | <1 KB |

### Requires Connectivity

| Feature | Fallback When Offline |
|---------|----------------------|
| Real-time vehicle tracking (RTI) | Show "Last known position" + scheduled time |
| Trip booking/modification | Queue action, sync when online |
| Content feed (new items) | Show cached content with "offline" badge |
| Quiz submission | Store locally, submit on reconnect |
| Emergency alert | Attempt send, fallback to direct phone call |
| Push notifications | Missed until reconnect (FCM handles retry) |
| Map tiles | Cached tiles for recent area, blank for new areas |

---

## Offline Manifest API

**Endpoint:** `GET /mobile/offline-manifest`

Returns a package of all data the app should cache for offline use:

```json
{
  "user_profile": { ... },
  "upcoming_trips": [ ... ],
  "assigned_pickup": { "lat": 33.5, "lng": -7.6, "name": "Zone A" },
  "site_info": { "name": "Site Casablanca", "shifts": [...] },
  "route_info": { "stops": [...], "schedule": [...] },
  "content_library": [
    { "id": "...", "title": "...", "body": "...", "type": "news", "media_url": null },
    { "id": "...", "title": "...", "type": "training", "media_url": "https://..." }
  ],
  "emergency_contacts": [
    { "name": "Security Office", "phone": "+212..." },
    { "name": "Emergency", "phone": "112" }
  ],
  "last_updated": "2026-03-07T10:00:00Z"
}
```

**Sync triggers:**
- On app launch (if online)
- On login
- Every 6 hours (background)
- On push notification with `sync_required: true` flag
- Manual pull-to-refresh

---

## Caching Strategy

### API Response Caching (Hive)

```dart
// Cache structure
class CacheEntry {
  final String key;
  final dynamic data;
  final DateTime cachedAt;
  final Duration ttl;

  bool get isExpired => DateTime.now().difference(cachedAt) > ttl;
}
```

| API Call | Cache Key | TTL | Stale Strategy |
|----------|-----------|-----|----------------|
| GET /auth/me | `user_profile` | 24h | Serve stale, refresh in background |
| GET /trips/upcoming | `upcoming_trips` | 1h | Serve stale, refresh in background |
| GET /content/feed | `content_feed` | 6h | Serve stale, show "updating" indicator |
| GET /rti/stop/{id}/eta | `rti_eta_{stop_id}` | 30s | Show "last updated X ago" |
| GET /settings | `app_settings` | 24h | Serve stale |

### Stale-While-Revalidate Pattern

1. Check cache first
2. If cache hit and not expired: return cached data
3. If cache hit but expired: return cached data immediately, trigger background refresh
4. If cache miss: show loading, fetch from API, cache result
5. If fetch fails and cache exists (even expired): return stale data with warning

---

## Offline Queue (Write Operations)

When offline, write operations are queued locally and synced when connectivity returns.

### Queued Actions

| Action | Priority | Max Queue Time |
|--------|----------|----------------|
| Trip booking | High | 24h |
| Trip cancellation | High | Until departure time |
| Quiz submission | Medium | 7 days |
| Survey response | Medium | 7 days |
| Content "viewed" event | Low | 30 days |
| Security questionnaire | Medium | 7 days |
| Emergency alert | Critical | Retry immediately on reconnect |

### Queue Implementation

```dart
class OfflineQueue {
  // SQLite table: offline_queue
  // Columns: id, action_type, endpoint, method, body, priority, created_at, retry_count, max_retries

  Future<void> enqueue(QueuedAction action);
  Future<void> processQueue(); // Called on connectivity change
  Future<void> retryFailed();  // Exponential backoff
}
```

### Sync on Reconnect

1. Detect connectivity change (connectivity_plus package)
2. Process queue in priority order (Critical > High > Medium > Low)
3. For each action:
   - Attempt API call
   - On success: remove from queue, update local cache
   - On failure: increment retry count, exponential backoff
   - On permanent failure (4xx): remove from queue, notify user
4. After queue processed: trigger offline manifest refresh

---

## Content Download Manager

### Pre-download Strategy

Training modules and content can be pre-downloaded for offline consumption:

```dart
class ContentDownloadManager {
  // Download training videos/audio for offline
  Future<void> downloadContent(String contentId, String mediaUrl);

  // Check download status
  DownloadStatus getStatus(String contentId);

  // Get local file path for downloaded content
  String? getLocalPath(String contentId);

  // Manage storage: auto-delete oldest when >200MB used
  Future<void> cleanupStorage({int maxMB = 200});
}
```

### Storage Limits

| Content Type | Max Cache | Cleanup Policy |
|-------------|-----------|----------------|
| Text content (news, articles) | 10 MB | LRU, keep last 100 items |
| Training videos | 150 MB | Manual download, LRU cleanup |
| Training audio/podcasts | 50 MB | Manual download, LRU cleanup |
| Images | 30 MB | LRU, keep last 200 |
| Map tiles | 50 MB | LRU, keep recent area |
| **Total budget** | **~300 MB** | |

---

## Map Tile Caching

```dart
// flutter_map cached_network_image or custom tile provider
class OfflineMapTileProvider {
  // Cache tiles for the employee's commute area
  // Automatically cache tiles viewed in last 7 days
  // Pre-cache: employee home area + site area (zoom 12-16)
  // Max storage: 50 MB
}
```

### Pre-cached Areas
- Employee home location (3km radius, zoom 12-16)
- Assigned site location (2km radius, zoom 12-16)
- Route between home and site (along corridor, zoom 14-16)

---

## Authentication Offline Handling

| Scenario | Behavior |
|----------|----------|
| Token valid, offline | App works normally with cached data |
| Token expired, offline | Allow read-only access to cached data, queue writes |
| Token expired, online | Auto-refresh token, continue normally |
| Refresh token expired | Force re-login on next connectivity |
| No stored token | Login screen (requires connectivity) |

### Token Storage
- Access token: Secure storage (flutter_secure_storage)
- Refresh token: Secure storage
- Token expiry: Shared Preferences (for quick expiry check without decryption)

---

## Connectivity Detection

```dart
// Using connectivity_plus package
class ConnectivityService {
  Stream<ConnectivityStatus> get statusStream;

  // States: online, offline, degraded (slow connection)
  // On state change:
  //   online -> process offline queue, refresh manifest
  //   offline -> enable offline mode UI indicators
  //   degraded -> disable heavy operations (video streaming), queue writes
}
```

### UI Indicators

- **Offline banner:** Persistent top banner "You are offline. Some features may be limited."
- **Stale data indicator:** Small badge on data cards showing "Updated 2 hours ago"
- **Sync indicator:** Spinning icon when processing offline queue
- **Download progress:** Progress bar for content downloads

---

## Data Encryption at Rest

| Data | Encryption | Method |
|------|-----------|--------|
| Auth tokens | Yes | flutter_secure_storage (Keychain/Keystore) |
| User profile | No (non-sensitive) | Hive |
| Trip data | No (non-sensitive) | SQLite |
| Emergency contacts | No | Hive |
| Content text | No | SQLite |
| Downloaded media | No | File system |
| Offline queue | Yes (may contain PII) | Encrypted SQLite (sqflite_sqlcipher) |
| Security questionnaire | Yes | Encrypted Hive box |

---

## Background Sync

**Important: No background location tracking (RGPD compliance)**

Allowed background operations:
- Push notification handling (FCM)
- Offline queue sync (on connectivity change event only)
- Content pre-download (user-initiated, continues in background)
- Periodic manifest refresh (WorkManager / BGTaskScheduler, every 6h, only when on WiFi)

Explicitly NOT allowed:
- Background GPS collection
- Continuous location tracking
- Background analytics collection

---
## Related Documentation
- [[MOBILE_PAGES]] — Mobile app screens
- [[API_ENDPOINTS]] — Backend API (offline manifest endpoint)
- [[ARCHITECTURE]] — System architecture
- [[DATABASE_SCHEMA]] — Data models for cached data
- [[PROGRESS]] — Implementation status
