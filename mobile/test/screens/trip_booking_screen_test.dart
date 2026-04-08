import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/screens/trips/trip_booking_screen.dart';

void main() {
  Widget createTestWidget() {
    return const ProviderScope(
      child: MaterialApp(
        home: TripBookingScreen(),
      ),
    );
  }

  group('TripBookingScreen', () {
    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('Réserver un trajet'), findsOneWidget);
    });

    testWidgets('renders date section', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('DATE'), findsOneWidget);
    });

    testWidgets('renders shift section', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('HORAIRE'), findsOneWidget);
    });

    testWidgets('renders cancellation policy', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.textContaining('Annulation possible'), findsOneWidget);
    });

    testWidgets('renders confirm button', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('Confirmer la réservation'), findsOneWidget);
    });

    testWidgets('confirm button is disabled initially', (tester) async {
      await tester.pumpWidget(createTestWidget());
      final button = tester.widget<ElevatedButton>(
        find.widgetWithText(ElevatedButton, 'Confirmer la réservation'),
      );
      expect(button.onPressed, isNull);
    });
  });
}
