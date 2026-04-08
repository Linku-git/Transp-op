import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/content_feed.dart';
import 'package:transpop_mobile/widgets/content/content_card.dart';

void main() {
  Widget wrap(Widget child) {
    return MaterialApp(home: Scaffold(body: child));
  }

  group('ContentCard', () {
    final newsItem = FeedContent(
      id: '1',
      title: 'Nouvelle route disponible',
      body: '<p>Une nouvelle route a été ajoutée</p>',
      contentType: 'news',
      publishedAt: DateTime(2026, 4, 8),
      delivered: false,
      viewed: false,
    );

    final trainingItem = FeedContent(
      id: '2',
      title: 'Formation sécurité routière',
      body: '<p>Formation obligatoire</p>',
      contentType: 'training',
      publishedAt: DateTime(2026, 4, 7),
      delivered: true,
      viewed: true,
      completed: true,
    );

    testWidgets('renders title and snippet', (tester) async {
      await tester.pumpWidget(wrap(ContentCard(item: newsItem)));

      expect(find.text('Nouvelle route disponible'), findsOneWidget);
    });

    testWidgets('shows type badge for news', (tester) async {
      await tester.pumpWidget(wrap(ContentCard(item: newsItem)));

      expect(find.text('Actualité'), findsOneWidget);
    });

    testWidgets('shows type badge for training', (tester) async {
      await tester.pumpWidget(wrap(ContentCard(item: trainingItem)));

      expect(find.text('Formation'), findsOneWidget);
    });

    testWidgets('shows NEW badge for undelivered content', (tester) async {
      await tester.pumpWidget(wrap(ContentCard(item: newsItem)));

      expect(find.text('NEW'), findsOneWidget);
    });

    testWidgets('shows check icon for completed content', (tester) async {
      await tester.pumpWidget(wrap(ContentCard(item: trainingItem)));

      expect(find.byIcon(Icons.check_circle), findsOneWidget);
    });

    testWidgets('does not show NEW badge for delivered content', (tester) async {
      await tester.pumpWidget(wrap(ContentCard(item: trainingItem)));

      expect(find.text('NEW'), findsNothing);
    });

    testWidgets('calls onTap when tapped', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(wrap(
        ContentCard(item: newsItem, onTap: () => tapped = true),
      ));

      await tester.tap(find.byType(ContentCard));
      expect(tapped, true);
    });
  });
}
