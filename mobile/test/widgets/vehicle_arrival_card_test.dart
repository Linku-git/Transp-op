import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/vehicle_arrival_card.dart';

void main() {
  group('VehicleArrivalCard', () {
    testWidgets('renders vehicle info', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VehicleArrivalCard(
              etaSeconds: 300,
              vehicleType: 'MINIBUS',
              routeName: 'Route A1',
              driverName: 'Mohammed',
              gatheringPointName: 'Ain Sebaa',
            ),
          ),
        ),
      );

      expect(find.text('MINIBUS'), findsOneWidget);
      expect(find.text('Route A1'), findsOneWidget);
      expect(find.text('Mohammed'), findsOneWidget);
      expect(find.text('Ain Sebaa'), findsOneWidget);
    });

    testWidgets('shows ETA countdown', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VehicleArrivalCard(
              etaSeconds: 125,
              vehicleType: 'BUS',
              routeName: 'R1',
              gatheringPointName: 'Test',
            ),
          ),
        ),
      );

      expect(find.textContaining('min'), findsOneWidget);
    });

    testWidgets('shows full map button when callback provided', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VehicleArrivalCard(
              etaSeconds: 120,
              vehicleType: 'BUS',
              routeName: 'R1',
              gatheringPointName: 'Test',
              onViewFullMap: () => tapped = true,
            ),
          ),
        ),
      );

      expect(find.text('Carte complète'), findsOneWidget);
      await tester.tap(find.text('Carte complète'));
      expect(tapped, true);
    });

    testWidgets('hides map button when no callback', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: VehicleArrivalCard(
              etaSeconds: 120,
              vehicleType: 'BUS',
              routeName: 'R1',
              gatheringPointName: 'Test',
            ),
          ),
        ),
      );

      expect(find.text('Carte complète'), findsNothing);
    });
  });
}
