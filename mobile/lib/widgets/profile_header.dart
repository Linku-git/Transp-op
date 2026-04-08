import 'package:flutter/material.dart';
import '../config/colors.dart';
import '../models/user_profile.dart';

class ProfileHeader extends StatelessWidget {
  final UserProfile profile;

  const ProfileHeader({super.key, required this.profile});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: [
        // Avatar
        CircleAvatar(
          radius: 40,
          backgroundColor: AppColors.primary,
          child: Text(
            profile.initials,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          profile.displayName,
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
        if (profile.matricule != null) ...[
          const SizedBox(height: 2),
          Text(
            'Matricule: ${profile.matricule}',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (profile.siteName != null)
              _InfoChip(icon: Icons.business, label: profile.siteName!),
            if (profile.shiftLabel != null) ...[
              const SizedBox(width: 8),
              _InfoChip(icon: Icons.schedule, label: profile.shiftLabel!),
            ],
          ],
        ),
        if (profile.transportMode != null) ...[
          const SizedBox(height: 8),
          TransportModeBadge(mode: profile.transportMode!),
        ],
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: theme.colorScheme.onSurfaceVariant),
          const SizedBox(width: 4),
          Text(label, style: theme.textTheme.labelSmall),
        ],
      ),
    );
  }
}

class TransportModeBadge extends StatelessWidget {
  final String mode;

  const TransportModeBadge({super.key, required this.mode});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final label = _modeLabel(mode);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_modeIcon(mode), size: 16, color: AppColors.primary),
          const SizedBox(width: 6),
          Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  String _modeLabel(String mode) => switch (mode) {
        'voiture' => 'Voiture',
        'transport_commun' => 'Transport en commun',
        'covoiturage' => 'Covoiturage',
        'taxi' => 'Taxi / VTC',
        'deux_roues' => 'Deux-roues',
        'marche' => 'Marche',
        'velo' => 'Vélo',
        _ => mode,
      };

  IconData _modeIcon(String mode) => switch (mode) {
        'voiture' => Icons.directions_car,
        'transport_commun' => Icons.directions_bus,
        'covoiturage' => Icons.people,
        'taxi' => Icons.local_taxi,
        'deux_roues' => Icons.two_wheeler,
        'marche' => Icons.directions_walk,
        'velo' => Icons.pedal_bike,
        _ => Icons.commute,
      };
}
