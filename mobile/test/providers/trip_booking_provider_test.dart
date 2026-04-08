import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip_booking.dart';
import 'package:transpop_mobile/providers/trip_booking_provider.dart';

void main() {
  group('TripBookingState', () {
    test('initial state defaults', () {
      final state = TripBookingState();
      expect(state.shifts, isEmpty);
      expect(state.selectedShiftId, isNull);
      expect(state.selectedShift, isNull);
      expect(state.activePickupPoint, isNull);
      expect(state.canConfirm, false);
      expect(state.isSubmitting, false);
      expect(state.confirmation, isNull);
    });

    test('canConfirm is true when shift and pickup selected', () {
      final state = TripBookingState(
        shifts: [const Shift(id: 's1', label: 'P1', entryTime: '06:00', exitTime: '14:00')],
        selectedShiftId: 's1',
        defaultPickupPoint: const PickupPoint(id: 'pp1', name: 'Test', lat: 33.0, lng: -7.0),
      );
      expect(state.canConfirm, true);
    });

    test('canConfirm is false when submitting', () {
      final state = TripBookingState(
        shifts: [const Shift(id: 's1', label: 'P1', entryTime: '06:00', exitTime: '14:00')],
        selectedShiftId: 's1',
        defaultPickupPoint: const PickupPoint(id: 'pp1', name: 'Test', lat: 33.0, lng: -7.0),
        isSubmitting: true,
      );
      expect(state.canConfirm, false);
    });

    test('selectedShift returns matching shift', () {
      final state = TripBookingState(
        shifts: [
          const Shift(id: 's1', label: 'P1', entryTime: '06:00', exitTime: '14:00'),
          const Shift(id: 's2', label: 'P2', entryTime: '14:00', exitTime: '22:00'),
        ],
        selectedShiftId: 's2',
      );
      expect(state.selectedShift?.label, 'P2');
    });

    test('activePickupPoint prefers selectedPickupPoint', () {
      final state = TripBookingState(
        defaultPickupPoint: const PickupPoint(id: 'pp1', name: 'Default', lat: 33.0, lng: -7.0),
        selectedPickupPoint: const PickupPoint(id: 'pp2', name: 'Custom', lat: 33.5, lng: -7.5),
      );
      expect(state.activePickupPoint?.name, 'Custom');
    });

    test('activePickupPoint falls back to default', () {
      final state = TripBookingState(
        defaultPickupPoint: const PickupPoint(id: 'pp1', name: 'Default', lat: 33.0, lng: -7.0),
      );
      expect(state.activePickupPoint?.name, 'Default');
    });

    test('copyWith preserves values', () {
      final state = TripBookingState(selectedShiftId: 's1');
      final updated = state.copyWith(isSubmitting: true);
      expect(updated.selectedShiftId, 's1');
      expect(updated.isSubmitting, true);
    });
  });
}
