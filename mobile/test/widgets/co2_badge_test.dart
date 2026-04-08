import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/co2_badge.dart';

void main() {
  group('Co2Badge', () {
    testWidgets('renders CO2 value', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: Co2Badge(co2SavedKg: 3.7)),
        ),
      );

      expect(find.text('3.7 kg CO2'), findsOneWidget);
      expect(find.text('économisés'), findsOneWidget);
      expect(find.byIcon(Icons.eco), findsOneWidget);
    });
  });
}
