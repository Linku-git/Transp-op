import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/vehicle_position.dart';
import '../services/vehicle_tracking_service.dart';
import '../services/websocket_service.dart';
import 'auth_provider.dart';

final vehicleTrackingServiceProvider = Provider<VehicleTrackingService>((ref) {
  return VehicleTrackingService(apiClient: ref.watch(apiClientProvider));
});

final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService();
  ref.onDispose(() => service.dispose());
  return service;
});

class TrackingState {
  final VehiclePosition? vehiclePosition;
  final String? vehicleId;
  final String vehicleType;
  final String routeName;
  final String? driverName;
  final String gatheringPointName;
  final double? gatheringPointLat;
  final double? gatheringPointLng;
  final double? employeeLat;
  final double? employeeLng;
  final bool isConnected;
  final bool isLoading;
  final String? error;

  const TrackingState({
    this.vehiclePosition,
    this.vehicleId,
    this.vehicleType = '',
    this.routeName = '',
    this.driverName,
    this.gatheringPointName = '',
    this.gatheringPointLat,
    this.gatheringPointLng,
    this.employeeLat,
    this.employeeLng,
    this.isConnected = false,
    this.isLoading = false,
    this.error,
  });

  int? get etaSeconds => vehiclePosition?.etaSeconds;

  TrackingState copyWith({
    VehiclePosition? vehiclePosition,
    String? vehicleId,
    String? vehicleType,
    String? routeName,
    String? driverName,
    String? gatheringPointName,
    double? gatheringPointLat,
    double? gatheringPointLng,
    double? employeeLat,
    double? employeeLng,
    bool? isConnected,
    bool? isLoading,
    String? error,
  }) {
    return TrackingState(
      vehiclePosition: vehiclePosition ?? this.vehiclePosition,
      vehicleId: vehicleId ?? this.vehicleId,
      vehicleType: vehicleType ?? this.vehicleType,
      routeName: routeName ?? this.routeName,
      driverName: driverName ?? this.driverName,
      gatheringPointName: gatheringPointName ?? this.gatheringPointName,
      gatheringPointLat: gatheringPointLat ?? this.gatheringPointLat,
      gatheringPointLng: gatheringPointLng ?? this.gatheringPointLng,
      employeeLat: employeeLat ?? this.employeeLat,
      employeeLng: employeeLng ?? this.employeeLng,
      isConnected: isConnected ?? this.isConnected,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class TrackingNotifier extends StateNotifier<TrackingState> {
  final VehicleTrackingService _trackingService;
  final WebSocketService _wsService;
  StreamSubscription<VehiclePosition>? _positionSub;
  Timer? _pollTimer;

  TrackingNotifier(this._trackingService, this._wsService)
      : super(const TrackingState());

  Future<void> startTracking(String vehicleId) async {
    state = state.copyWith(isLoading: true, vehicleId: vehicleId, error: null);

    // Load initial info
    final info = await _trackingService.getTrackingInfo();
    if (info != null) {
      state = state.copyWith(
        vehicleType: info['vehicle_type'] as String? ?? '',
        routeName: info['route_name'] as String? ?? '',
        driverName: info['driver_name'] as String?,
        gatheringPointName: info['gathering_point_name'] as String? ?? '',
        gatheringPointLat: (info['gathering_point_lat'] as num?)?.toDouble(),
        gatheringPointLng: (info['gathering_point_lng'] as num?)?.toDouble(),
        employeeLat: (info['employee_lat'] as num?)?.toDouble(),
        employeeLng: (info['employee_lng'] as num?)?.toDouble(),
      );
    }

    // Get initial position
    final position = await _trackingService.getLatestPosition(vehicleId);
    if (position != null) {
      state = state.copyWith(vehiclePosition: position, isLoading: false);
    } else {
      state = state.copyWith(isLoading: false);
    }

    // Connect WebSocket
    try {
      await _wsService.connect(vehicleId);
      _positionSub = _wsService.positionStream.listen((pos) {
        state = state.copyWith(vehiclePosition: pos, isConnected: true);
      });
      state = state.copyWith(isConnected: true);
    } catch (_) {
      // Fallback to polling if WebSocket fails
      _startPolling(vehicleId);
    }
  }

  void _startPolling(String vehicleId) {
    _pollTimer = Timer.periodic(const Duration(seconds: 10), (_) async {
      final pos = await _trackingService.getLatestPosition(vehicleId);
      if (pos != null && mounted) {
        state = state.copyWith(vehiclePosition: pos);
      }
    });
  }

  void stopTracking() {
    _positionSub?.cancel();
    _pollTimer?.cancel();
    _wsService.disconnect();
    state = const TrackingState();
  }

  @override
  void dispose() {
    _positionSub?.cancel();
    _pollTimer?.cancel();
    super.dispose();
  }
}

final trackingProvider =
    StateNotifierProvider<TrackingNotifier, TrackingState>((ref) {
  return TrackingNotifier(
    ref.watch(vehicleTrackingServiceProvider),
    ref.watch(webSocketServiceProvider),
  );
});
