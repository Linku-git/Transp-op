import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../models/notification_item.dart';
import '../../providers/notification_provider.dart';
import '../../widgets/empty_state.dart';

class NotificationListScreen extends ConsumerWidget {
  const NotificationListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(notificationProvider);
    final notifier = ref.read(notificationProvider.notifier);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          if (state.unreadCount > 0)
            TextButton(
              onPressed: () => notifier.markAllAsRead(),
              child: const Text('Tout lire'),
            ),
        ],
      ),
      body: state.notifications.isEmpty
          ? const EmptyState(
              title: 'Aucune notification',
              subtitle: 'Vous recevrez des alertes transport ici',
              icon: Icons.notifications_none,
            )
          : ListView(
              children: state.groupedByDate.entries.map((entry) {
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Date header
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                      child: Text(
                        _formatDateKey(entry.key),
                        style: theme.textTheme.labelSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.5,
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                    ...entry.value.map((item) => Dismissible(
                          key: Key(item.id),
                          direction: DismissDirection.endToStart,
                          onDismissed: (_) => notifier.dismiss(item.id),
                          background: Container(
                            alignment: Alignment.centerRight,
                            padding: const EdgeInsets.only(right: 20),
                            color: theme.colorScheme.error,
                            child: const Icon(Icons.delete, color: Colors.white),
                          ),
                          child: _NotificationTile(
                            item: item,
                            onTap: () {
                              notifier.markAsRead(item.id);
                              final route = item.targetRoute;
                              if (route != null) {
                                context.push(route);
                              }
                            },
                          ),
                        )),
                  ],
                );
              }).toList(),
            ),
    );
  }

  String _formatDateKey(String key) {
    final now = DateTime.now();
    final date = DateTime.parse(key);
    final today =
        '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
    final yesterday = DateTime(now.year, now.month, now.day - 1);
    final yesterdayKey =
        '${yesterday.year}-${yesterday.month.toString().padLeft(2, '0')}-${yesterday.day.toString().padLeft(2, '0')}';

    if (key == today) return 'Aujourd\'hui';
    if (key == yesterdayKey) return 'Hier';
    return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
  }
}

class _NotificationTile extends StatelessWidget {
  final NotificationItem item;
  final VoidCallback onTap;

  const _NotificationTile({required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: _typeColor(item.type).withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(
          _typeIcon(item.type),
          size: 20,
          color: _typeColor(item.type),
        ),
      ),
      title: Text(
        item.title,
        style: theme.textTheme.titleSmall?.copyWith(
          fontWeight: item.isRead ? FontWeight.w400 : FontWeight.w600,
        ),
      ),
      subtitle: Text(
        item.body,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            '${item.receivedAt.hour.toString().padLeft(2, '0')}:${item.receivedAt.minute.toString().padLeft(2, '0')}',
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.outline,
            ),
          ),
          if (!item.isRead) ...[
            const SizedBox(height: 4),
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: theme.colorScheme.primary,
                shape: BoxShape.circle,
              ),
            ),
          ],
        ],
      ),
      onTap: onTap,
    );
  }

  IconData _typeIcon(NotificationType type) => switch (type) {
        NotificationType.rtiAlert => Icons.directions_bus,
        NotificationType.routeChange => Icons.map,
        NotificationType.weather => Icons.cloud,
        NotificationType.content => Icons.article,
        NotificationType.emergency => Icons.shield,
      };

  Color _typeColor(NotificationType type) => switch (type) {
        NotificationType.rtiAlert => Colors.blue,
        NotificationType.routeChange => Colors.orange,
        NotificationType.weather => Colors.cyan,
        NotificationType.content => Colors.purple,
        NotificationType.emergency => Colors.red,
      };
}
