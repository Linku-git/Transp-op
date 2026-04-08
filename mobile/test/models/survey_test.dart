import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/survey.dart';

void main() {
  group('SurveyData', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 's-1',
        'title': 'Enquête mobilité',
        'description': 'Donnez votre avis',
        'questions': [
          {
            'id': 'q1',
            'text': 'Transport préféré ?',
            'question_type': 'single_choice',
            'options': [
              {'text': 'Bus', 'value': 'bus'},
              {'text': 'Navette', 'value': 'shuttle'},
            ],
            'required': true,
          },
        ],
        'response_count': 42,
        'is_anonymous': true,
        'is_active': true,
      };

      final survey = SurveyData.fromJson(json);
      expect(survey.id, 's-1');
      expect(survey.title, 'Enquête mobilité');
      expect(survey.description, 'Donnez votre avis');
      expect(survey.questions.length, 1);
      expect(survey.responseCount, 42);
      expect(survey.isAnonymous, true);
    });

    test('requiredCount counts required questions', () {
      final survey = SurveyData(
        id: '1',
        title: 'Test',
        questions: [
          const SurveyQuestion(id: 'q1', text: 'Q1', questionType: 'text', required: true),
          const SurveyQuestion(id: 'q2', text: 'Q2', questionType: 'text', required: false),
          const SurveyQuestion(id: 'q3', text: 'Q3', questionType: 'text', required: true),
        ],
      );
      expect(survey.requiredCount, 2);
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'id': '1',
        'title': 'Test',
        'questions': [],
      };
      final survey = SurveyData.fromJson(json);
      expect(survey.description, isNull);
      expect(survey.isAnonymous, false);
      expect(survey.responseCount, 0);
    });
  });

  group('SurveyQuestion', () {
    test('fromJson parses options', () {
      final json = {
        'id': 'q1',
        'text': 'Choose one',
        'question_type': 'single_choice',
        'options': [
          {'text': 'A', 'value': 'a'},
          {'text': 'B'},
        ],
        'required': true,
      };
      final q = SurveyQuestion.fromJson(json);
      expect(q.options.length, 2);
      expect(q.options[0].effectiveValue, 'a');
      expect(q.options[1].effectiveValue, 'B'); // Falls back to text
    });

    test('fromJson parses slider with min/max', () {
      final json = {
        'id': 'q1',
        'text': 'Satisfaction',
        'question_type': 'slider',
        'min_value': 0,
        'max_value': 100,
      };
      final q = SurveyQuestion.fromJson(json);
      expect(q.minValue, 0);
      expect(q.maxValue, 100);
    });
  });

  group('SurveyAnswer', () {
    test('toJson serializes correctly', () {
      const answer = SurveyAnswer(questionId: 'q1', value: 'bus');
      final json = answer.toJson();
      expect(json['question_id'], 'q1');
      expect(json['value'], 'bus');
    });

    test('toJson handles list values', () {
      const answer = SurveyAnswer(
        questionId: 'q2',
        value: ['mon', 'wed', 'fri'],
      );
      final json = answer.toJson();
      expect(json['value'], isA<List>());
      expect((json['value'] as List).length, 3);
    });

    test('toJson handles numeric values', () {
      const answer = SurveyAnswer(questionId: 'q3', value: 4);
      final json = answer.toJson();
      expect(json['value'], 4);
    });
  });
}
