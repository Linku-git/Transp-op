import 'package:flutter/material.dart';

import '../../models/survey.dart';

/// Radio button (single choice) question.
class RadioQuestion extends StatelessWidget {
  final SurveyQuestion question;
  final String? selectedValue;
  final ValueChanged<String> onChanged;

  const RadioQuestion({
    super.key,
    required this.question,
    this.selectedValue,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: question.options.map((option) {
        return RadioListTile<String>(
          value: option.effectiveValue,
          groupValue: selectedValue,
          onChanged: (v) {
            if (v != null) onChanged(v);
          },
          title: Text(option.text),
          dense: true,
          contentPadding: EdgeInsets.zero,
        );
      }).toList(),
    );
  }
}

/// Checkbox (multiple choice) question.
class CheckboxQuestion extends StatelessWidget {
  final SurveyQuestion question;
  final List<String> selectedValues;
  final ValueChanged<List<String>> onChanged;

  const CheckboxQuestion({
    super.key,
    required this.question,
    required this.selectedValues,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: question.options.map((option) {
        final val = option.effectiveValue;
        final isSelected = selectedValues.contains(val);
        return CheckboxListTile(
          value: isSelected,
          onChanged: (_) {
            final updated = List<String>.from(selectedValues);
            if (isSelected) {
              updated.remove(val);
            } else {
              updated.add(val);
            }
            onChanged(updated);
          },
          title: Text(option.text),
          dense: true,
          contentPadding: EdgeInsets.zero,
          controlAffinity: ListTileControlAffinity.leading,
        );
      }).toList(),
    );
  }
}

/// Free text question.
class TextQuestion extends StatelessWidget {
  final SurveyQuestion question;
  final String value;
  final ValueChanged<String> onChanged;

  const TextQuestion({
    super.key,
    required this.question,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return TextField(
      onChanged: onChanged,
      maxLines: 3,
      decoration: InputDecoration(
        hintText: 'Votre réponse...',
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        filled: true,
      ),
      controller: TextEditingController(text: value)
        ..selection = TextSelection.collapsed(offset: value.length),
    );
  }
}

/// Star rating question (1-5).
class RatingQuestion extends StatelessWidget {
  final SurveyQuestion question;
  final int? selectedRating;
  final ValueChanged<int> onChanged;

  const RatingQuestion({
    super.key,
    required this.question,
    this.selectedRating,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final maxRating = question.maxValue ?? 5;

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(maxRating, (index) {
        final rating = index + 1;
        final isSelected = selectedRating != null && rating <= selectedRating!;
        return IconButton(
          onPressed: () => onChanged(rating),
          icon: Icon(
            isSelected ? Icons.star : Icons.star_border,
            color: isSelected ? Colors.amber : theme.colorScheme.onSurfaceVariant,
            size: 36,
          ),
          tooltip: '$rating',
        );
      }),
    );
  }
}

/// Slider question.
class SliderQuestion extends StatelessWidget {
  final SurveyQuestion question;
  final double? value;
  final ValueChanged<double> onChanged;

  const SliderQuestion({
    super.key,
    required this.question,
    this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final minVal = (question.minValue ?? 0).toDouble();
    final maxVal = (question.maxValue ?? 100).toDouble();
    final current = value ?? minVal;

    return Column(
      children: [
        Slider(
          value: current.clamp(minVal, maxVal),
          min: minVal,
          max: maxVal,
          divisions: (maxVal - minVal).round(),
          label: current.round().toString(),
          onChanged: onChanged,
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                minVal.round().toString(),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              Text(
                current.round().toString(),
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: theme.colorScheme.primary,
                ),
              ),
              Text(
                maxVal.round().toString(),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
