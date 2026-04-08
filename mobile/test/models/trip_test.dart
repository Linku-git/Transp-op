import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip.dart';

void main() {
  group('Trip', () {
    test('fromJson parses correctly', () {
      final trip = Trip.fromJson({
        'id': 'trip-1',
        'date': '2026-04-08',
        'shift_label': 'Poste 1',
        'pickup_point_name': 'Ain Sebaa',
        'route_name': 'Route A1',
        'vehicle_type': 'MINIBUS',
        'status': 'booked',
        'departure_time': '2026-04-08T06:30:00',
        'co2_saved_kg': 2.5,
        'distance_km': 15.3,
      });

      expect(trip.id, 'trip-1');
      expect(trip.shiftLabel, 'Poste 1');
      expect(trip.status, TripStatus.booked);
      expect(trip.co2SavedKg, 2.5);
      expect(trip.distanceKm, 15.3);
    });

    test('canModify is true when >30min before departure', () {
      final trip = Trip(
        id: '1',
        date: DateTime.now(),
        shiftLabel: 'P1',
        pickupPointName: 'Test',
        routeName: 'R1',
        vehicleType: 'BUS',
        status: TripStatus.booked,
        departureTime: DateTime.now().add(const Duration(hours: 2)),
      );
      expect(trip.canModify, true);
      expect(trip.canCancel, true);
    });

    test('canModify is false when <30min before departure', () {
      final trip = Trip(
        id: '1',
        date: DateTime.now(),
        shiftLabel: 'P1',
        pickupPointName: 'Test',
        routeName: 'R1',
        vehicleType: 'BUS',
        status: TripStatus.booked,
        departureTime: DateTime.now().add(const Duration(minutes: 15)),
      );
      expect(trip.canModify, false);
    });

    test('canModify is false for completed trips', () {
      final trip = Trip(
        id: '1',
        date: DateTime.now(),
        shiftLabel: 'P1',
        pickupPointName: 'Test',
        routeName: 'R1',
        vehicleType: 'BUS',
        status: TripStatus.completed,
        departureTime: DateTime.now().add(const Duration(hours: 2)),
      );
      expect(trip.canModify, false);
    });

    test('isUpcoming for booked/confirmed/inProgress', () {
      for (final s in [TripStatus.booked, TripStatus.confirmed, TripStatus.inProgress]) {
        final trip = Trip(
          id: '1', date: DateTime.now(), shiftLabel: '', pickupPointName: '',
          routeName: '', vehicleType: '', status: s,
          departureTime: DateTime.now(),
        );
        expect(trip.isUpcoming, true);
      }
    });

    test('isUpcoming false for completed/cancelled', () {
      for (final s in [TripStatus.completed, TripStatus.cancelled]) {
        final trip = Trip(
          id: '1', date: DateTime.now(), shiftLabel: '', pickupPointName: '',
          routeName: '', vehicleType: '', status: s,
          departureTime: DateTime.now(),
        );
        expect(trip.isUpcoming, false);
      }
    });
  });

  group('TripStatus', () {
    test('fromString parses all statuses', () {
      expect(TripStatus.fromString('booked'), TripStatus.booked);
      expect(TripStatus.fromString('confirmed'), TripStatus.confirmed);
      expect(TripStatus.fromString('in_progress'), TripStatus.inProgress);
      expect(TripStatus.fromString('completed'), TripStatus.completed);
      expect(TripStatus.fromString('cancelled'), TripStatus.cancelled);
    });

    test('fromString defaults to booked', () {
      expect(TripStatus.fromString('unknown'), TripStatus.booked);
    });

    test('labels are in French', () {
      expect(TripStatus.booked.label, 'Réservé');
      expect(TripStatus.completed.label, 'Terminé');
      expect(TripStatus.cancelled.label, 'Annulé');
    });
  });

  group('TripStats', () {
    test('fromTrips computes aggregates', () {
      final trips = [
        Trip(
          id: '1', date: DateTime.now(), shiftLabel: '', pickupPointName: '',
          routeName: '', vehicleType: '', status: TripStatus.completed,
          departureTime: DateTime.now(), co2SavedKg: 2.0, distanceKm: 10.0,
        ),
        Trip(
          id: '2', date: DateTime.now(), shiftLabel: '', pickupPointName: '',
          routeName: '', vehicleType: '', status: TripStatus.completed,
          departureTime: DateTime.now(), co2SavedKg: 3.5, distanceKm: 20.0,
        ),
      ];
      final stats = TripStats.fromTrips(trips);
      expect(stats.totalTrips, 2);
      expect(stats.totalCo2SavedKg, 5.5);
      expect(stats.totalDistanceKm, 30.0);
    });
  });
}
