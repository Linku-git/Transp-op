import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/vehicle_position.dart';
import 'package:transpop_mobile/providers/tracking_provider.dart';

void main() {
  group('TrackingState', () {
    test('initial state', () {
      const state = TrackingState();
      expect(state.vehiclePosition, isNull);
      expect(state.vehicleId, isNull);
      expect(state.isConnected, false);
      expect(state.isLoading, false);
      expect(state.etaSeconds, isNull);
    });

    test('etaSeconds from vehiclePosition', () {
      final state = TrackingState(
        vehiclePosition: VehiclePosition(
          vehicleId: 'v1',
          lat: 33.58,
          lng: -7.63,
          timestamp: DateTime.now(),
          etaSeconds: 120,
        ),
      );
      expect(state.etaSeconds, 120);
    });

    test('copyWith preserves values', () {
      const state = TrackingState(
        vehicleType: 'MINIBUS',
        routeName: 'Route A1',
        isConnected: true,
      );
      final updated = state.copyWith(driverName: 'Mohammed');
      expect(updated.vehicleType, 'MINIBUS');
      expect(updated.routeName, 'Route A1');
      expect(updated.isConnected, true);
      expect(updated.driverName, 'Mohammed');
    });

    test('copyWith can set loading', () {
      const state = TrackingState();
      final updated = state.copyWith(isLoading: true);
      expect(updated.isLoading, true);
    });
  });
}
