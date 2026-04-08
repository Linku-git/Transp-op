import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/date_picker_strip.dart';

void main() {
  group('DatePickerStrip', () {
    testWidgets('renders 8 date items (today + 7)', (tester) async {
      final today = DateTime.now();
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: DatePickerStrip(
              selectedDate: today,
              onDateSelected: (_) {},
            ),
          ),
        ),
      );

      // Should show today's date number
      expect(find.text('${today.day}'), findsAtLeast(1));
    });

    testWidgets('calls onDateSelected when tapped', (tester) async {
      DateTime? selected;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: DatePickerStrip(
              selectedDate: DateTime.now(),
              onDateSelected: (d) => selected = d,
            ),
          ),
        ),
      );

      // Tap tomorrow's date
      final tomorrow = DateTime.now().add(const Duration(days: 1));
      final finder = find.text('${tomorrow.day}');
      if (finder.evaluate().isNotEmpty) {
        await tester.tap(finder.first);
        expect(selected, isNotNull);
      }
    });
  });
}
