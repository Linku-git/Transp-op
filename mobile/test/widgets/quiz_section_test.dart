import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/training.dart';
import 'package:transpop_mobile/widgets/training/quiz_section.dart';

void main() {
  Widget wrap(Widget child) {
    return MaterialApp(home: Scaffold(body: SingleChildScrollView(child: child)));
  }

  final questions = [
    const QuizQuestion(
      id: 'q1',
      text: 'Quelle est la vitesse max en ville ?',
      options: [
        QuizOption(text: '30 km/h'),
        QuizOption(text: '50 km/h'),
        QuizOption(text: '70 km/h'),
      ],
      correctIndex: 1,
    ),
    const QuizQuestion(
      id: 'q2',
      text: 'Port de la ceinture ?',
      options: [
        QuizOption(text: 'Obligatoire'),
        QuizOption(text: 'Facultatif'),
      ],
      correctIndex: 0,
    ),
  ];

  group('QuizSection', () {
    testWidgets('renders all questions', (tester) async {
      await tester.pumpWidget(wrap(
        QuizSection(
          questions: questions,
          selectedAnswers: const {},
          onAnswerSelected: (_) {},
        ),
      ));

      expect(find.text('Question 1'), findsOneWidget);
      expect(find.text('Question 2'), findsOneWidget);
      expect(find.text('Quelle est la vitesse max en ville ?'), findsOneWidget);
      expect(find.text('Port de la ceinture ?'), findsOneWidget);
    });

    testWidgets('renders all options', (tester) async {
      await tester.pumpWidget(wrap(
        QuizSection(
          questions: questions,
          selectedAnswers: const {},
          onAnswerSelected: (_) {},
        ),
      ));

      expect(find.text('30 km/h'), findsOneWidget);
      expect(find.text('50 km/h'), findsOneWidget);
      expect(find.text('70 km/h'), findsOneWidget);
      expect(find.text('Obligatoire'), findsOneWidget);
      expect(find.text('Facultatif'), findsOneWidget);
    });

    testWidgets('shows progress counter', (tester) async {
      await tester.pumpWidget(wrap(
        QuizSection(
          questions: questions,
          selectedAnswers: const {'q1': 0},
          onAnswerSelected: (_) {},
        ),
      ));

      expect(find.text('1/2'), findsOneWidget);
    });

    testWidgets('submit button disabled when quiz incomplete', (tester) async {
      await tester.pumpWidget(wrap(
        QuizSection(
          questions: questions,
          selectedAnswers: const {'q1': 0},
          onAnswerSelected: (_) {},
          canSubmit: false,
          onSubmit: () {},
        ),
      ));

      final button = tester.widget<FilledButton>(find.byType(FilledButton));
      expect(button.onPressed, isNull);
    });

    testWidgets('submit button enabled when quiz complete', (tester) async {
      bool submitted = false;
      await tester.pumpWidget(wrap(
        QuizSection(
          questions: questions,
          selectedAnswers: const {'q1': 0, 'q2': 0},
          onAnswerSelected: (_) {},
          canSubmit: true,
          onSubmit: () => submitted = true,
        ),
      ));

      await tester.tap(find.text('Soumettre le quiz'));
      expect(submitted, true);
    });

    testWidgets('calls onAnswerSelected when option tapped', (tester) async {
      MapEntry<String, int>? selected;
      await tester.pumpWidget(wrap(
        QuizSection(
          questions: questions,
          selectedAnswers: const {},
          onAnswerSelected: (entry) => selected = entry,
        ),
      ));

      await tester.tap(find.text('50 km/h'));
      expect(selected?.key, 'q1');
      expect(selected?.value, 1);
    });
  });
}
