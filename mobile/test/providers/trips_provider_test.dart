import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip.dart';
import 'package:transpop_mobile/providers/trips_provider.dart';

void main() {
  group('TripsState', () {
    test('initial state', () {
      const state = TripsState();
      expect(state.upcoming, isEmpty);
      expect(state.past, isEmpty);
      expect(state.isLoading, false);
    });

    test('pastStats computes from past trips', () {
      final state = TripsState(
        past: [
          Trip(
            id: '1', date: DateTime(2026, 4, 8), shiftLabel: '', pickupPointName: '',
            routeName: '', vehicleType: '', status: TripStatus.completed,
            departureTime: DateTime(2026, 4, 8), co2SavedKg: 2.0, distanceKm: 10.0,
          ),
        ],
      );
      expect(state.pastStats.totalTrips, 1);
      expect(state.pastStats.totalCo2SavedKg, 2.0);
    });

    test('pastByMonth groups correctly', () {
      final state = TripsState(
        past: [
          Trip(
            id: '1', date: DateTime(2026, 4, 8), shiftLabel: '', pickupPointName: '',
            routeName: '', vehicleType: '', status: TripStatus.completed,
            departureTime: DateTime(2026, 4, 8),
          ),
          Trip(
            id: '2', date: DateTime(2026, 3, 15), shiftLabel: '', pickupPointName: '',
            routeName: '', vehicleType: '', status: TripStatus.completed,
            departureTime: DateTime(2026, 3, 15),
          ),
        ],
      );
      final grouped = state.pastByMonth;
      expect(grouped.keys, contains('2026-04'));
      expect(grouped.keys, contains('2026-03'));
      expect(grouped['2026-04']!.length, 1);
    });

    test('copyWith preserves values', () {
      const state = TripsState(isLoading: true);
      final updated = state.copyWith(error: 'Test');
      expect(updated.isLoading, true);
      expect(updated.error, 'Test');
    });
  });
}
