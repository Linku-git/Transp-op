import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/content/content_tabs.dart';

void main() {
  Widget wrap(Widget child) {
    return MaterialApp(home: Scaffold(body: child));
  }

  group('ContentTabs', () {
    testWidgets('renders all tab labels', (tester) async {
      await tester.pumpWidget(wrap(
        ContentTabs(selectedType: 'all', onTypeChanged: (_) {}),
      ));

      expect(find.text('Tout'), findsOneWidget);
      expect(find.text('Actualités'), findsOneWidget);
      expect(find.text('Formation'), findsOneWidget);
      expect(find.text('Sécurité'), findsOneWidget);
      expect(find.text('Sondages'), findsOneWidget);
    });

    testWidgets('calls onTypeChanged when tab tapped', (tester) async {
      String? selected;
      await tester.pumpWidget(wrap(
        ContentTabs(
          selectedType: 'all',
          onTypeChanged: (type) => selected = type,
        ),
      ));

      await tester.tap(find.text('Formation'));
      expect(selected, 'training');
    });
  });
}
