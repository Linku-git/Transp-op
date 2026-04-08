import 'package:flutter/material.dart';
import '../../models/security_preferences.dart';

class SecurityQuestionnaireStep extends StatelessWidget {
  final SecurityPreferences preferences;
  final ValueChanged<SecurityPreferences> onChanged;

  const SecurityQuestionnaireStep({
    super.key,
    required this.preferences,
    required this.onChanged,
  });

  void _update(void Function(SecurityPreferences p) mutate) {
    mutate(preferences);
    onChanged(preferences);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Questionnaire sécurité',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Vos réponses nous aident à sécuriser vos trajets',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),

          // Safety rating (1-5 stars)
          Text(
            'PERCEPTION GLOBALE DE SÉCURITÉ',
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(5, (index) {
              final rating = index + 1;
              return IconButton(
                icon: Icon(
                  rating <= preferences.safetyRating
                      ? Icons.star_rounded
                      : Icons.star_outline_rounded,
                  size: 40,
                  color: rating <= preferences.safetyRating
                      ? Colors.amber
                      : theme.colorScheme.outlineVariant,
                ),
                onPressed: () => _update((p) => p.safetyRating = rating),
              );
            }),
          ),
          Center(
            child: Text(
              _ratingLabel(preferences.safetyRating),
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Vulnerable time slots
          Text(
            'CRÉNEAUX DE VULNÉRABILITÉ',
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Sélectionnez les créneaux où vous vous sentez moins en sécurité',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: TimeSlot.all.map((slot) {
              final isSelected =
                  preferences.vulnerableTimeSlots.contains(slot.key);
              return FilterChip(
                label: Text(slot.label),
                selected: isSelected,
                onSelected: (selected) {
                  _update((p) {
                    if (selected) {
                      p.vulnerableTimeSlots.add(slot.key);
                    } else {
                      p.vulnerableTimeSlots.remove(slot.key);
                    }
                  });
                },
                selectedColor: theme.colorScheme.error.withValues(alpha: 0.12),
                checkmarkColor: theme.colorScheme.error,
                labelStyle: TextStyle(
                  color: isSelected
                      ? theme.colorScheme.error
                      : theme.colorScheme.onSurface,
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),

          // Night walking distance
          Text(
            'DISTANCE DE MARCHE LA NUIT',
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              Expanded(
                child: Slider(
                  value: preferences.maxNightWalkingDistanceMeters,
                  min: 100,
                  max: 1000,
                  divisions: 18,
                  label:
                      '${preferences.maxNightWalkingDistanceMeters.round()} m',
                  onChanged: (v) =>
                      _update((p) => p.maxNightWalkingDistanceMeters = v),
                ),
              ),
              SizedBox(
                width: 64,
                child: Text(
                  '${preferences.maxNightWalkingDistanceMeters.round()} m',
                  style: theme.textTheme.titleSmall,
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Night concerns text
          Text(
            'PRÉOCCUPATIONS NOCTURNES',
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 8),
          TextFormField(
            initialValue: preferences.nightConcerns,
            decoration: const InputDecoration(
              hintText: 'Décrivez vos préoccupations (optionnel)',
            ),
            maxLines: 3,
            onChanged: (v) =>
                _update((p) => p.nightConcerns = v.isEmpty ? null : v),
          ),
        ],
      ),
    );
  }

  String _ratingLabel(int rating) {
    switch (rating) {
      case 1:
        return 'Très insécure';
      case 2:
        return 'Plutôt insécure';
      case 3:
        return 'Neutre';
      case 4:
        return 'Plutôt sécure';
      case 5:
        return 'Très sécure';
      default:
        return '';
    }
  }
}
