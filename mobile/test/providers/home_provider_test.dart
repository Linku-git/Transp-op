import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/providers/home_provider.dart';

void main() {
  group('HomeState', () {
    test('initial state has no departure', () {
      const state = HomeState();
      expect(state.nextDeparture, isNull);
      expect(state.contentItems, isEmpty);
      expect(state.unreadNotifications, 0);
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('copyWith updates fields', () {
      const state = HomeState(unreadNotifications: 5);
      final updated = state.copyWith(isLoading: true);
      expect(updated.isLoading, true);
      expect(updated.unreadNotifications, 5);
    });

    test('copyWith can clear departure', () {
      const state = HomeState();
      final updated = state.copyWith(clearDeparture: true);
      expect(updated.nextDeparture, isNull);
    });
  });
}
