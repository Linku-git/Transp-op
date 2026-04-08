import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/providers/auth_provider.dart';

void main() {
  group('AuthState', () {
    test('initial state is correct', () {
      const state = AuthState();
      expect(state.status, AuthStatus.initial);
      expect(state.user, isNull);
      expect(state.errorMessage, isNull);
      expect(state.isAuthenticated, false);
      expect(state.isLoading, false);
    });

    test('authenticated state', () {
      const state = AuthState(status: AuthStatus.authenticated);
      expect(state.isAuthenticated, true);
      expect(state.isLoading, false);
    });

    test('loading state', () {
      const state = AuthState(status: AuthStatus.loading);
      expect(state.isLoading, true);
      expect(state.isAuthenticated, false);
    });

    test('copyWith preserves existing values', () {
      const state = AuthState(
        status: AuthStatus.authenticated,
        errorMessage: 'test',
      );
      final copied = state.copyWith(status: AuthStatus.loading);
      expect(copied.status, AuthStatus.loading);
      expect(copied.errorMessage, isNull); // errorMessage not passed
    });
  });

  group('AuthStatus', () {
    test('all statuses exist', () {
      expect(AuthStatus.values, contains(AuthStatus.initial));
      expect(AuthStatus.values, contains(AuthStatus.loading));
      expect(AuthStatus.values, contains(AuthStatus.authenticated));
      expect(AuthStatus.values, contains(AuthStatus.unauthenticated));
      expect(AuthStatus.values, contains(AuthStatus.error));
    });
  });
}
