import 'package:hive_flutter/hive_flutter.dart';
import '../config/cache_config.dart';

class HiveStorageService {
  late Box<dynamic> _profileBox;
  late Box<dynamic> _tripsBox;
  late Box<dynamic> _settingsBox;
  late Box<dynamic> _cacheMetaBox;

  Future<void> initialize() async {
    await Hive.initFlutter();
    _profileBox = await Hive.openBox(CacheConfig.userProfileBox);
    _tripsBox = await Hive.openBox(CacheConfig.tripsBox);
    _settingsBox = await Hive.openBox(CacheConfig.settingsBox);
    _cacheMetaBox = await Hive.openBox(CacheConfig.cacheMetaBox);
  }

  // User profile
  Future<void> saveProfile(Map<String, dynamic> profile) async {
    await _profileBox.put('current', profile);
    await _setCachedAt('profile');
  }

  Map<String, dynamic>? getProfile() {
    final data = _profileBox.get('current');
    return data != null ? Map<String, dynamic>.from(data) : null;
  }

  // Trips
  Future<void> saveTrips(String key, List<Map<String, dynamic>> trips) async {
    await _tripsBox.put(key, trips);
    await _setCachedAt('trips_$key');
  }

  List<Map<String, dynamic>> getTrips(String key) {
    final data = _tripsBox.get(key);
    if (data == null) return [];
    return (data as List).map((e) => Map<String, dynamic>.from(e)).toList();
  }

  // Settings
  Future<void> saveSetting(String key, dynamic value) async {
    await _settingsBox.put(key, value);
  }

  T? getSetting<T>(String key) {
    return _settingsBox.get(key) as T?;
  }

  // Cache metadata
  Future<void> _setCachedAt(String key) async {
    await _cacheMetaBox.put('${key}_cached_at', DateTime.now().toIso8601String());
  }

  DateTime? getCachedAt(String key) {
    final value = _cacheMetaBox.get('${key}_cached_at') as String?;
    return value != null ? DateTime.parse(value) : null;
  }

  bool isStale(String key, Duration ttl) {
    final cachedAt = getCachedAt(key);
    if (cachedAt == null) return true;
    return DateTime.now().difference(cachedAt) > ttl;
  }

  Future<void> clearAll() async {
    await _profileBox.clear();
    await _tripsBox.clear();
    await _settingsBox.clear();
    await _cacheMetaBox.clear();
  }
}
