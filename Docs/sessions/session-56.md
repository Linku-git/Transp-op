# Session 56 — Offline Mode

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-45|Session 45]], [[sessions/session-54|Session 54]]
## Complexity: High
> Previous: [[sessions/session-55|Session 55]] | Next: [[sessions/session-57|Session 57]]

## Objective
Implement comprehensive offline support using Hive and SQLite for local storage, a write queue for deferred operations, and connectivity-aware caching to ensure the app remains functional without network access.

---

## Tasks
- [ ] Implement Hive storage for: user profile, trip data, and settings cache
- [ ] Implement SQLite storage for: trip history, content library, and notifications
- [ ] Create ConnectivityService (using connectivity_plus) to detect online, offline, and degraded network states
- [ ] Create OfflineQueue to queue write operations when offline and sync automatically on reconnect
- [ ] Create CacheManager with stale-while-revalidate pattern and TTL management
- [ ] Implement offline manifest sync on app launch and every 6 hours on WiFi
- [ ] Add UI indicators: offline banner, stale data badge, sync spinner
- [ ] Pre-cache map tiles for the user's commute area

## Files to Create/Modify
- `mobile/lib/services/connectivity_service.dart`
- `mobile/lib/services/offline_queue.dart`
- `mobile/lib/services/cache_manager.dart`
- `mobile/lib/services/hive_storage_service.dart`
- `mobile/lib/services/sqlite_storage_service.dart`
- `mobile/lib/services/offline_manifest_sync.dart`
- `mobile/lib/services/map_tile_cache.dart`
- `mobile/lib/providers/connectivity_provider.dart`
- `mobile/lib/widgets/offline_banner.dart`
- `mobile/lib/widgets/stale_data_badge.dart`
- `mobile/lib/widgets/sync_spinner.dart`
- `mobile/lib/config/cache_config.dart`

## Tests
- [ ] Offline data access works for user profile, trips, and settings
- [ ] OfflineQueue stores write operations when offline
- [ ] OfflineQueue replays and syncs queued operations on reconnect
- [ ] ConnectivityService correctly detects online, offline, and degraded states
- [ ] CacheManager serves stale data while revalidating in background
- [ ] TTL expiration triggers data refresh
- [ ] Offline manifest syncs on app launch
- [ ] Offline manifest syncs every 6 hours on WiFi
- [ ] Offline banner appears when network is unavailable
- [ ] Stale data badge shows when cached data exceeds TTL
- [ ] Sync spinner displays during active synchronization

## Acceptance Criteria
- App remains fully navigable and displays cached data when offline
- User profile, upcoming trips, and settings are available from Hive storage without network
- Trip history, content, and notifications are available from SQLite without network
- Write operations (bookings, cancellations) are queued when offline and executed on reconnect
- Queue sync handles conflicts and retries failed operations
- CacheManager implements stale-while-revalidate: serves cached data immediately, refreshes in background
- TTL is configurable per data type
- Offline manifest downloads on first launch and refreshes every 6 hours over WiFi
- UI clearly indicates offline status with a banner
- Stale data is flagged with a visual badge
- Active sync operations show a spinner indicator
- Map tiles for the commute area are pre-cached for offline map viewing

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
