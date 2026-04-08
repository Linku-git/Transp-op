import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';
import '../../providers/profile_provider.dart';
import '../../widgets/profile_header.dart';
import '../../widgets/quick_stats_row.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/error_widget.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(profileProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Profil')),
      body: state.isLoading
          ? const LoadingIndicator()
          : state.profile == null
              ? AppErrorWidget(
                  message: state.error ?? 'Impossible de charger le profil',
                  onRetry: () => ref.read(profileProvider.notifier).load(),
                )
              : RefreshIndicator(
                  onRefresh: () => ref.read(profileProvider.notifier).load(),
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      ProfileHeader(profile: state.profile!),
                      const SizedBox(height: 20),
                      QuickStatsRow(stats: state.profile!.stats),
                      const SizedBox(height: 24),

                      // Menu items
                      _MenuItem(
                        icon: Icons.edit,
                        label: 'Modifier le profil',
                        onTap: () => context.push('/profile/edit'),
                      ),
                      _MenuItem(
                        icon: Icons.tune,
                        label: 'Préférences de transport',
                        onTap: () => context.push('/profile/preferences'),
                      ),
                      _MenuItem(
                        icon: Icons.shield_outlined,
                        label: 'Questionnaire sécurité',
                        onTap: () => context.push('/profile/security'),
                      ),
                      _MenuItem(
                        icon: Icons.notifications_outlined,
                        label: 'Notifications',
                        onTap: () => context.push('/notifications'),
                      ),
                      _MenuItem(
                        icon: Icons.language,
                        label: 'Langue',
                        trailing: Text('Français', style: theme.textTheme.bodySmall),
                        onTap: () {},
                      ),
                      _MenuItem(
                        icon: Icons.dark_mode_outlined,
                        label: 'Mode nuit',
                        trailing: const Text('Auto'),
                        onTap: () {},
                      ),
                      _MenuItem(
                        icon: Icons.info_outline,
                        label: 'À propos',
                        onTap: () {},
                      ),
                      const SizedBox(height: 8),
                      _MenuItem(
                        icon: Icons.logout,
                        label: 'Déconnexion',
                        isDestructive: true,
                        onTap: () => _handleLogout(context, ref),
                      ),
                    ],
                  ),
                ),
    );
  }

  void _handleLogout(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Déconnexion'),
        content: const Text('Voulez-vous vraiment vous déconnecter ?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Annuler'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(ctx).pop();
              await ref.read(authProvider.notifier).logout();
              if (context.mounted) context.go('/login');
            },
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Déconnexion'),
          ),
        ],
      ),
    );
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final Widget? trailing;
  final VoidCallback onTap;
  final bool isDestructive;

  const _MenuItem({
    required this.icon,
    required this.label,
    this.trailing,
    required this.onTap,
    this.isDestructive = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = isDestructive
        ? theme.colorScheme.error
        : theme.colorScheme.onSurface;

    return Card(
      margin: const EdgeInsets.only(bottom: 4),
      child: ListTile(
        leading: Icon(icon, color: color, size: 22),
        title: Text(
          label,
          style: theme.textTheme.bodyMedium?.copyWith(color: color),
        ),
        trailing: trailing ?? Icon(
          Icons.chevron_right,
          color: theme.colorScheme.outline,
          size: 20,
        ),
        onTap: onTap,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );
  }
}
