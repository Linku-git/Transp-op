import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/trip_booking.dart';
import 'package:transpop_mobile/widgets/shift_selector.dart';

void main() {
  const shifts = [
    Shift(id: 's1', label: 'Poste 1', entryTime: '06:00', exitTime: '14:00'),
    Shift(id: 's2', label: 'Poste 2', entryTime: '14:00', exitTime: '22:00'),
  ];

  group('ShiftSelector', () {
    testWidgets('renders shift options', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ShiftSelector(
              shifts: shifts,
              onShiftSelected: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('Poste 1'), findsOneWidget);
      expect(find.text('Poste 2'), findsOneWidget);
      expect(find.text('06:00 — 14:00'), findsOneWidget);
      expect(find.text('14:00 — 22:00'), findsOneWidget);
    });

    testWidgets('calls onShiftSelected', (tester) async {
      Shift? selected;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ShiftSelector(
              shifts: shifts,
              onShiftSelected: (s) => selected = s,
            ),
          ),
        ),
      );

      await tester.tap(find.text('Poste 2'));
      expect(selected?.id, 's2');
    });

    testWidgets('shows loading state', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ShiftSelector(
              shifts: const [],
              onShiftSelected: (_) {},
              isLoading: true,
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows empty message', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ShiftSelector(
              shifts: const [],
              onShiftSelected: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('Aucun horaire disponible'), findsOneWidget);
    });
  });
}
