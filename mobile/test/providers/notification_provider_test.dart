import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/notification_item.dart';
import 'package:transpop_mobile/providers/notification_provider.dart';

void main() {
  group('NotificationState', () {
    test('initial state is empty', () {
      const state = NotificationState();
      expect(state.notifications, isEmpty);
      expect(state.unreadCount, 0);
      expect(state.isLoading, false);
    });

    test('groupedByDate groups correctly', () {
      final state = NotificationState(
        notifications: [
          NotificationItem(
            id: '1', type: NotificationType.content, title: 'A', body: '',
            receivedAt: DateTime(2026, 4, 8, 10, 0),
          ),
          NotificationItem(
            id: '2', type: NotificationType.rtiAlert, title: 'B', body: '',
            receivedAt: DateTime(2026, 4, 8, 8, 0),
          ),
          NotificationItem(
            id: '3', type: NotificationType.weather, title: 'C', body: '',
            receivedAt: DateTime(2026, 4, 7, 15, 0),
          ),
        ],
      );

      final grouped = state.groupedByDate;
      expect(grouped.keys, contains('2026-04-08'));
      expect(grouped.keys, contains('2026-04-07'));
      expect(grouped['2026-04-08']!.length, 2);
      expect(grouped['2026-04-07']!.length, 1);
    });

    test('copyWith preserves values', () {
      const state = NotificationState(unreadCount: 3);
      final updated = state.copyWith(isLoading: true);
      expect(updated.unreadCount, 3);
      expect(updated.isLoading, true);
    });
  });
}
