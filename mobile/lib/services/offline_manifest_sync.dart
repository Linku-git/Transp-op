import 'dart:async';
import 'package:logger/logger.dart';
import '../config/cache_config.dart';
import 'api_client.dart';
import 'connectivity_service.dart';
import 'hive_storage_service.dart';

final _log = Logger();

class OfflineManifestSync {
  final ApiClient _apiClient;
  final HiveStorageService _hive;
  final ConnectivityService _connectivity;
  Timer? _periodicTimer;

  OfflineManifestSync({
    required ApiClient apiClient,
    required HiveStorageService hive,
    required ConnectivityService connectivity,
  })  : _apiClient = apiClient,
        _hive = hive,
        _connectivity = connectivity;

  Future<void> syncOnLaunch() async {
    if (!_connectivity.isOnline) return;
    await _sync();
  }

  void startPeriodicSync() {
    _periodicTimer?.cancel();
    _periodicTimer = Timer.periodic(
      CacheConfig.manifestSyncInterval,
      (_) => _syncIfOnWifi(),
    );
  }

  Future<void> _syncIfOnWifi() async {
    if (_connectivity.currentState == ConnectivityState.online) {
      await _sync();
    }
  }

  Future<void> _sync() async {
    try {
      final response = await _apiClient.dio.get('/mobile/offline-manifest');
      final manifest = response.data as Map<String, dynamic>;

      // Cache profile
      if (manifest['profile'] != null) {
        await _hive.saveProfile(
          Map<String, dynamic>.from(manifest['profile']),
        );
      }

      // Cache upcoming trips
      if (manifest['upcoming_trips'] != null) {
        final trips = (manifest['upcoming_trips'] as List)
            .map((e) => Map<String, dynamic>.from(e))
            .toList();
        await _hive.saveTrips('upcoming', trips);
      }

      // Cache site info
      if (manifest['site'] != null) {
        await _hive.saveSetting('site', manifest['site']);
      }

      // Cache point_arrets
      if (manifest['point_arrets'] != null) {
        await _hive.saveSetting('point_arrets', manifest['point_arrets']);
      }

      _log.d('Offline manifest synced at ${manifest['generated_at']}');
    } catch (e) {
      _log.w('Offline manifest sync failed: $e');
    }
  }

  void dispose() {
    _periodicTimer?.cancel();
  }
}
