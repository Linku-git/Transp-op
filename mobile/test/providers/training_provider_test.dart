import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/training.dart';
import 'package:transpop_mobile/providers/training_provider.dart';

void main() {
  group('TrainingPlayerState', () {
    test('initial state has correct defaults', () {
      const state = TrainingPlayerState();
      expect(state.isLoading, false);
      expect(state.isPlaying, false);
      expect(state.mediaCompleted, false);
      expect(state.showQuiz, false);
      expect(state.selectedAnswers, isEmpty);
      expect(state.quizResult, isNull);
    });

    test('canSubmitQuiz is false without training', () {
      const state = TrainingPlayerState();
      expect(state.canSubmitQuiz, false);
    });

    test('canSubmitQuiz is true when all questions answered', () {
      const training = TrainingContent(
        id: '1',
        title: 'Test',
        questions: [
          QuizQuestion(
            id: 'q1',
            text: 'Q1',
            options: [QuizOption(text: 'A'), QuizOption(text: 'B')],
            correctIndex: 0,
          ),
          QuizQuestion(
            id: 'q2',
            text: 'Q2',
            options: [QuizOption(text: 'A'), QuizOption(text: 'B')],
            correctIndex: 1,
          ),
        ],
      );

      final state = TrainingPlayerState(
        training: training,
        selectedAnswers: const {'q1': 0, 'q2': 1},
      );
      expect(state.canSubmitQuiz, true);
    });

    test('canSubmitQuiz is false when not all answered', () {
      const training = TrainingContent(
        id: '1',
        title: 'Test',
        questions: [
          QuizQuestion(
            id: 'q1',
            text: 'Q1',
            options: [QuizOption(text: 'A')],
            correctIndex: 0,
          ),
          QuizQuestion(
            id: 'q2',
            text: 'Q2',
            options: [QuizOption(text: 'A')],
            correctIndex: 0,
          ),
        ],
      );

      final state = TrainingPlayerState(
        training: training,
        selectedAnswers: const {'q1': 0},
      );
      expect(state.canSubmitQuiz, false);
    });

    test('timeSpentSeconds calculates from startedAt', () {
      final startedAt = DateTime.now().subtract(const Duration(minutes: 2));
      final state = TrainingPlayerState(startedAt: startedAt);
      expect(state.timeSpentSeconds, greaterThanOrEqualTo(119));
    });

    test('copyWith preserves existing values', () {
      const state = TrainingPlayerState(
        isPlaying: true,
        mediaCompleted: false,
      );
      final updated = state.copyWith(mediaCompleted: true);
      expect(updated.isPlaying, true);
      expect(updated.mediaCompleted, true);
    });

    test('copyWith clearError removes error', () {
      final state = TrainingPlayerState(error: 'Some error');
      final updated = state.copyWith(clearError: true);
      expect(updated.error, isNull);
    });
  });
}
