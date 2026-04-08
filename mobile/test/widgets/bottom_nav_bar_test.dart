import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/bottom_nav_bar.dart';

void main() {
  group('BottomNavBar', () {
    testWidgets('renders 5 navigation destinations', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            bottomNavigationBar: BottomNavBar(
              currentIndex: 0,
              onTap: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('Accueil'), findsOneWidget);
      expect(find.text('Trajets'), findsOneWidget);
      expect(find.text('Suivi'), findsOneWidget);
      expect(find.text('Contenu'), findsOneWidget);
      expect(find.text('Profil'), findsOneWidget);
    });

    testWidgets('calls onTap with correct index', (WidgetTester tester) async {
      int? tappedIndex;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            bottomNavigationBar: BottomNavBar(
              currentIndex: 0,
              onTap: (index) => tappedIndex = index,
            ),
          ),
        ),
      );

      await tester.tap(find.text('Trajets'));
      expect(tappedIndex, 1);

      await tester.tap(find.text('Profil'));
      expect(tappedIndex, 4);
    });
  });
}
