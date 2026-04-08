import 'package:flutter/material.dart';

import '../../models/training.dart';

class ScoreDisplay extends StatelessWidget {
  final QuizResult result;
  final VoidCallback? onRetry;
  final String? certificateUrl;

  const ScoreDisplay({
    super.key,
    required this.result,
    this.onRetry,
    this.certificateUrl,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              // Result icon
              Icon(
                result.passed ? Icons.emoji_events : Icons.refresh,
                size: 56,
                color: result.passed ? Colors.amber : theme.colorScheme.error,
              ),
              const SizedBox(height: 16),

              // Title
              Text(
                result.passed ? 'Félicitations !' : 'Essayez encore',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),

              // Score
              Text(
                'Score : ${result.scoreLabel}',
                style: theme.textTheme.titleLarge?.copyWith(
                  color: result.passed
                      ? Colors.green
                      : theme.colorScheme.error,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),

              // Details
              Text(
                '${result.correctAnswers}/${result.totalQuestions} réponses correctes',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),

              if (!result.passed) ...[
                const SizedBox(height: 8),
                Text(
                  'Score minimum requis : ${result.passingScore}%',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],

              const SizedBox(height: 24),

              // Actions
              if (result.passed && certificateUrl != null) ...[
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: () {
                      // Open certificate URL
                    },
                    icon: const Icon(Icons.verified, size: 18),
                    label: const Text('Voir le certificat'),
                  ),
                ),
                const SizedBox(height: 8),
              ],

              if (!result.passed && onRetry != null)
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.tonal(
                    onPressed: onRetry,
                    child: const Text('Réessayer'),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
