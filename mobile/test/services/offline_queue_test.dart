import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/services/offline_queue.dart';

void main() {
  group('QueuedAction', () {
    test('toJson produces correct map', () {
      final action = QueuedAction(
        id: 'q-1',
        method: 'POST',
        path: '/mobile/trips/book',
        data: {'route_id': '123'},
        priority: QueuePriority.high,
      );
      final json = action.toJson();

      expect(json['id'], 'q-1');
      expect(json['method'], 'POST');
      expect(json['path'], '/mobile/trips/book');
      expect(json['priority'], QueuePriority.high.index);
      expect(json['retries'], 0);
    });

    test('fromJson parses correctly', () {
      final action = QueuedAction.fromJson({
        'id': 'q-2',
        'method': 'DELETE',
        'path': '/mobile/trips/abc',
        'priority': 1,
        'created_at': '2026-04-08T10:00:00.000',
        'retries': 2,
      });

      expect(action.id, 'q-2');
      expect(action.method, 'DELETE');
      expect(action.priority, QueuePriority.high);
      expect(action.retries, 2);
    });

    test('roundtrip serialization', () {
      final original = QueuedAction(
        id: 'q-3',
        method: 'PUT',
        path: '/test',
        data: {'key': 'value'},
        priority: QueuePriority.critical,
      );
      final restored = QueuedAction.fromJson(original.toJson());

      expect(restored.id, original.id);
      expect(restored.method, original.method);
      expect(restored.priority, original.priority);
    });
  });

  group('QueuePriority', () {
    test('critical is lowest index (highest priority)', () {
      expect(QueuePriority.critical.index, 0);
      expect(QueuePriority.high.index, 1);
      expect(QueuePriority.medium.index, 2);
      expect(QueuePriority.low.index, 3);
    });
  });
}
