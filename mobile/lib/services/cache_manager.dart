import 'dart:async';
import 'package:logger/logger.dart';
import 'hive_storage_service.dart';
import 'connectivity_service.dart';

final _log = Logger();

class CacheManager {
  final HiveStorageService _hive;
  final ConnectivityService _connectivity;

  CacheManager({
    required HiveStorageService hive,
    required ConnectivityService connectivity,
  })  : _hive = hive,
        _connectivity = connectivity;

  /// Stale-while-revalidate pattern:
  /// 1. Return cached data immediately if available
  /// 2. If stale or missing and online, fetch fresh in background
  /// 3. If offline and cache exists, return stale data
  /// 4. If offline and no cache, return null
  Future<T?> getOrFetch<T>({
    required String cacheKey,
    required Duration ttl,
    required Future<T> Function() fetcher,
    required Future<void> Function(T data) cacher,
    required T? Function() cacheReader,
  }) async {
    final cached = cacheReader();
    final isStale = _hive.isStale(cacheKey, ttl);

    if (cached != null && !isStale) {
      return cached;
    }

    if (cached != null && isStale) {
      // Serve stale, refresh in background if online
      if (_connectivity.isOnline) {
        unawaited(_refreshInBackground(fetcher, cacher, cacheKey));
      }
      return cached;
    }

    // No cache — must fetch
    if (_connectivity.isOnline) {
      try {
        final fresh = await fetcher();
        await cacher(fresh);
        return fresh;
      } catch (e) {
        _log.w('Failed to fetch $cacheKey: $e');
        return cached; // Still null
      }
    }

    return null;
  }

  Future<void> _refreshInBackground<T>(
    Future<T> Function() fetcher,
    Future<void> Function(T data) cacher,
    String cacheKey,
  ) async {
    try {
      final fresh = await fetcher();
      await cacher(fresh);
      _log.d('Background refresh for $cacheKey complete');
    } catch (e) {
      _log.w('Background refresh for $cacheKey failed: $e');
    }
  }

  /// Check if data is stale
  bool isStale(String key, Duration ttl) => _hive.isStale(key, ttl);

  /// Get the age of cached data
  Duration? getAge(String key) {
    final cachedAt = _hive.getCachedAt(key);
    if (cachedAt == null) return null;
    return DateTime.now().difference(cachedAt);
  }

  /// Format staleness for display
  String? getStaleLabel(String key, Duration ttl) {
    final age = getAge(key);
    if (age == null) return null;
    if (age <= ttl) return null;

    if (age.inMinutes < 60) return 'Mis à jour il y a ${age.inMinutes} min';
    if (age.inHours < 24) return 'Mis à jour il y a ${age.inHours}h';
    return 'Mis à jour il y a ${age.inDays}j';
  }
}
