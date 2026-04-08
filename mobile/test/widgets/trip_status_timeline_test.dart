import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip.dart';
import 'package:transpop_mobile/widgets/trip_status_timeline.dart';

void main() {
  group('TripStatusTimeline', () {
    testWidgets('renders all 4 status labels', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: TripStatusTimeline(currentStatus: TripStatus.booked),
          ),
        ),
      );

      expect(find.text('Réservé'), findsOneWidget);
      expect(find.text('Confirmé'), findsOneWidget);
      expect(find.text('En cours'), findsOneWidget);
      expect(find.text('Terminé'), findsOneWidget);
    });

    testWidgets('renders check icon for completed steps', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: TripStatusTimeline(currentStatus: TripStatus.completed),
          ),
        ),
      );

      // All 4 steps should have check icons when completed
      expect(find.byIcon(Icons.check), findsNWidgets(4));
    });
  });
}
