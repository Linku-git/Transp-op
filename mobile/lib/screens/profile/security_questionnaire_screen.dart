import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/security_preferences.dart';
import '../../providers/auth_provider.dart';
import '../../utils/api_error.dart';

class SecurityQuestionnaireScreen extends ConsumerStatefulWidget {
  const SecurityQuestionnaireScreen({super.key});

  @override
  ConsumerState<SecurityQuestionnaireScreen> createState() =>
      _SecurityQuestionnaireScreenState();
}

class _SecurityQuestionnaireScreenState
    extends ConsumerState<SecurityQuestionnaireScreen> {
  final _prefs = SecurityPreferences();
  bool _isSaving = false;
  String? _error;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Questionnaire sécurité')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Safety rating
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
                    rating <= _prefs.safetyRating
                        ? Icons.star_rounded
                        : Icons.star_outline_rounded,
                    size: 40,
                    color: rating <= _prefs.safetyRating
                        ? Colors.amber
                        : theme.colorScheme.outlineVariant,
                  ),
                  onPressed: () => setState(() => _prefs.safetyRating = rating),
                );
              }),
            ),
            const SizedBox(height: 24),

            // Time slots
            Text(
              'CRÉNEAUX DE VULNÉRABILITÉ',
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: TimeSlot.all.map((slot) {
                final isSelected = _prefs.vulnerableTimeSlots.contains(slot.key);
                return FilterChip(
                  label: Text(slot.label),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _prefs.vulnerableTimeSlots.add(slot.key);
                      } else {
                        _prefs.vulnerableTimeSlots.remove(slot.key);
                      }
                    });
                  },
                  selectedColor: theme.colorScheme.error.withValues(alpha: 0.12),
                  checkmarkColor: theme.colorScheme.error,
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
            Slider(
              value: _prefs.maxNightWalkingDistanceMeters,
              min: 100,
              max: 1000,
              divisions: 18,
              label: '${_prefs.maxNightWalkingDistanceMeters.round()} m',
              onChanged: (v) => setState(() => _prefs.maxNightWalkingDistanceMeters = v),
            ),
            Center(
              child: Text(
                '${_prefs.maxNightWalkingDistanceMeters.round()} mètres',
                style: theme.textTheme.titleSmall,
              ),
            ),
            const SizedBox(height: 24),

            // Night concerns
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
              initialValue: _prefs.nightConcerns,
              maxLines: 3,
              decoration: const InputDecoration(hintText: 'Décrivez vos préoccupations (optionnel)'),
              onChanged: (v) => _prefs.nightConcerns = v.isEmpty ? null : v,
            ),

            if (_error != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(_error!, style: TextStyle(color: theme.colorScheme.onErrorContainer, fontSize: 13)),
              ),
            ],

            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: _isSaving ? null : _save,
                child: _isSaving
                    ? const SizedBox(width: 22, height: 22, child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white))
                    : const Text('Enregistrer', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _save() async {
    setState(() { _isSaving = true; _error = null; });
    try {
      final apiClient = ref.read(apiClientProvider);
      await apiClient.dio.post(
        '/security/questionnaire',
        data: {
          'overall_safety_rating': _prefs.safetyRating,
          'responses': {
            'vulnerable_time_slots': _prefs.vulnerableTimeSlots,
            'max_night_walking_distance': _prefs.maxNightWalkingDistanceMeters.round(),
          },
          'vulnerable_stops': [],
          'night_concerns': _prefs.nightConcerns,
          'trigger_type': 'periodic',
        },
      );
      if (mounted) context.pop();
    } catch (e) {
      setState(() { _error = extractApiError(e, 'Erreur de sauvegarde'); });
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }
}
