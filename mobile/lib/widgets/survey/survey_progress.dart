import 'package:flutter/material.dart';

class SurveyProgress extends StatelessWidget {
  final int current;
  final int total;
  final int answeredCount;

  const SurveyProgress({
    super.key,
    required this.current,
    required this.total,
    required this.answeredCount,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final progress = total > 0 ? answeredCount / total : 0.0;

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Question $current sur $total',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '$answeredCount/$total répondu${answeredCount > 1 ? 's' : ''}',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: LinearProgressIndicator(
            value: progress,
            borderRadius: BorderRadius.circular(4),
            minHeight: 4,
          ),
        ),
      ],
    );
  }
}
