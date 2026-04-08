import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/vehicle_position.dart';
import 'package:transpop_mobile/widgets/tracking_mini_map.dart';

void main() {
  group('TrackingMiniMap', () {
    testWidgets('renders map placeholder', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: TrackingMiniMap()),
        ),
      );

      expect(find.text('Carte de suivi en direct'), findsOneWidget);
      expect(find.byIcon(Icons.map), findsOneWidget);
    });

    testWidgets('shows legend items', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: TrackingMiniMap()),
        ),
      );

      expect(find.text('Vous'), findsOneWidget);
      expect(find.text('Arrêt'), findsOneWidget);
      expect(find.text('Véhicule'), findsOneWidget);
    });

    testWidgets('shows LIVE badge when vehicle position exists', (tester) async {
      final pos = VehiclePosition(
        vehicleId: 'v1',
        lat: 33.58,
        lng: -7.63,
        timestamp: DateTime.now(),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: TrackingMiniMap(vehiclePosition: pos)),
        ),
      );

      expect(find.text('EN DIRECT'), findsOneWidget);
    });

    testWidgets('shows expand icon when onTap provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: TrackingMiniMap(onTap: () {}),
          ),
        ),
      );

      expect(find.byIcon(Icons.fullscreen), findsOneWidget);
    });

    testWidgets('calls onTap when tapped', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: TrackingMiniMap(onTap: () => tapped = true),
          ),
        ),
      );

      await tester.tap(find.byType(TrackingMiniMap));
      expect(tapped, true);
    });
  });
}
