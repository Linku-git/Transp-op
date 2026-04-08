import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/content/offline_indicator.dart';

void main() {
  group('OfflineIndicator', () {
    testWidgets('displays offline message', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: Scaffold(body: OfflineIndicator())),
      );

      expect(find.byIcon(Icons.cloud_off_outlined), findsOneWidget);
      expect(find.textContaining('hors-ligne'), findsOneWidget);
    });
  });
}
