import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/training.dart';
import 'package:transpop_mobile/widgets/training/score_display.dart';

void main() {
  Widget wrap(Widget child) {
    return MaterialApp(home: Scaffold(body: SingleChildScrollView(child: child)));
  }

  group('ScoreDisplay', () {
    testWidgets('shows success for passing score', (tester) async {
      const result = QuizResult(
        totalQuestions: 5,
        correctAnswers: 4,
        passingScore: 70,
      );

      await tester.pumpWidget(wrap(ScoreDisplay(result: result)));

      expect(find.text('Félicitations !'), findsOneWidget);
      expect(find.text('Score : 80%'), findsOneWidget);
      expect(find.text('4/5 réponses correctes'), findsOneWidget);
    });

    testWidgets('shows retry for failing score', (tester) async {
      const result = QuizResult(
        totalQuestions: 5,
        correctAnswers: 2,
        passingScore: 70,
      );

      bool retried = false;
      await tester.pumpWidget(wrap(
        ScoreDisplay(result: result, onRetry: () => retried = true),
      ));

      expect(find.text('Essayez encore'), findsOneWidget);
      expect(find.text('Score : 40%'), findsOneWidget);
      expect(find.text('Score minimum requis : 70%'), findsOneWidget);

      await tester.tap(find.text('Réessayer'));
      expect(retried, true);
    });

    testWidgets('shows trophy icon for success', (tester) async {
      const result = QuizResult(
        totalQuestions: 3,
        correctAnswers: 3,
        passingScore: 70,
      );

      await tester.pumpWidget(wrap(ScoreDisplay(result: result)));
      expect(find.byIcon(Icons.emoji_events), findsOneWidget);
    });

    testWidgets('shows refresh icon for failure', (tester) async {
      const result = QuizResult(
        totalQuestions: 3,
        correctAnswers: 1,
        passingScore: 70,
      );

      await tester.pumpWidget(wrap(ScoreDisplay(result: result)));
      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });
  });
}
