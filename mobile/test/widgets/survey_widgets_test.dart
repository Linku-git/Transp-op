import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/widgets/survey/survey_progress.dart';
import 'package:transpop_mobile/widgets/survey/anonymous_indicator.dart';

void main() {
  Widget wrap(Widget child) {
    return MaterialApp(home: Scaffold(body: child));
  }

  group('SurveyProgress', () {
    testWidgets('shows question count', (tester) async {
      await tester.pumpWidget(wrap(
        const SurveyProgress(current: 3, total: 10, answeredCount: 2),
      ));
      expect(find.text('Question 3 sur 10'), findsOneWidget);
      expect(find.text('2/10 répondus'), findsOneWidget);
    });

    testWidgets('shows progress bar', (tester) async {
      await tester.pumpWidget(wrap(
        const SurveyProgress(current: 1, total: 5, answeredCount: 0),
      ));
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });
  });

  group('AnonymousIndicator', () {
    testWidgets('displays anonymous message', (tester) async {
      await tester.pumpWidget(wrap(const AnonymousIndicator()));
      expect(find.byIcon(Icons.visibility_off_outlined), findsOneWidget);
      expect(find.textContaining('anonyme'), findsOneWidget);
    });
  });
}
