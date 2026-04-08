import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/quick_actions_row.dart';

void main() {
  group('QuickActionsRow', () {
    testWidgets('renders 3 action buttons', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickActionsRow(
              onBookTrip: () {},
              onViewMap: () {},
              onMyTrips: () {},
            ),
          ),
        ),
      );

      expect(find.text('Réserver'), findsOneWidget);
      expect(find.text('Carte'), findsOneWidget);
      expect(find.text('Mes trajets'), findsOneWidget);
    });

    testWidgets('tapping Book Trip calls callback', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickActionsRow(
              onBookTrip: () => tapped = true,
              onViewMap: () {},
              onMyTrips: () {},
            ),
          ),
        ),
      );

      await tester.tap(find.text('Réserver'));
      expect(tapped, true);
    });
  });
}
