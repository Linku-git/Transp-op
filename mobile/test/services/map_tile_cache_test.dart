import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/services/map_tile_cache.dart';

void main() {
  group('MapTileCache', () {
    test('starts with no cached regions', () {
      final cache = MapTileCache();
      expect(cache.cachedRegionCount, 0);
    });

    test('preCacheCommuteArea adds regions', () async {
      final cache = MapTileCache();
      await cache.preCacheCommuteArea(
        homeLat: 33.58,
        homeLng: -7.63,
        siteLat: 33.55,
        siteLng: -7.60,
      );
      expect(cache.cachedRegionCount, 2);
    });

    test('isRegionCached returns correct state', () async {
      final cache = MapTileCache();
      await cache.preCacheCommuteArea(
        homeLat: 33.58,
        homeLng: -7.63,
        siteLat: 33.55,
        siteLng: -7.60,
      );
      expect(cache.isRegionCached('home_33.58_-7.63'), true);
      expect(cache.isRegionCached('unknown'), false);
    });

    test('clearCache removes all regions', () async {
      final cache = MapTileCache();
      await cache.preCacheCommuteArea(
        homeLat: 33.58,
        homeLng: -7.63,
        siteLat: 33.55,
        siteLng: -7.60,
      );
      cache.clearCache();
      expect(cache.cachedRegionCount, 0);
    });
  });
}
