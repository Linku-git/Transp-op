import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/stale_data_badge.dart';
import 'package:transpop_mobile/widgets/sync_spinner.dart';

void main() {
  group('StaleDataBadge', () {
    testWidgets('renders nothing when label is null', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: Scaffold(body: StaleDataBadge())),
      );
      expect(find.byType(StaleDataBadge), findsOneWidget);
      expect(find.byIcon(Icons.access_time), findsNothing);
    });

    testWidgets('renders label when provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: StaleDataBadge(label: 'Mis à jour il y a 2h')),
        ),
      );
      expect(find.text('Mis à jour il y a 2h'), findsOneWidget);
      expect(find.byIcon(Icons.access_time), findsOneWidget);
    });
  });

  group('SyncSpinner', () {
    testWidgets('renders nothing when not syncing', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: SyncSpinner(isSyncing: false)),
        ),
      );
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('renders spinner when syncing', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: SyncSpinner(isSyncing: true)),
        ),
      );
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Synchronisation...'), findsOneWidget);
    });

    testWidgets('renders custom label', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SyncSpinner(isSyncing: true, label: 'Envoi en cours...'),
          ),
        ),
      );
      expect(find.text('Envoi en cours...'), findsOneWidget);
    });
  });
}
