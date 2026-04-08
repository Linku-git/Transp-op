import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/notification_item.dart';

void main() {
  group('NotificationType', () {
    test('fromString parses all types', () {
      expect(NotificationType.fromString('rti_alert'), NotificationType.rtiAlert);
      expect(NotificationType.fromString('route_change'), NotificationType.routeChange);
      expect(NotificationType.fromString('weather'), NotificationType.weather);
      expect(NotificationType.fromString('content'), NotificationType.content);
      expect(NotificationType.fromString('emergency'), NotificationType.emergency);
    });

    test('fromString defaults to content', () {
      expect(NotificationType.fromString('unknown'), NotificationType.content);
    });

    test('labels are in French', () {
      expect(NotificationType.rtiAlert.label, 'Transport');
      expect(NotificationType.emergency.label, 'Urgence');
    });

    test('targetRoute maps correctly', () {
      expect(NotificationType.rtiAlert.targetRoute, '/tracking');
      expect(NotificationType.routeChange.targetRoute, '/trips');
      expect(NotificationType.content.targetRoute, '/content');
      expect(NotificationType.emergency.targetRoute, '/emergency');
    });
  });

  group('NotificationItem', () {
    test('fromJson parses correctly', () {
      final item = NotificationItem.fromJson({
        'id': 'n-1',
        'type': 'rti_alert',
        'title': 'Véhicule en approche',
        'body': 'Arrivée dans 2 minutes',
        'received_at': '2026-04-08T08:28:00',
        'is_read': false,
      });

      expect(item.id, 'n-1');
      expect(item.type, NotificationType.rtiAlert);
      expect(item.title, 'Véhicule en approche');
      expect(item.isRead, false);
    });

    test('fromFCM parses message', () {
      final item = NotificationItem.fromFCM({
        'notification': {
          'title': 'Changement de route',
          'body': 'Votre itinéraire a été modifié',
        },
        'data': {
          'type': 'route_change',
          'notification_id': 'fcm-1',
        },
      });

      expect(item.type, NotificationType.routeChange);
      expect(item.title, 'Changement de route');
      expect(item.id, 'fcm-1');
    });

    test('targetRoute includes content_id for content type', () {
      final item = NotificationItem(
        id: '1',
        type: NotificationType.content,
        title: 'Test',
        body: '',
        receivedAt: DateTime.now(),
        data: {'content_id': 'c-123'},
      );

      expect(item.targetRoute, '/content/c-123');
    });

    test('targetRoute falls back to type default', () {
      final item = NotificationItem(
        id: '1',
        type: NotificationType.weather,
        title: 'Test',
        body: '',
        receivedAt: DateTime.now(),
      );

      expect(item.targetRoute, '/home');
    });

    test('copyWith updates isRead', () {
      final item = NotificationItem(
        id: '1',
        type: NotificationType.content,
        title: 'Test',
        body: '',
        receivedAt: DateTime.now(),
      );

      expect(item.isRead, false);
      final read = item.copyWith(isRead: true);
      expect(read.isRead, true);
      expect(read.id, '1');
    });
  });
}
