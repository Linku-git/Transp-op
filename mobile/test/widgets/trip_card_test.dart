import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip.dart';
import 'package:transpop_mobile/widgets/trip_card.dart';

void main() {
  final trip = Trip(
    id: '1',
    date: DateTime(2026, 4, 8),
    shiftLabel: 'Poste 1',
    pickupPointName: 'Ain Sebaa',
    routeName: 'Route A1',
    vehicleType: 'MINIBUS',
    status: TripStatus.booked,
    departureTime: DateTime.now().add(const Duration(hours: 2)),
    co2SavedKg: 2.5,
  );

  group('TripCard', () {
    testWidgets('renders trip info', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: TripCard(trip: trip))),
      );

      expect(find.text('Poste 1'), findsOneWidget);
      expect(find.text('Ain Sebaa'), findsOneWidget);
      expect(find.text('Route A1'), findsOneWidget);
      expect(find.text('Réservé'), findsOneWidget);
    });

    testWidgets('shows CO2 badge when available', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: TripCard(trip: trip))),
      );

      expect(find.textContaining('2.5 kg CO2'), findsOneWidget);
    });

    testWidgets('shows modify/cancel for modifiable trip', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: TripCard(
              trip: trip,
              onModify: () {},
              onCancel: () {},
            ),
          ),
        ),
      );

      expect(find.text('Modifier'), findsOneWidget);
      expect(find.text('Annuler'), findsOneWidget);
    });

    testWidgets('hides actions for completed trip', (tester) async {
      final completed = Trip(
        id: '1', date: DateTime(2026, 4, 8), shiftLabel: 'P1',
        pickupPointName: 'Test', routeName: 'R1', vehicleType: 'BUS',
        status: TripStatus.completed,
        departureTime: DateTime.now().subtract(const Duration(hours: 1)),
      );
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: TripCard(trip: completed))),
      );

      expect(find.text('Modifier'), findsNothing);
      expect(find.text('Annuler'), findsNothing);
    });
  });
}
