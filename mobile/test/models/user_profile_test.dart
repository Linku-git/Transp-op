import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/user_profile.dart';

void main() {
  group('UserProfile', () {
    test('fromJson parses correctly', () {
      final profile = UserProfile.fromJson({
        'id': 'u-1',
        'email': 'jean@transpop.dev',
        'first_name': 'Jean',
        'last_name': 'Dupont',
        'matricule': 'MAT-001',
        'site_name': 'Ain Sebaa',
        'shift_label': 'Poste 1',
        'phone': '+212600000000',
        'current_transport_mode': 'voiture',
        'is_pmr': false,
        'stats': {
          'total_trips': 42,
          'co2_saved_kg': 15.3,
          'training_completed': 5,
        },
      });

      expect(profile.id, 'u-1');
      expect(profile.displayName, 'Jean Dupont');
      expect(profile.matricule, 'MAT-001');
      expect(profile.transportMode, 'voiture');
      expect(profile.stats.totalTrips, 42);
      expect(profile.stats.co2SavedKg, 15.3);
    });

    test('displayName falls back to email', () {
      final profile = UserProfile(id: '1', email: 'test@test.com');
      expect(profile.displayName, 'test@test.com');
    });

    test('initials from first and last name', () {
      final profile = UserProfile(
        id: '1', email: 'test@test.com',
        firstName: 'Jean', lastName: 'Dupont',
      );
      expect(profile.initials, 'JD');
    });

    test('initials from email when no name', () {
      final profile = UserProfile(id: '1', email: 'test@test.com');
      expect(profile.initials, 'T');
    });
  });

  group('ProfileStats', () {
    test('fromJson parses correctly', () {
      final stats = ProfileStats.fromJson({
        'total_trips': 10,
        'co2_saved_kg': 5.5,
        'training_completed': 3,
      });

      expect(stats.totalTrips, 10);
      expect(stats.co2SavedKg, 5.5);
      expect(stats.trainingCompleted, 3);
    });

    test('defaults to zero when fields missing', () {
      final stats = ProfileStats.fromJson({});
      expect(stats.totalTrips, 0);
      expect(stats.co2SavedKg, 0);
      expect(stats.trainingCompleted, 0);
    });
  });

  group('NotificationPreferences', () {
    test('toJson produces correct map', () {
      final prefs = NotificationPreferences();
      final json = prefs.toJson();

      expect(json['rti_alerts'], true);
      expect(json['route_changes'], true);
      expect(json['auto_night_mode'], true);
      expect(json['night_mode_start_hour'], 20);
    });
  });
}
