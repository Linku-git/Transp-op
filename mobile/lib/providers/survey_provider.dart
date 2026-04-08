import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/survey.dart';
import '../services/survey_service.dart';
import '../services/api_client.dart';
import 'auth_provider.dart';

final surveyServiceProvider = Provider<SurveyService>((ref) {
  return SurveyService(apiClient: ref.watch(apiClientProvider));
});

class SurveyScreenState {
  final SurveyData? survey;
  final bool isLoading;
  final String? error;
  final Map<String, dynamic> answers;
  final bool isSubmitting;
  final bool submitted;
  final int currentQuestion;

  const SurveyScreenState({
    this.survey,
    this.isLoading = false,
    this.error,
    this.answers = const {},
    this.isSubmitting = false,
    this.submitted = false,
    this.currentQuestion = 0,
  });

  int get answeredCount {
    if (survey == null) return 0;
    return survey!.questions
        .where((q) => answers.containsKey(q.id) && answers[q.id] != null)
        .length;
  }

  bool get canSubmit {
    if (survey == null) return false;
    for (final q in survey!.questions) {
      if (q.required && (!answers.containsKey(q.id) || answers[q.id] == null)) {
        return false;
      }
    }
    return true;
  }

  SurveyScreenState copyWith({
    SurveyData? survey,
    bool? isLoading,
    String? error,
    Map<String, dynamic>? answers,
    bool? isSubmitting,
    bool? submitted,
    int? currentQuestion,
    bool clearError = false,
  }) {
    return SurveyScreenState(
      survey: survey ?? this.survey,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      answers: answers ?? this.answers,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      submitted: submitted ?? this.submitted,
      currentQuestion: currentQuestion ?? this.currentQuestion,
    );
  }
}

class SurveyScreenNotifier extends StateNotifier<SurveyScreenState> {
  final SurveyService _service;
  final String? _employeeId;
  final bool _isOnline;

  SurveyScreenNotifier(this._service, this._employeeId, this._isOnline)
      : super(const SurveyScreenState());

  Future<void> load(String surveyId) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final survey = await _service.getSurvey(surveyId);
      state = state.copyWith(survey: survey, isLoading: false);
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        error: 'Impossible de charger le sondage',
      );
    }
  }

  void setAnswer(String questionId, dynamic value) {
    final updated = Map<String, dynamic>.from(state.answers);
    updated[questionId] = value;
    state = state.copyWith(answers: updated);
  }

  void setCurrentQuestion(int index) {
    state = state.copyWith(currentQuestion: index);
  }

  Future<void> submit() async {
    if (!state.canSubmit || state.survey == null) return;

    state = state.copyWith(isSubmitting: true);

    final surveyAnswers = state.answers.entries
        .map((e) => SurveyAnswer(questionId: e.key, value: e.value))
        .toList();

    if (_isOnline) {
      try {
        await _service.submitResponse(
          surveyId: state.survey!.id,
          employeeId: state.survey!.isAnonymous ? null : _employeeId,
          answers: surveyAnswers,
        );
        state = state.copyWith(submitted: true, isSubmitting: false);
      } catch (e) {
        // Queue for offline if submission fails
        await _service.queueOfflineResponse(
          surveyId: state.survey!.id,
          employeeId: state.survey!.isAnonymous ? null : _employeeId,
          answers: surveyAnswers,
        );
        state = state.copyWith(submitted: true, isSubmitting: false);
      }
    } else {
      await _service.queueOfflineResponse(
        surveyId: state.survey!.id,
        employeeId: state.survey!.isAnonymous ? null : _employeeId,
        answers: surveyAnswers,
      );
      state = state.copyWith(submitted: true, isSubmitting: false);
    }
  }
}

final surveyScreenProvider =
    StateNotifierProvider.autoDispose<SurveyScreenNotifier, SurveyScreenState>(
        (ref) {
  final service = ref.watch(surveyServiceProvider);
  final authState = ref.watch(authProvider);
  // Default to online; offline queue handles failures gracefully
  return SurveyScreenNotifier(service, authState.user?.id, true);
});
