import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/night_mode_service.dart';

class NightModeToggle extends ConsumerWidget {
  const NightModeToggle({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nightMode = ref.watch(nightModeProvider);
    final notifier = ref.read(nightModeProvider.notifier);
    final theme = Theme.of(context);

    return Card(
      child: SwitchListTile(
        title: const Text('Mode nuit'),
        subtitle: Text(
          nightMode.preference == NightModePreference.auto
              ? 'Automatique (20h - 6h30)'
              : nightMode.isActive
                  ? 'Activé manuellement'
                  : 'Désactivé',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        value: nightMode.isActive,
        onChanged: (_) => notifier.toggle(),
        secondary: Icon(
          nightMode.isActive ? Icons.dark_mode : Icons.light_mode,
          color: nightMode.isActive ? Colors.amber : theme.colorScheme.outline,
        ),
      ),
    );
  }
}
