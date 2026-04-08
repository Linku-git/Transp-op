import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/services/connectivity_service.dart';

void main() {
  group('ConnectivityState', () {
    test('all states exist', () {
      expect(ConnectivityState.values.length, 3);
      expect(ConnectivityState.values, contains(ConnectivityState.online));
      expect(ConnectivityState.values, contains(ConnectivityState.offline));
      expect(ConnectivityState.values, contains(ConnectivityState.degraded));
    });

    test('online and offline are distinct', () {
      expect(ConnectivityState.online, isNot(ConnectivityState.offline));
    });
  });
}
