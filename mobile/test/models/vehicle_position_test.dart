import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/vehicle_position.dart';

void main() {
  group('VehiclePosition', () {
    test('fromJson parses correctly', () {
      final pos = VehiclePosition.fromJson({
        'vehicle_id': 'v-1',
        'lat': 33.58,
        'lng': -7.63,
        'heading': 45.0,
        'speed': 30.5,
        'timestamp': '2026-04-08T08:30:00',
        'eta_seconds': 120,
      });

      expect(pos.vehicleId, 'v-1');
      expect(pos.lat, 33.58);
      expect(pos.lng, -7.63);
      expect(pos.heading, 45.0);
      expect(pos.speed, 30.5);
      expect(pos.etaSeconds, 120);
    });

    test('fromJson handles missing optionals', () {
      final pos = VehiclePosition.fromJson({
        'vehicle_id': 'v-1',
        'lat': 33.58,
        'lng': -7.63,
      });

      expect(pos.heading, isNull);
      expect(pos.speed, isNull);
      expect(pos.etaSeconds, isNull);
    });
  });

  group('TrackingInfo', () {
    test('fromJson parses correctly', () {
      final info = TrackingInfo.fromJson({
        'vehicle_id': 'v-1',
        'vehicle_type': 'MINIBUS',
        'route_name': 'Route A1',
        'driver_name': 'Mohammed',
        'gathering_point_name': 'Ain Sebaa',
        'gathering_point_lat': 33.58,
        'gathering_point_lng': -7.63,
        'employee_lat': 33.57,
        'employee_lng': -7.64,
      });

      expect(info.vehicleId, 'v-1');
      expect(info.vehicleType, 'MINIBUS');
      expect(info.driverName, 'Mohammed');
      expect(info.gatheringPointLat, 33.58);
      expect(info.employeeLat, 33.57);
    });
  });
}
