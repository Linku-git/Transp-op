import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip_booking.dart';
import 'package:transpop_mobile/widgets/booking_summary_card.dart';

void main() {
  group('BookingSummaryCard', () {
    testWidgets('renders summary header', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BookingSummaryCard(
              date: DateTime(2026, 4, 8),
            ),
          ),
        ),
      );

      expect(find.text('RÉCAPITULATIF'), findsOneWidget);
    });

    testWidgets('displays shift info when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BookingSummaryCard(
              date: DateTime(2026, 4, 8),
              shift: const Shift(
                id: 's1',
                label: 'Poste 1',
                entryTime: '06:00',
                exitTime: '14:00',
              ),
            ),
          ),
        ),
      );

      expect(find.textContaining('Poste 1'), findsOneWidget);
      expect(find.text('Horaire'), findsOneWidget);
    });

    testWidgets('displays pickup point when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: BookingSummaryCard(
              date: DateTime(2026, 4, 8),
              pickupPoint: const PickupPoint(
                id: 'pp1',
                name: 'Ain Sebaa',
                lat: 33.58,
                lng: -7.63,
              ),
            ),
          ),
        ),
      );

      expect(find.text('Ain Sebaa'), findsOneWidget);
      expect(find.text('Ramassage'), findsOneWidget);
    });
  });
}
