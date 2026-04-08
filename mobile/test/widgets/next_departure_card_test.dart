import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/departure.dart';
import 'package:transpop_mobile/widgets/next_departure_card.dart';

void main() {
  Departure createDeparture({Duration? offset}) {
    return Departure(
      id: 'test-1',
      departureTime: DateTime.now().add(offset ?? const Duration(minutes: 30)),
      pickupPointName: 'Ain Sebaa',
      walkingMinutes: 5,
      vehicleType: 'MINIBUS',
      routeName: 'Route A1',
      driverName: 'Mohammed',
    );
  }

  group('NextDepartureCard', () {
    testWidgets('displays all departure info', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NextDepartureCard(departure: createDeparture()),
          ),
        ),
      );

      expect(find.text('PROCHAIN DÉPART'), findsOneWidget);
      expect(find.text('Ain Sebaa'), findsOneWidget);
      expect(find.text('Route A1'), findsOneWidget);
      expect(find.text('MINIBUS'), findsOneWidget);
      expect(find.text('Mohammed'), findsOneWidget);
      expect(find.text('5 min à pied'), findsOneWidget);
    });

    testWidgets('shows View on Map button', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NextDepartureCard(
              departure: createDeparture(),
              onViewMap: () => tapped = true,
            ),
          ),
        ),
      );

      expect(find.text('Voir sur la carte'), findsOneWidget);
      await tester.tap(find.text('Voir sur la carte'));
      expect(tapped, true);
    });

    testWidgets('hides map button when onViewMap is null', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NextDepartureCard(departure: createDeparture()),
          ),
        ),
      );

      expect(find.text('Voir sur la carte'), findsNothing);
    });
  });
}
