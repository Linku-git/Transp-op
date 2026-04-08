import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/transport_preferences.dart';

void main() {
  group('TransportPreferences', () {
    test('defaults are correct', () {
      final prefs = TransportPreferences();
      expect(prefs.currentMode, isNull);
      expect(prefs.interestedInCompanyTransport, true);
      expect(prefs.hasPrivateCar, false);
      expect(prefs.volunteerDriver, false);
      expect(prefs.carpoolSeats, 0);
      expect(prefs.maxWalkingDistanceMeters, 500);
    });

    test('toJson produces correct map', () {
      final prefs = TransportPreferences(
        currentMode: 'voiture',
        hasPrivateCar: true,
        volunteerDriver: true,
        carpoolSeats: 3,
        maxWalkingDistanceMeters: 800,
      );
      final json = prefs.toJson();

      expect(json['current_transport_mode'], 'voiture');
      expect(json['has_private_car'], true);
      expect(json['volunteer_driver'], true);
      expect(json['carpool_seats'], 3);
      expect(json['max_walking_distance_meters'], 800);
    });

    test('toJson omits null pickup fields', () {
      final prefs = TransportPreferences();
      final json = prefs.toJson();

      expect(json.containsKey('pickup_lat'), false);
      expect(json.containsKey('pickup_lng'), false);
      expect(json.containsKey('pickup_name'), false);
    });

    test('toJson includes pickup when set', () {
      final prefs = TransportPreferences(
        pickupLat: 33.58,
        pickupLng: -7.63,
        pickupName: 'Ain Sebaa',
      );
      final json = prefs.toJson();

      expect(json['pickup_lat'], 33.58);
      expect(json['pickup_lng'], -7.63);
      expect(json['pickup_name'], 'Ain Sebaa');
    });
  });

  group('TransportMode', () {
    test('has 8 predefined modes', () {
      expect(TransportMode.all.length, 8);
    });

    test('voiture mode exists', () {
      expect(
        TransportMode.all.any((m) => m.key == 'voiture'),
        true,
      );
    });
  });
}
