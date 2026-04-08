import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/security_preferences.dart';

void main() {
  group('SecurityPreferences', () {
    test('defaults are correct', () {
      final prefs = SecurityPreferences();
      expect(prefs.safetyRating, 3);
      expect(prefs.vulnerableTimeSlots, isEmpty);
      expect(prefs.concernZones, isEmpty);
      expect(prefs.nightConcerns, isNull);
      expect(prefs.maxNightWalkingDistanceMeters, 300);
    });

    test('toJson produces correct map', () {
      final prefs = SecurityPreferences(
        safetyRating: 2,
        vulnerableTimeSlots: ['22h-05h', '05h-07h'],
        nightConcerns: 'Zones mal éclairées',
        maxNightWalkingDistanceMeters: 200,
      );
      final json = prefs.toJson();

      expect(json['safety_rating'], 2);
      expect(json['vulnerable_time_slots'], ['22h-05h', '05h-07h']);
      expect(json['night_concerns'], 'Zones mal éclairées');
      expect(json['max_night_walking_distance_meters'], 200);
    });

    test('toJson serializes concern zones', () {
      final prefs = SecurityPreferences(
        concernZones: [
          const ConcernZone(lat: 33.58, lng: -7.63, description: 'Zone sombre'),
        ],
      );
      final json = prefs.toJson();
      final zones = json['concern_zones'] as List;

      expect(zones.length, 1);
      expect(zones[0]['lat'], 33.58);
      expect(zones[0]['description'], 'Zone sombre');
    });
  });

  group('ConcernZone', () {
    test('toJson omits null description', () {
      const zone = ConcernZone(lat: 33.0, lng: -7.0);
      final json = zone.toJson();

      expect(json.containsKey('description'), false);
      expect(json['lat'], 33.0);
    });
  });

  group('TimeSlot', () {
    test('has 6 predefined slots', () {
      expect(TimeSlot.all.length, 6);
    });

    test('includes night slot', () {
      expect(
        TimeSlot.all.any((s) => s.key == '22h-05h'),
        true,
      );
    });
  });
}
