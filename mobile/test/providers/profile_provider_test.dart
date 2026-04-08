import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/providers/profile_provider.dart';

void main() {
  group('ProfileState', () {
    test('initial state', () {
      const state = ProfileState();
      expect(state.profile, isNull);
      expect(state.isLoading, false);
      expect(state.isSaving, false);
      expect(state.error, isNull);
    });

    test('copyWith preserves values', () {
      const state = ProfileState(isLoading: true);
      final updated = state.copyWith(error: 'Test');
      expect(updated.isLoading, true);
      expect(updated.error, 'Test');
    });

    test('copyWith clearMessages clears error and success', () {
      const state = ProfileState(error: 'err', saveSuccess: 'ok');
      final updated = state.copyWith(clearMessages: true);
      expect(updated.error, isNull);
      expect(updated.saveSuccess, isNull);
    });
  });
}
