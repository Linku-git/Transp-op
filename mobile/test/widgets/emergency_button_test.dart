import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/emergency_button.dart';

void main() {
  group('EmergencyButton', () {
    testWidgets('renders with URGENCE label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EmergencyButton(onPressed: () {}),
          ),
        ),
      );

      expect(find.text('URGENCE'), findsOneWidget);
      expect(find.byIcon(Icons.emergency), findsOneWidget);
    });

    testWidgets('calls onPressed when tapped', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EmergencyButton(onPressed: () => tapped = true),
          ),
        ),
      );

      await tester.tap(find.text('URGENCE'));
      expect(tapped, true);
    });
  });
}
