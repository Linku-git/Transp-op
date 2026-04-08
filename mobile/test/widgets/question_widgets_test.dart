import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/survey.dart';
import 'package:transpop_mobile/widgets/survey/question_widgets.dart';

void main() {
  Widget wrap(Widget child) {
    return MaterialApp(home: Scaffold(body: SingleChildScrollView(child: child)));
  }

  group('RadioQuestion', () {
    final question = SurveyQuestion(
      id: 'q1',
      text: 'Transport préféré ?',
      questionType: 'single_choice',
      options: [
        const SurveyOption(text: 'Bus', value: 'bus'),
        const SurveyOption(text: 'Navette', value: 'shuttle'),
        const SurveyOption(text: 'Covoiturage', value: 'carpool'),
      ],
    );

    testWidgets('renders all options', (tester) async {
      await tester.pumpWidget(wrap(
        RadioQuestion(question: question, onChanged: (_) {}),
      ));
      expect(find.text('Bus'), findsOneWidget);
      expect(find.text('Navette'), findsOneWidget);
      expect(find.text('Covoiturage'), findsOneWidget);
    });

    testWidgets('calls onChanged when option selected', (tester) async {
      String? selected;
      await tester.pumpWidget(wrap(
        RadioQuestion(
          question: question,
          onChanged: (v) => selected = v,
        ),
      ));
      await tester.tap(find.text('Navette'));
      await tester.pump();
      expect(selected, 'shuttle');
    });
  });

  group('CheckboxQuestion', () {
    final question = SurveyQuestion(
      id: 'q2',
      text: 'Jours ?',
      questionType: 'multiple_choice',
      options: [
        const SurveyOption(text: 'Lundi', value: 'mon'),
        const SurveyOption(text: 'Mardi', value: 'tue'),
        const SurveyOption(text: 'Mercredi', value: 'wed'),
      ],
    );

    testWidgets('renders all options', (tester) async {
      await tester.pumpWidget(wrap(
        CheckboxQuestion(
          question: question,
          selectedValues: const [],
          onChanged: (_) {},
        ),
      ));
      expect(find.text('Lundi'), findsOneWidget);
      expect(find.text('Mardi'), findsOneWidget);
      expect(find.text('Mercredi'), findsOneWidget);
    });

    testWidgets('toggles selection', (tester) async {
      List<String>? result;
      await tester.pumpWidget(wrap(
        CheckboxQuestion(
          question: question,
          selectedValues: const ['mon'],
          onChanged: (v) => result = v,
        ),
      ));
      await tester.tap(find.text('Mardi'));
      await tester.pump();
      expect(result, containsAll(['mon', 'tue']));
    });
  });

  group('RatingQuestion', () {
    const question = SurveyQuestion(
      id: 'q3',
      text: 'Satisfaction ?',
      questionType: 'rating',
      maxValue: 5,
    );

    testWidgets('renders 5 stars', (tester) async {
      await tester.pumpWidget(wrap(
        RatingQuestion(question: question, onChanged: (_) {}),
      ));
      expect(find.byIcon(Icons.star_border), findsNWidgets(5));
    });

    testWidgets('fills stars on selection', (tester) async {
      int? rating;
      await tester.pumpWidget(wrap(
        RatingQuestion(
          question: question,
          selectedRating: 3,
          onChanged: (v) => rating = v,
        ),
      ));
      expect(find.byIcon(Icons.star), findsNWidgets(3));
      expect(find.byIcon(Icons.star_border), findsNWidgets(2));
    });
  });

  group('SliderQuestion', () {
    const question = SurveyQuestion(
      id: 'q4',
      text: 'Score',
      questionType: 'slider',
      minValue: 0,
      maxValue: 100,
    );

    testWidgets('renders slider', (tester) async {
      await tester.pumpWidget(wrap(
        SliderQuestion(question: question, onChanged: (_) {}),
      ));
      expect(find.byType(Slider), findsOneWidget);
      // Min and max labels are rendered (may appear more than once due to Slider label)
      expect(find.textContaining('0'), findsWidgets);
      expect(find.textContaining('100'), findsWidgets);
    });
  });

  group('TextQuestion', () {
    const question = SurveyQuestion(
      id: 'q5',
      text: 'Commentaires',
      questionType: 'text',
    );

    testWidgets('renders text field', (tester) async {
      await tester.pumpWidget(wrap(
        TextQuestion(
          question: question,
          value: '',
          onChanged: (_) {},
        ),
      ));
      expect(find.byType(TextField), findsOneWidget);
      expect(find.text('Votre réponse...'), findsOneWidget);
    });
  });
}
