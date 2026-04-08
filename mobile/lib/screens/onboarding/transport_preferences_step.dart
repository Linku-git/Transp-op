import 'package:flutter/material.dart';
import '../../models/transport_preferences.dart';

class TransportPreferencesStep extends StatelessWidget {
  final TransportPreferences preferences;
  final ValueChanged<TransportPreferences> onChanged;

  const TransportPreferencesStep({
    super.key,
    required this.preferences,
    required this.onChanged,
  });

  void _update(void Function(TransportPreferences p) mutate) {
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
            'Vos préférences de transport',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Aidez-nous à personnaliser votre expérience',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 24),

          // Transport mode selector
          Text(
            'MODE DE TRANSPORT ACTUEL',
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
            children: TransportMode.all.map((mode) {
              final isSelected = preferences.currentMode == mode.key;
              return ChoiceChip(
                label: Text(mode.label),
                selected: isSelected,
                onSelected: (_) => _update((p) => p.currentMode = mode.key),
                selectedColor: theme.colorScheme.primary.withValues(alpha: 0.15),
                labelStyle: TextStyle(
                  color: isSelected
                      ? theme.colorScheme.primary
                      : theme.colorScheme.onSurface,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 24),

          // Company transport interest
          _SwitchTile(
            title: 'Transport entreprise',
            subtitle: 'Je suis intéressé(e) par le transport collectif',
            value: preferences.interestedInCompanyTransport,
            onChanged: (v) => _update((p) => p.interestedInCompanyTransport = v),
          ),
          const SizedBox(height: 8),

          // Private car
          _SwitchTile(
            title: 'Véhicule personnel',
            subtitle: 'Je possède un véhicule personnel',
            value: preferences.hasPrivateCar,
            onChanged: (v) => _update((p) {
              p.hasPrivateCar = v;
              if (!v) p.volunteerDriver = false;
            }),
          ),
          const SizedBox(height: 8),

          // Volunteer driver (only if has car)
          if (preferences.hasPrivateCar) ...[
            _SwitchTile(
              title: 'Conducteur volontaire',
              subtitle: 'Je souhaite proposer des places de covoiturage',
              value: preferences.volunteerDriver,
              onChanged: (v) => _update((p) => p.volunteerDriver = v),
            ),
            const SizedBox(height: 8),
          ],

          // Carpool seats
          if (preferences.volunteerDriver) ...[
            Text(
              'PLACES DISPONIBLES',
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
                    value: preferences.carpoolSeats.toDouble(),
                    min: 1,
                    max: 4,
                    divisions: 3,
                    label: '${preferences.carpoolSeats} places',
                    onChanged: (v) =>
                        _update((p) => p.carpoolSeats = v.round()),
                  ),
                ),
                SizedBox(
                  width: 48,
                  child: Text(
                    '${preferences.carpoolSeats}',
                    style: theme.textTheme.titleMedium,
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
          ],

          // Walking distance slider
          Text(
            'DISTANCE DE MARCHE MAXIMALE',
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
                  value: preferences.maxWalkingDistanceMeters,
                  min: 200,
                  max: 2000,
                  divisions: 18,
                  label: '${preferences.maxWalkingDistanceMeters.round()} m',
                  onChanged: (v) =>
                      _update((p) => p.maxWalkingDistanceMeters = v),
                ),
              ),
              SizedBox(
                width: 64,
                child: Text(
                  '${preferences.maxWalkingDistanceMeters.round()} m',
                  style: theme.textTheme.titleSmall,
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SwitchTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SwitchTile({
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: SwitchListTile(
        title: Text(title, style: theme.textTheme.titleSmall),
        subtitle: Text(
          subtitle,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        value: value,
        onChanged: onChanged,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      ),
    );
  }
}
