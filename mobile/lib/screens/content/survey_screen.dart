import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/survey.dart';
import '../../providers/survey_provider.dart';
import '../../widgets/survey/question_widgets.dart';
import '../../widgets/survey/survey_progress.dart';
import '../../widgets/survey/anonymous_indicator.dart';
import '../../widgets/loading_indicator.dart';

class SurveyScreen extends ConsumerStatefulWidget {
  final String surveyId;

  const SurveyScreen({super.key, required this.surveyId});

  @override
  ConsumerState<SurveyScreen> createState() => _SurveyScreenState();
}

class _SurveyScreenState extends ConsumerState<SurveyScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(surveyScreenProvider.notifier).load(widget.surveyId),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(surveyScreenProvider);
    final theme = Theme.of(context);

    if (state.submitted) return _buildConfirmation(theme);

    return Scaffold(
      appBar: AppBar(title: Text(state.survey?.title ?? 'Sondage')),
      body: _buildBody(state, theme),
    );
  }

  Widget _buildBody(SurveyScreenState state, ThemeData theme) {
    if (state.isLoading) {
      return const LoadingIndicator(message: 'Chargement du sondage...');
    }

    if (state.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
            const SizedBox(height: 12),
            Text(state.error!, style: theme.textTheme.bodyMedium),
            const SizedBox(height: 16),
            FilledButton.tonal(
              onPressed: () =>
                  ref.read(surveyScreenProvider.notifier).load(widget.surveyId),
              child: const Text('Réessayer'),
            ),
          ],
        ),
      );
    }

    final survey = state.survey;
    if (survey == null) return const SizedBox.shrink();

    return Column(
      children: [
        // Anonymous indicator
        if (survey.isAnonymous) const AnonymousIndicator(),

        // Progress
        SurveyProgress(
          current: state.currentQuestion + 1,
          total: survey.questions.length,
          answeredCount: state.answeredCount,
        ),

        // Questions
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: survey.questions.length + 1, // +1 for description
            itemBuilder: (context, index) {
              if (index == 0 && survey.description != null) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Text(
                    survey.description!,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                );
              }

              final qIndex =
                  survey.description != null ? index - 1 : index;
              if (qIndex < 0 || qIndex >= survey.questions.length) {
                return const SizedBox.shrink();
              }

              final question = survey.questions[qIndex];
              return _buildQuestion(question, qIndex, state, theme);
            },
          ),
        ),

        // Submit button
        Padding(
          padding: const EdgeInsets.all(16),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: state.canSubmit && !state.isSubmitting
                  ? () => ref.read(surveyScreenProvider.notifier).submit()
                  : null,
              child: state.isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('Soumettre'),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildQuestion(
    SurveyQuestion question,
    int index,
    SurveyScreenState state,
    ThemeData theme,
  ) {
    final notifier = ref.read(surveyScreenProvider.notifier);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Question header
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    question.text,
                    style: theme.textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                if (question.required)
                  Text(
                    ' *',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: theme.colorScheme.error,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),

            // Question input
            _buildQuestionInput(question, state, notifier),
          ],
        ),
      ),
    );
  }

  Widget _buildQuestionInput(
    SurveyQuestion question,
    SurveyScreenState state,
    SurveyScreenNotifier notifier,
  ) {
    final answer = state.answers[question.id];

    switch (question.questionType) {
      case 'single_choice':
        return RadioQuestion(
          question: question,
          selectedValue: answer as String?,
          onChanged: (v) => notifier.setAnswer(question.id, v),
        );

      case 'multiple_choice':
        return CheckboxQuestion(
          question: question,
          selectedValues:
              (answer as List<String>?) ?? [],
          onChanged: (v) => notifier.setAnswer(question.id, v),
        );

      case 'text':
        return TextQuestion(
          question: question,
          value: (answer as String?) ?? '',
          onChanged: (v) =>
              notifier.setAnswer(question.id, v.isEmpty ? null : v),
        );

      case 'rating':
        return RatingQuestion(
          question: question,
          selectedRating: answer as int?,
          onChanged: (v) => notifier.setAnswer(question.id, v),
        );

      case 'slider':
        return SliderQuestion(
          question: question,
          value: (answer as num?)?.toDouble(),
          onChanged: (v) => notifier.setAnswer(question.id, v.round()),
        );

      default:
        return Text('Type de question non supporté: ${question.questionType}');
    }
  }

  Widget _buildConfirmation(ThemeData theme) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.check_circle,
                size: 72,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(height: 24),
              Text(
                'Merci !',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Votre réponse a bien été enregistrée.',
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              FilledButton.tonal(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Retour au contenu'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
