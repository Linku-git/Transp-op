import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/training_provider.dart';
import '../../widgets/training/media_player.dart';
import '../../widgets/training/quiz_section.dart';
import '../../widgets/training/score_display.dart';
import '../../widgets/loading_indicator.dart';

class TrainingPlayerScreen extends ConsumerStatefulWidget {
  final String contentId;

  const TrainingPlayerScreen({super.key, required this.contentId});

  @override
  ConsumerState<TrainingPlayerScreen> createState() =>
      _TrainingPlayerScreenState();
}

class _TrainingPlayerScreenState extends ConsumerState<TrainingPlayerScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(
      () => ref.read(trainingPlayerProvider.notifier).load(widget.contentId),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(trainingPlayerProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(state.training?.title ?? 'Formation'),
        actions: [
          // Time tracking indicator
          if (state.startedAt != null)
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Center(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.timer_outlined,
                      size: 16,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: 4),
                    _TimeDisplay(startedAt: state.startedAt!),
                  ],
                ),
              ),
            ),
        ],
      ),
      body: _buildBody(state, theme),
    );
  }

  Widget _buildBody(TrainingPlayerState state, ThemeData theme) {
    if (state.isLoading) {
      return const LoadingIndicator(message: 'Chargement de la formation...');
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
              onPressed: () => ref
                  .read(trainingPlayerProvider.notifier)
                  .load(widget.contentId),
              child: const Text('Réessayer'),
            ),
          ],
        ),
      );
    }

    final training = state.training;
    if (training == null) return const SizedBox.shrink();

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Media player
          if (training.hasMedia && !state.mediaCompleted)
            TrainingMediaPlayer(
              mediaUrl: training.mediaUrl!,
              mediaType: training.mediaType,
              onCompleted: () {
                ref.read(trainingPlayerProvider.notifier).onMediaCompleted();
              },
              onPositionChanged: (pos) {
                ref.read(trainingPlayerProvider.notifier).updatePlayback(
                  position: pos,
                );
              },
              onDurationChanged: (dur) {
                ref.read(trainingPlayerProvider.notifier).updatePlayback(
                  duration: dur,
                );
              },
            ),

          // Media completed banner
          if (state.mediaCompleted) _buildMediaCompletedBanner(theme),

          // Content body
          if (training.body != null && training.body!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                training.body!.replaceAll(RegExp(r'<[^>]*>'), ''),
                style: theme.textTheme.bodyLarge?.copyWith(height: 1.6),
              ),
            ),

          // Quiz result
          if (state.quizResult != null)
            ScoreDisplay(
              result: state.quizResult!,
              onRetry: state.quizResult!.passed
                  ? null
                  : () => ref.read(trainingPlayerProvider.notifier).retryQuiz(),
            ),

          // Quiz section
          if (state.showQuiz && state.quizResult == null && training.hasQuiz)
            QuizSection(
              questions: training.questions,
              selectedAnswers: state.selectedAnswers,
              onAnswerSelected: (entry) {
                ref
                    .read(trainingPlayerProvider.notifier)
                    .selectAnswer(entry.key, entry.value);
              },
              onSubmit: () =>
                  ref.read(trainingPlayerProvider.notifier).submitQuiz(),
              canSubmit: state.canSubmitQuiz,
              isSubmitting: state.isSubmitting,
            ),

          // No quiz, no media — simple completion
          if (!training.hasMedia &&
              !training.hasQuiz &&
              state.quizResult == null)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      Icon(Icons.check_circle,
                          size: 48, color: theme.colorScheme.primary),
                      const SizedBox(height: 12),
                      Text(
                        'Formation consultée',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildMediaCompletedBanner(ThemeData theme) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: Colors.green.withValues(alpha: 0.1),
      child: Row(
        children: [
          const Icon(Icons.check_circle, size: 20, color: Colors.green),
          const SizedBox(width: 8),
          Text(
            'Média terminé — Répondez au quiz ci-dessous',
            style: theme.textTheme.bodySmall?.copyWith(
              color: Colors.green.shade700,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

/// Live time counter widget.
class _TimeDisplay extends StatefulWidget {
  final DateTime startedAt;
  const _TimeDisplay({required this.startedAt});

  @override
  State<_TimeDisplay> createState() => _TimeDisplayState();
}

class _TimeDisplayState extends State<_TimeDisplay> {
  late final Stream<int> _ticker;

  @override
  void initState() {
    super.initState();
    _ticker = Stream.periodic(
      const Duration(seconds: 1),
      (_) => DateTime.now().difference(widget.startedAt).inSeconds,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return StreamBuilder<int>(
      stream: _ticker,
      builder: (context, snapshot) {
        final seconds = snapshot.data ?? 0;
        final minutes = seconds ~/ 60;
        final secs = seconds % 60;
        return Text(
          '${minutes.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}',
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
            fontFeatures: const [FontFeature.tabularFigures()],
          ),
        );
      },
    );
  }
}
