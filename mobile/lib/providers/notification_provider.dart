import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/notification_item.dart';
import '../services/push_notification_service.dart';
import 'auth_provider.dart';

final pushNotificationServiceProvider = Provider<PushNotificationService>((ref) {
  final service = PushNotificationService(apiClient: ref.watch(apiClientProvider));
  ref.onDispose(() => service.dispose());
  return service;
});

class NotificationState {
  final List<NotificationItem> notifications;
  final int unreadCount;
  final bool isLoading;

  const NotificationState({
    this.notifications = const [],
    this.unreadCount = 0,
    this.isLoading = false,
  });

  Map<String, List<NotificationItem>> get groupedByDate {
    final grouped = <String, List<NotificationItem>>{};
    for (final n in notifications) {
      final key =
          '${n.receivedAt.year}-${n.receivedAt.month.toString().padLeft(2, '0')}-${n.receivedAt.day.toString().padLeft(2, '0')}';
      grouped.putIfAbsent(key, () => []).add(n);
    }
    return grouped;
  }

  NotificationState copyWith({
    List<NotificationItem>? notifications,
    int? unreadCount,
    bool? isLoading,
  }) {
    return NotificationState(
      notifications: notifications ?? this.notifications,
      unreadCount: unreadCount ?? this.unreadCount,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class NotificationNotifier extends StateNotifier<NotificationState> {
  final PushNotificationService _service;
  StreamSubscription<NotificationItem>? _sub;

  NotificationNotifier(this._service) : super(const NotificationState()) {
    _sub = _service.notificationStream.listen(_onNotification);
  }

  void _onNotification(NotificationItem item) {
    state = state.copyWith(
      notifications: [item, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    );
  }

  void markAsRead(String notificationId) {
    final updated = state.notifications.map((n) {
      if (n.id == notificationId && !n.isRead) {
        return n.copyWith(isRead: true);
      }
      return n;
    }).toList();

    final unread = updated.where((n) => !n.isRead).length;
    state = state.copyWith(notifications: updated, unreadCount: unread);
  }

  void markAllAsRead() {
    final updated = state.notifications.map((n) => n.copyWith(isRead: true)).toList();
    state = state.copyWith(notifications: updated, unreadCount: 0);
  }

  void dismiss(String notificationId) {
    final updated = state.notifications.where((n) => n.id != notificationId).toList();
    final unread = updated.where((n) => !n.isRead).length;
    state = state.copyWith(notifications: updated, unreadCount: unread);
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }
}

final notificationProvider =
    StateNotifierProvider<NotificationNotifier, NotificationState>((ref) {
  return NotificationNotifier(ref.watch(pushNotificationServiceProvider));
});
