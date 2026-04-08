import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/loading_indicator.dart';
import 'package:transpop_mobile/widgets/error_widget.dart';
import 'package:transpop_mobile/widgets/empty_state.dart';

void main() {
  group('LoadingIndicator', () {
    testWidgets('renders circular progress', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: LoadingIndicator()),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows message when provided', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: LoadingIndicator(message: 'Chargement...')),
        ),
      );

      expect(find.text('Chargement...'), findsOneWidget);
    });
  });

  group('AppErrorWidget', () {
    testWidgets('renders error message', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: AppErrorWidget(message: 'Une erreur est survenue')),
        ),
      );

      expect(find.text('Une erreur est survenue'), findsOneWidget);
      expect(find.byIcon(Icons.error_outline), findsOneWidget);
    });

    testWidgets('shows retry button when onRetry provided', (WidgetTester tester) async {
      bool retried = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppErrorWidget(
              message: 'Erreur',
              onRetry: () => retried = true,
            ),
          ),
        ),
      );

      expect(find.text('Réessayer'), findsOneWidget);
      await tester.tap(find.text('Réessayer'));
      expect(retried, true);
    });

    testWidgets('hides retry button when onRetry is null', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: AppErrorWidget(message: 'Erreur')),
        ),
      );

      expect(find.text('Réessayer'), findsNothing);
    });
  });

  group('EmptyState', () {
    testWidgets('renders title and icon', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: EmptyState(title: 'Aucun trajet')),
        ),
      );

      expect(find.text('Aucun trajet'), findsOneWidget);
      expect(find.byIcon(Icons.inbox_outlined), findsOneWidget);
    });

    testWidgets('shows subtitle when provided', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: EmptyState(
              title: 'Aucun trajet',
              subtitle: 'Réservez votre premier trajet',
            ),
          ),
        ),
      );

      expect(find.text('Réservez votre premier trajet'), findsOneWidget);
    });

    testWidgets('shows action widget when provided', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EmptyState(
              title: 'Vide',
              action: ElevatedButton(
                onPressed: () {},
                child: const Text('Ajouter'),
              ),
            ),
          ),
        ),
      );

      expect(find.text('Ajouter'), findsOneWidget);
    });
  });
}
