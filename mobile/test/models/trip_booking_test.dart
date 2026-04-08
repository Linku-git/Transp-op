import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip_booking.dart';

void main() {
  group('TripBooking', () {
    test('toJson formats date correctly', () {
      final booking = TripBooking(
        date: DateTime(2026, 4, 8),
        shiftId: 'shift-1',
        shiftLabel: 'Poste 1',
        pickupPointId: 'pp-1',
        pickupPointName: 'Ain Sebaa',
      );
      final json = booking.toJson();

      expect(json['date'], '2026-04-08');
      expect(json['shift_id'], 'shift-1');
      expect(json['pickup_point_id'], 'pp-1');
      expect(json.containsKey('pickup_lat'), false);
    });

    test('toJson includes optional pickup coords', () {
      final booking = TripBooking(
        date: DateTime(2026, 4, 8),
        shiftId: 's1',
        shiftLabel: 'P1',
        pickupPointId: 'pp-1',
        pickupPointName: 'Test',
        pickupLat: 33.58,
        pickupLng: -7.63,
      );
      final json = booking.toJson();

      expect(json['pickup_lat'], 33.58);
      expect(json['pickup_lng'], -7.63);
    });

    test('toJson pads single-digit months and days', () {
      final booking = TripBooking(
        date: DateTime(2026, 1, 5),
        shiftId: 's1',
        shiftLabel: 'P1',
        pickupPointId: 'pp-1',
        pickupPointName: 'Test',
      );
      expect(booking.toJson()['date'], '2026-01-05');
    });
  });

  group('Shift', () {
    test('fromJson parses correctly', () {
      final shift = Shift.fromJson({
        'id': 's-1',
        'label': 'Poste 1',
        'entry_time': '06:00',
        'exit_time': '14:00',
      });
      expect(shift.id, 's-1');
      expect(shift.label, 'Poste 1');
      expect(shift.entryTime, '06:00');
      expect(shift.exitTime, '14:00');
    });

    test('fromJson handles missing label', () {
      final shift = Shift.fromJson({
        'id': 's-1',
        'shift_type': 'Normal',
      });
      expect(shift.label, 'Normal');
    });
  });

  group('PickupPoint', () {
    test('fromJson parses correctly', () {
      final point = PickupPoint.fromJson({
        'id': 'pp-1',
        'name': 'Ain Sebaa',
        'lat': 33.58,
        'lng': -7.63,
        'walking_minutes': 5.0,
      });
      expect(point.id, 'pp-1');
      expect(point.name, 'Ain Sebaa');
      expect(point.lat, 33.58);
      expect(point.walkingMinutes, 5.0);
    });
  });

  group('BookingConfirmation', () {
    test('fromJson parses correctly', () {
      final conf = BookingConfirmation.fromJson({
        'trip_id': 'trip-123',
        'message': 'Réservation confirmée',
      });
      expect(conf.tripId, 'trip-123');
      expect(conf.message, 'Réservation confirmée');
    });

    test('fromJson uses defaults', () {
      final conf = BookingConfirmation.fromJson({});
      expect(conf.tripId, '');
      expect(conf.message, 'Réservation confirmée');
    });
  });
}
