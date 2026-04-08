import 'dart:async';
import 'dart:convert';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:logger/logger.dart';
import '../config/cache_config.dart';
import 'api_client.dart';
import 'connectivity_service.dart';

final _log = Logger();

enum QueuePriority { critical, high, medium, low }

class QueuedAction {
  final String id;
  final String method;
  final String path;
  final Map<String, dynamic>? data;
  final QueuePriority priority;
  final DateTime createdAt;
  int retries;

  QueuedAction({
    required this.id,
    required this.method,
    required this.path,
    this.data,
    this.priority = QueuePriority.medium,
    DateTime? createdAt,
    this.retries = 0,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toJson() => {
        'id': id,
        'method': method,
        'path': path,
        'data': data,
        'priority': priority.index,
        'created_at': createdAt.toIso8601String(),
        'retries': retries,
      };

  factory QueuedAction.fromJson(Map<String, dynamic> json) => QueuedAction(
        id: json['id'] as String,
        method: json['method'] as String,
        path: json['path'] as String,
        data: json['data'] as Map<String, dynamic>?,
        priority: QueuePriority.values[json['priority'] as int? ?? 2],
        createdAt: DateTime.parse(json['created_at'] as String),
        retries: json['retries'] as int? ?? 0,
      );
}

class OfflineQueue {
  final ApiClient _apiClient;
  final ConnectivityService _connectivity;
  late Box<String> _box;
  bool _isSyncing = false;
  StreamSubscription<ConnectivityState>? _connectivitySub;

  OfflineQueue({
    required ApiClient apiClient,
    required ConnectivityService connectivity,
  })  : _apiClient = apiClient,
        _connectivity = connectivity;

  bool get isSyncing => _isSyncing;
  int get pendingCount => _box.length;

  Future<void> initialize() async {
    _box = await Hive.openBox<String>(CacheConfig.offlineQueueBox);

    // Auto-sync on reconnect
    _connectivitySub = _connectivity.stateStream.listen((state) {
      if (state == ConnectivityState.online && !_isSyncing) {
        syncQueue();
      }
    });
  }

  Future<void> enqueue(QueuedAction action) async {
    await _box.put(action.id, jsonEncode(action.toJson()));
    _log.d('Queued ${action.method} ${action.path} (${action.priority.name})');

    // Try immediate sync if online
    if (_connectivity.isOnline && !_isSyncing) {
      unawaited(syncQueue());
    }
  }

  Future<void> syncQueue() async {
    if (_isSyncing || _box.isEmpty) return;
    _isSyncing = true;

    try {
      // Sort by priority (critical first)
      final entries = _box.keys.toList();
      final actions = entries
          .map((key) {
            final json = _box.get(key);
            if (json == null) return null;
            return QueuedAction.fromJson(jsonDecode(json));
          })
          .whereType<QueuedAction>()
          .toList()
        ..sort((a, b) => a.priority.index.compareTo(b.priority.index));

      for (final action in actions) {
        try {
          await _executeAction(action);
          await _box.delete(action.id);
          _log.d('Synced ${action.method} ${action.path}');
        } catch (e) {
          action.retries++;
          if (action.retries >= CacheConfig.maxQueueRetries) {
            await _box.delete(action.id);
            _log.w('Dropped ${action.path} after ${action.retries} retries');
          } else {
            await _box.put(action.id, jsonEncode(action.toJson()));
            _log.w('Retry ${action.retries} for ${action.path}');
          }
        }
      }
    } finally {
      _isSyncing = false;
    }
  }

  Future<void> _executeAction(QueuedAction action) async {
    switch (action.method.toUpperCase()) {
      case 'POST':
        await _apiClient.dio.post(action.path, data: action.data);
      case 'PUT':
        await _apiClient.dio.put(action.path, data: action.data);
      case 'DELETE':
        await _apiClient.dio.delete(action.path);
      case 'PATCH':
        await _apiClient.dio.patch(action.path, data: action.data);
    }
  }

  Future<void> clear() async {
    await _box.clear();
  }

  void dispose() {
    _connectivitySub?.cancel();
  }
}
