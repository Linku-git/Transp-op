import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/survey.dart';
import 'package:transpop_mobile/providers/survey_provider.dart';

void main() {
  group('SurveyScreenState', () {
    test('initial state has correct defaults', () {
      const state = SurveyScreenState();
      expect(state.isLoading, false);
      expect(state.submitted, false);
      expect(state.answers, isEmpty);
      expect(state.currentQuestion, 0);
    });

    test('answeredCount counts non-null answers', () {
      final state = SurveyScreenState(
        survey: SurveyData(
          id: '1',
          title: 'Test',
          questions: [
            const SurveyQuestion(id: 'q1', text: 'Q1', questionType: 'text'),
            const SurveyQuestion(id: 'q2', text: 'Q2', questionType: 'text'),
            const SurveyQuestion(id: 'q3', text: 'Q3', questionType: 'text'),
          ],
        ),
        answers: const {'q1': 'answer1', 'q2': null, 'q3': 'answer3'},
      );
      expect(state.answeredCount, 2);
    });

    test('canSubmit is true when all required questions answered', () {
      final state = SurveyScreenState(
        survey: SurveyData(
          id: '1',
          title: 'Test',
          questions: [
            const SurveyQuestion(id: 'q1', text: 'Q1', questionType: 'text', required: true),
            const SurveyQuestion(id: 'q2', text: 'Q2', questionType: 'text', required: false),
          ],
        ),
        answers: const {'q1': 'answer1'},
      );
      expect(state.canSubmit, true);
    });

    test('canSubmit is false when required question unanswered', () {
      final state = SurveyScreenState(
        survey: SurveyData(
          id: '1',
          title: 'Test',
          questions: [
            const SurveyQuestion(id: 'q1', text: 'Q1', questionType: 'text', required: true),
            const SurveyQuestion(id: 'q2', text: 'Q2', questionType: 'text', required: true),
          ],
        ),
        answers: const {'q1': 'answer1'},
      );
      expect(state.canSubmit, false);
    });

    test('copyWith preserves values', () {
      const state = SurveyScreenState(
        isLoading: true,
        currentQuestion: 2,
      );
      final updated = state.copyWith(isLoading: false);
      expect(updated.isLoading, false);
      expect(updated.currentQuestion, 2);
    });

    test('copyWith clearError removes error', () {
      final state = SurveyScreenState(error: 'Some error');
      final updated = state.copyWith(clearError: true);
      expect(updated.error, isNull);
    });
  });
}
