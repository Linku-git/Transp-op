import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/departure.dart';

void main() {
  group('Departure', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'trip-123',
        'departure_time': '2026-04-08T08:30:00',
        'pickup_point_name': 'Ain Sebaa',
        'walking_minutes': 5.0,
        'vehicle_type': 'MINIBUS',
        'route_name': 'Route A1',
        'driver_name': 'Mohammed',
      };

      final dep = Departure.fromJson(json);
      expect(dep.id, 'trip-123');
      expect(dep.pickupPointName, 'Ain Sebaa');
      expect(dep.walkingMinutes, 5.0);
      expect(dep.vehicleType, 'MINIBUS');
      expect(dep.routeName, 'Route A1');
      expect(dep.driverName, 'Mohammed');
    });

    test('hasDeparted returns true for past departure', () {
      final dep = Departure(
        id: '1',
        departureTime: DateTime.now().subtract(const Duration(minutes: 5)),
        pickupPointName: 'Test',
        vehicleType: 'BUS',
        routeName: 'R1',
      );
      expect(dep.hasDeparted, true);
    });

    test('hasDeparted returns false for future departure', () {
      final dep = Departure(
        id: '1',
        departureTime: DateTime.now().add(const Duration(hours: 1)),
        pickupPointName: 'Test',
        vehicleType: 'BUS',
        routeName: 'R1',
      );
      expect(dep.hasDeparted, false);
    });

    test('minutesRemaining is positive for future departure', () {
      final dep = Departure(
        id: '1',
        departureTime: DateTime.now().add(const Duration(minutes: 30)),
        pickupPointName: 'Test',
        vehicleType: 'BUS',
        routeName: 'R1',
      );
      expect(dep.minutesRemaining, greaterThan(25));
    });
  });

  group('ContentItem', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'content-1',
        'title': 'Nouvelle route',
        'snippet': 'Description courte',
        'type': 'news',
        'published_at': '2026-04-08T10:00:00',
        'is_read': false,
      };

      final item = ContentItem.fromJson(json);
      expect(item.id, 'content-1');
      expect(item.title, 'Nouvelle route');
      expect(item.type, 'news');
      expect(item.isRead, false);
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'id': '1',
        'title': 'Test',
        'published_at': '2026-04-08T10:00:00',
      };

      final item = ContentItem.fromJson(json);
      expect(item.snippet, '');
      expect(item.type, 'news');
      expect(item.imageUrl, isNull);
      expect(item.isRead, false);
    });
  });
}
