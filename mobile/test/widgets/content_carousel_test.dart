import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/departure.dart';
import 'package:transpop_mobile/widgets/content_carousel.dart';

void main() {
  group('ContentCarousel', () {
    final items = [
      ContentItem(
        id: '1',
        title: 'Nouvelle route disponible',
        snippet: 'Description',
        type: 'news',
        publishedAt: DateTime(2026, 4, 8),
      ),
      ContentItem(
        id: '2',
        title: 'Formation sécurité',
        snippet: 'Module obligatoire',
        type: 'training',
        publishedAt: DateTime(2026, 4, 7),
      ),
      ContentItem(
        id: '3',
        title: 'Sondage satisfaction',
        snippet: 'Donnez votre avis',
        type: 'survey',
        publishedAt: DateTime(2026, 4, 6),
        isRead: true,
      ),
    ];

    testWidgets('renders items', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ContentCarousel(items: items)),
        ),
      );

      expect(find.text('ACTUALITÉS'), findsOneWidget);
      expect(find.text('Nouvelle route disponible'), findsOneWidget);
      expect(find.text('Formation sécurité'), findsOneWidget);
    });

    testWidgets('renders nothing when empty', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ContentCarousel(items: const [])),
        ),
      );

      expect(find.text('ACTUALITÉS'), findsNothing);
    });

    testWidgets('type badges render correctly', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: ContentCarousel(items: items)),
        ),
      );

      expect(find.text('Actualité'), findsOneWidget);
      expect(find.text('Formation'), findsOneWidget);
    });

    testWidgets('tapping item calls onItemTap', (tester) async {
      String? tappedId;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ContentCarousel(
              items: items,
              onItemTap: (id) => tappedId = id,
            ),
          ),
        ),
      );

      await tester.tap(find.text('Nouvelle route disponible'));
      expect(tappedId, '1');
    });
  });
}
