class CacheConfig {
  CacheConfig._();

  // TTL per data type
  static const Duration userProfileTtl = Duration(hours: 24);
  static const Duration upcomingTripsTtl = Duration(hours: 1);
  static const Duration contentFeedTtl = Duration(hours: 6);
  static const Duration rtiEtaTtl = Duration(seconds: 30);
  static const Duration appSettingsTtl = Duration(hours: 24);
  static const Duration notificationsTtl = Duration(hours: 6);

  // Manifest sync interval
  static const Duration manifestSyncInterval = Duration(hours: 6);

  // Storage limits (bytes)
  static const int maxTextContentBytes = 10 * 1024 * 1024; // 10 MB
  static const int maxMapTileBytes = 50 * 1024 * 1024; // 50 MB
  static const int maxTotalBytes = 300 * 1024 * 1024; // 300 MB

  // Queue settings
  static const int maxQueueRetries = 3;
  static const Duration queueRetryDelay = Duration(seconds: 5);

  // Hive box names
  static const String userProfileBox = 'user_profile';
  static const String tripsBox = 'trips';
  static const String settingsBox = 'settings';
  static const String cacheMetaBox = 'cache_meta';
  static const String offlineQueueBox = 'offline_queue';
}
