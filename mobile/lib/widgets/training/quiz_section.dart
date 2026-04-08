import 'package:flutter/material.dart';

import '../../models/training.dart';

class QuizSection extends StatelessWidget {
  final List<QuizQuestion> questions;
  final Map<String, int> selectedAnswers;
  final ValueChanged<MapEntry<String, int>> onAnswerSelected;
  final VoidCallback? onSubmit;
  final bool canSubmit;
  final bool isSubmitting;

  const QuizSection({
    super.key,
    required this.questions,
    required this.selectedAnswers,
    required this.onAnswerSelected,
    this.onSubmit,
    this.canSubmit = false,
    this.isSubmitting = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              Icon(Icons.quiz_outlined,
                  size: 20, color: theme.colorScheme.primary),
              const SizedBox(width: 8),
              Text(
                'Quiz',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              Text(
                '${selectedAnswers.length}/${questions.length}',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),

        // Questions
        ...questions.asMap().entries.map((entry) {
          final index = entry.key;
          final q = entry.value;
          return QuizQuestionWidget(
            number: index + 1,
            question: q,
            selectedIndex: selectedAnswers[q.id],
            onOptionSelected: (optionIndex) {
              onAnswerSelected(MapEntry(q.id, optionIndex));
            },
          );
        }),

        // Submit button
        Padding(
          padding: const EdgeInsets.all(16),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton(
              onPressed: canSubmit && !isSubmitting ? onSubmit : null,
              child: isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('Soumettre le quiz'),
            ),
          ),
        ),
      ],
    );
  }
}

class QuizQuestionWidget extends StatelessWidget {
  final int number;
  final QuizQuestion question;
  final int? selectedIndex;
  final ValueChanged<int> onOptionSelected;

  const QuizQuestionWidget({
    super.key,
    required this.number,
    required this.question,
    this.selectedIndex,
    required this.onOptionSelected,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Question $number',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.primary,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                question.text,
                style: theme.textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 12),
              ...question.options.asMap().entries.map((entry) {
                final optIndex = entry.key;
                final option = entry.value;
                final isSelected = selectedIndex == optIndex;

                return Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: InkWell(
                    onTap: () => onOptionSelected(optIndex),
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 10,
                      ),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        color: isSelected
                            ? theme.colorScheme.primaryContainer
                            : theme.colorScheme.surfaceContainerHigh
                                .withValues(alpha: 0.5),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            isSelected
                                ? Icons.radio_button_checked
                                : Icons.radio_button_unchecked,
                            size: 20,
                            color: isSelected
                                ? theme.colorScheme.primary
                                : theme.colorScheme.onSurfaceVariant,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              option.text,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                color: isSelected
                                    ? theme.colorScheme.onPrimaryContainer
                                    : null,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }),
            ],
          ),
        ),
      ),
    );
  }
}
