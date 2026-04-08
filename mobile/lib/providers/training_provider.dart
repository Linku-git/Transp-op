import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/training.dart';
import '../services/training_service.dart';
import '../services/api_client.dart';
import 'auth_provider.dart';

final trainingServiceProvider = Provider<TrainingService>((ref) {
  return TrainingService(apiClient: ref.watch(apiClientProvider));
});

class TrainingPlayerState {
  final TrainingContent? training;
  final bool isLoading;
  final String? error;

  // Playback state
  final bool isPlaying;
  final bool mediaCompleted;
  final Duration position;
  final Duration duration;

  // Quiz state
  final bool showQuiz;
  final Map<String, int> selectedAnswers;
  final QuizResult? quizResult;
  final bool isSubmitting;

  // Time tracking
  final DateTime? startedAt;

  const TrainingPlayerState({
    this.training,
    this.isLoading = false,
    this.error,
    this.isPlaying = false,
    this.mediaCompleted = false,
    this.position = Duration.zero,
    this.duration = Duration.zero,
    this.showQuiz = false,
    this.selectedAnswers = const {},
    this.quizResult,
    this.isSubmitting = false,
    this.startedAt,
  });

  int get timeSpentSeconds {
    if (startedAt == null) return 0;
    return DateTime.now().difference(startedAt!).inSeconds;
  }

  bool get canSubmitQuiz {
    if (training == null) return false;
    return selectedAnswers.length == training!.questions.length;
  }

  TrainingPlayerState copyWith({
    TrainingContent? training,
    bool? isLoading,
    String? error,
    bool? isPlaying,
    bool? mediaCompleted,
    Duration? position,
    Duration? duration,
    bool? showQuiz,
    Map<String, int>? selectedAnswers,
    QuizResult? quizResult,
    bool? isSubmitting,
    DateTime? startedAt,
    bool clearError = false,
    bool clearResult = false,
  }) {
    return TrainingPlayerState(
      training: training ?? this.training,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      isPlaying: isPlaying ?? this.isPlaying,
      mediaCompleted: mediaCompleted ?? this.mediaCompleted,
      position: position ?? this.position,
      duration: duration ?? this.duration,
      showQuiz: showQuiz ?? this.showQuiz,
      selectedAnswers: selectedAnswers ?? this.selectedAnswers,
      quizResult: clearResult ? null : (quizResult ?? this.quizResult),
      isSubmitting: isSubmitting ?? this.isSubmitting,
      startedAt: startedAt ?? this.startedAt,
    );
  }
}

class TrainingPlayerNotifier extends StateNotifier<TrainingPlayerState> {
  final TrainingService _service;
  final String? _employeeId;

  TrainingPlayerNotifier(this._service, this._employeeId)
      : super(const TrainingPlayerState());

  Future<void> load(String contentId) async {
    state = state.copyWith(
      isLoading: true,
      clearError: true,
      startedAt: DateTime.now(),
    );
    try {
      final training = await _service.getTraining(contentId);
      await _service.cacheTraining(training);

      // Mark as viewed
      if (_employeeId != null) {
        await _service.markViewed(contentId, _employeeId);
      }

      state = state.copyWith(
        training: training,
        isLoading: false,
        showQuiz: !training.hasMedia && training.hasQuiz,
      );
    } catch (_) {
      // Try offline cache
      final cached = await _service.getCachedTraining(contentId);
      if (cached != null) {
        state = state.copyWith(training: cached, isLoading: false);
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Impossible de charger la formation',
        );
      }
    }
  }

  void onMediaCompleted() {
    state = state.copyWith(
      mediaCompleted: true,
      isPlaying: false,
      showQuiz: state.training?.hasQuiz ?? false,
    );
  }

  void updatePlayback({
    bool? isPlaying,
    Duration? position,
    Duration? duration,
  }) {
    state = state.copyWith(
      isPlaying: isPlaying,
      position: position,
      duration: duration,
    );
  }

  void selectAnswer(String questionId, int optionIndex) {
    final updated = Map<String, int>.from(state.selectedAnswers);
    updated[questionId] = optionIndex;
    state = state.copyWith(selectedAnswers: updated);
  }

  Future<void> submitQuiz() async {
    final training = state.training;
    if (training == null || !state.canSubmitQuiz) return;

    state = state.copyWith(isSubmitting: true);

    int correct = 0;
    for (final q in training.questions) {
      final selected = state.selectedAnswers[q.id];
      if (selected == q.correctIndex) correct++;
    }

    final result = QuizResult(
      totalQuestions: training.questions.length,
      correctAnswers: correct,
      passingScore: training.passingScore,
    );

    // Submit to backend
    if (_employeeId != null) {
      try {
        await _service.submitScore(
          contentId: training.id,
          employeeId: _employeeId,
          score: result.scorePercent,
          timeSpentSeconds: state.timeSpentSeconds,
        );
      } catch (_) {
        // Non-critical — score submission failure shouldn't block UX
      }
    }

    state = state.copyWith(quizResult: result, isSubmitting: false);
  }

  void retryQuiz() {
    state = state.copyWith(
      selectedAnswers: {},
      clearResult: true,
    );
  }
}

final trainingPlayerProvider =
    StateNotifierProvider.autoDispose<TrainingPlayerNotifier, TrainingPlayerState>(
        (ref) {
  final service = ref.watch(trainingServiceProvider);
  final authState = ref.watch(authProvider);
  return TrainingPlayerNotifier(service, authState.user?.id);
});
