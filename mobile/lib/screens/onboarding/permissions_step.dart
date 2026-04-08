import 'package:flutter/material.dart';
import '../../config/colors.dart';

class PermissionsStep extends StatelessWidget {
  final bool locationGranted;
  final bool notificationsGranted;
  final VoidCallback onRequestLocation;
  final VoidCallback onRequestNotifications;

  const PermissionsStep({
    super.key,
    required this.locationGranted,
    required this.notificationsGranted,
    required this.onRequestLocation,
    required this.onRequestNotifications,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Autorisations',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Pour profiter de toutes les fonctionnalités',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 32),

          // Location permission
          _PermissionCard(
            icon: Icons.location_on_outlined,
            title: 'Localisation',
            description:
                'Utilisée uniquement lorsque l\'application est active pour afficher votre position et calculer les distances de marche.',
            granted: locationGranted,
            onRequest: onRequestLocation,
          ),
          const SizedBox(height: 16),

          // Notifications permission
          _PermissionCard(
            icon: Icons.notifications_outlined,
            title: 'Notifications',
            description:
                'Recevez des alertes 2 minutes avant l\'arrivée de votre véhicule et des informations importantes sur vos trajets.',
            granted: notificationsGranted,
            onRequest: onRequestNotifications,
          ),
          const SizedBox(height: 32),

          // Privacy note
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.infoContainer.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  Icons.privacy_tip_outlined,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Votre vie privée est notre priorité. La géolocalisation n\'est jamais utilisée en arrière-plan. Vous pouvez modifier ces autorisations à tout moment.',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface,
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PermissionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final bool granted;
  final VoidCallback onRequest;

  const _PermissionCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.granted,
    required this.onRequest,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: granted
                        ? AppColors.successContainer
                        : theme.colorScheme.surfaceContainerHigh,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    icon,
                    color: granted
                        ? AppColors.success
                        : theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    title,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                if (granted)
                  const Icon(Icons.check_circle, color: AppColors.success, size: 24),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              description,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                height: 1.4,
              ),
            ),
            if (!granted) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: onRequest,
                  child: const Text('Autoriser'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
