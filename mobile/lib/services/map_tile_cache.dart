import 'package:logger/logger.dart';

final _log = Logger();

class MapTileCache {
  /// Pre-cache map tiles for the user's commute area.
  /// In production, this would use google_maps_flutter's tile caching
  /// or a custom tile downloader. For now, this is a placeholder
  /// that tracks which areas should be cached.

  final Set<String> _cachedRegions = {};

  bool isRegionCached(String regionKey) => _cachedRegions.contains(regionKey);

  Future<void> preCacheCommuteArea({
    required double homeLat,
    required double homeLng,
    required double siteLat,
    required double siteLng,
    double homeRadiusKm = 3.0,
    double siteRadiusKm = 2.0,
  }) async {
    // In production: download map tiles for these areas at zoom 12-16
    // For now, register the areas as "cached"
    final homeKey = 'home_${homeLat.toStringAsFixed(2)}_${homeLng.toStringAsFixed(2)}';
    final siteKey = 'site_${siteLat.toStringAsFixed(2)}_${siteLng.toStringAsFixed(2)}';

    _cachedRegions.add(homeKey);
    _cachedRegions.add(siteKey);

    _log.d('Pre-cached map tiles for home ($homeKey) and site ($siteKey)');
  }

  int get cachedRegionCount => _cachedRegions.length;

  void clearCache() {
    _cachedRegions.clear();
  }
}
