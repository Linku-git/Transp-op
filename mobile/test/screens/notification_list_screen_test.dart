import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/screens/notifications/notification_list_screen.dart';
import 'package:transpop_mobile/providers/notification_provider.dart';
import 'package:transpop_mobile/models/notification_item.dart';

void main() {
  group('NotificationListScreen', () {
    testWidgets('shows empty state when no notifications', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            notificationProvider.overrideWith(
              (ref) => _StubNotificationNotifier(),
            ),
          ],
          child: const MaterialApp(
            home: NotificationListScreen(),
          ),
        ),
      );

      expect(find.text('Notifications'), findsOneWidget);
      expect(find.text('Aucune notification'), findsOneWidget);
    });

    testWidgets('renders notification title', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            notificationProvider.overrideWith(
              (ref) => _StubNotificationNotifier(items: [
                NotificationItem(
                  id: '1',
                  type: NotificationType.rtiAlert,
                  title: 'Véhicule en approche',
                  body: 'Arrivée dans 2 minutes',
                  receivedAt: DateTime.now(),
                ),
              ]),
            ),
          ],
          child: const MaterialApp(
            home: NotificationListScreen(),
          ),
        ),
      );

      expect(find.text('Véhicule en approche'), findsOneWidget);
      expect(find.text('Arrivée dans 2 minutes'), findsOneWidget);
    });

    testWidgets('shows Tout lire button when unread exist', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            notificationProvider.overrideWith(
              (ref) => _StubNotificationNotifier(
                items: [
                  NotificationItem(
                    id: '1',
                    type: NotificationType.content,
                    title: 'Test',
                    body: 'Body',
                    receivedAt: DateTime.now(),
                  ),
                ],
                unread: 1,
              ),
            ),
          ],
          child: const MaterialApp(
            home: NotificationListScreen(),
          ),
        ),
      );

      expect(find.text('Tout lire'), findsOneWidget);
    });
  });
}

/// Stub that doesn't touch Firebase at all
class _StubNotificationNotifier extends StateNotifier<NotificationState>
    implements NotificationNotifier {
  _StubNotificationNotifier({
    List<NotificationItem>? items,
    int unread = 0,
  }) : super(NotificationState(
          notifications: items ?? [],
          unreadCount: unread,
        ));

  @override
  void markAsRead(String notificationId) {
    final updated = state.notifications.map((n) {
      if (n.id == notificationId) return n.copyWith(isRead: true);
      return n;
    }).toList();
    state = state.copyWith(
      notifications: updated,
      unreadCount: updated.where((n) => !n.isRead).length,
    );
  }

  @override
  void markAllAsRead() {
    final updated = state.notifications.map((n) => n.copyWith(isRead: true)).toList();
    state = state.copyWith(notifications: updated, unreadCount: 0);
  }

  @override
  void dismiss(String notificationId) {
    final updated = state.notifications.where((n) => n.id != notificationId).toList();
    state = state.copyWith(
      notifications: updated,
      unreadCount: updated.where((n) => !n.isRead).length,
    );
  }
}
