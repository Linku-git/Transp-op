import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/user_profile.dart';
import 'package:transpop_mobile/widgets/quick_stats_row.dart';

void main() {
  group('QuickStatsRow', () {
    testWidgets('renders all 3 stats', (tester) async {
      const stats = ProfileStats(
        totalTrips: 42,
        co2SavedKg: 15.3,
        trainingCompleted: 5,
      );

      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: QuickStatsRow(stats: stats))),
      );

      expect(find.text('42'), findsOneWidget);
      expect(find.text('15.3 kg'), findsOneWidget);
      expect(find.text('5'), findsOneWidget);
      expect(find.text('Trajets'), findsOneWidget);
      expect(find.text('CO2 éco.'), findsOneWidget);
      expect(find.text('Formations'), findsOneWidget);
    });

    testWidgets('renders icons', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickStatsRow(stats: const ProfileStats()),
          ),
        ),
      );

      expect(find.byIcon(Icons.directions_bus), findsOneWidget);
      expect(find.byIcon(Icons.eco), findsOneWidget);
      expect(find.byIcon(Icons.school), findsOneWidget);
    });
  });
}
