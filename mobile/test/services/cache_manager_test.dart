import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/config/cache_config.dart';

void main() {
  group('CacheConfig', () {
    test('TTLs are configured', () {
      expect(CacheConfig.userProfileTtl.inHours, 24);
      expect(CacheConfig.upcomingTripsTtl.inHours, 1);
      expect(CacheConfig.contentFeedTtl.inHours, 6);
      expect(CacheConfig.rtiEtaTtl.inSeconds, 30);
    });

    test('storage limits are reasonable', () {
      expect(CacheConfig.maxTotalBytes, greaterThan(0));
      expect(CacheConfig.maxMapTileBytes, lessThan(CacheConfig.maxTotalBytes));
    });

    test('manifest sync interval is 6 hours', () {
      expect(CacheConfig.manifestSyncInterval.inHours, 6);
    });

    test('queue settings are configured', () {
      expect(CacheConfig.maxQueueRetries, 3);
      expect(CacheConfig.queueRetryDelay.inSeconds, 5);
    });

    test('hive box names are defined', () {
      expect(CacheConfig.userProfileBox, isNotEmpty);
      expect(CacheConfig.tripsBox, isNotEmpty);
      expect(CacheConfig.settingsBox, isNotEmpty);
      expect(CacheConfig.offlineQueueBox, isNotEmpty);
    });
  });
}
