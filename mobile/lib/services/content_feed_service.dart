import 'package:hive_flutter/hive_flutter.dart';

import '../models/content_feed.dart';
import 'api_client.dart';

class ContentFeedService {
  final ApiClient _apiClient;
  static const String _cacheBoxName = 'content_feed_cache';

  ContentFeedService({required ApiClient apiClient}) : _apiClient = apiClient;

  /// Fetch personalized feed from API.
  Future<List<FeedContent>> fetchFeed({
    required String employeeId,
    int page = 1,
    int pageSize = 20,
  }) async {
    final response = await _apiClient.dio.get(
      '/content/feed',
      queryParameters: {
        'employee_id': employeeId,
        'page': page,
        'page_size': pageSize,
      },
    );
    final data = response.data['data'] as List? ?? [];
    final items = data.map((item) => FeedContent.fromJson(item)).toList();

    // Cache for offline use
    await _cacheItems(items);

    return items;
  }

  /// Get single content item.
  Future<FeedContent> getContent(String contentId) async {
    final response = await _apiClient.dio.get('/content/$contentId');
    return FeedContent.fromJson(response.data);
  }

  /// Mark content as viewed.
  Future<void> markViewed(String contentId, String employeeId) async {
    await _apiClient.dio.post(
      '/content/$contentId/view',
      queryParameters: {'employee_id': employeeId},
    );
  }

  /// Mark content as completed.
  Future<void> markCompleted(
    String contentId,
    String employeeId, {
    int? timeSpentSeconds,
  }) async {
    await _apiClient.dio.post(
      '/content/$contentId/complete',
      queryParameters: {'employee_id': employeeId},
      data: {
        if (timeSpentSeconds != null) 'time_spent_seconds': timeSpentSeconds,
      },
    );
  }

  /// Cache items locally with Hive.
  Future<void> _cacheItems(List<FeedContent> items) async {
    try {
      final box = await Hive.openBox(_cacheBoxName);
      final jsonList = items.map((i) => i.toJson()).toList();
      await box.put('feed_items', jsonList);
      await box.put('cached_at', DateTime.now().toIso8601String());
    } catch (_) {
      // Non-critical — cache failure shouldn't block the user
    }
  }

  /// Get cached items for offline access.
  Future<List<FeedContent>> getCachedFeed() async {
    try {
      final box = await Hive.openBox(_cacheBoxName);
      final data = box.get('feed_items');
      if (data == null) return [];
      final list = (data as List).map((e) => Map<String, dynamic>.from(e)).toList();
      return list.map((item) => FeedContent.fromJson(item)).toList();
    } catch (_) {
      return [];
    }
  }

  /// Check if cached data is stale (> 30 minutes).
  Future<bool> isCacheStale() async {
    try {
      final box = await Hive.openBox(_cacheBoxName);
      final cachedAt = box.get('cached_at') as String?;
      if (cachedAt == null) return true;
      final cachedTime = DateTime.parse(cachedAt);
      return DateTime.now().difference(cachedTime).inMinutes > 30;
    } catch (_) {
      return true;
    }
  }
}
