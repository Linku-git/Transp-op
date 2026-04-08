import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../utils/api_error.dart';

// Singleton providers for ApiClient and AuthService
final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(apiClient: ref.watch(apiClientProvider));
});

// Auth state
enum AuthStatus { initial, loading, authenticated, unauthenticated, error }

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? errorMessage;

  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.errorMessage,
  });

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? errorMessage,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      errorMessage: errorMessage,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;

  AuthNotifier(this._authService) : super(const AuthState());

  Future<void> checkSession() async {
    state = state.copyWith(status: AuthStatus.loading);

    final hasSession = await _authService.hasStoredSession();
    if (!hasSession) {
      state = const AuthState(status: AuthStatus.unauthenticated);
      return;
    }

    final refreshed = await _authService.tryRefresh();
    if (!refreshed) {
      await _authService.clearSession();
      state = const AuthState(status: AuthStatus.unauthenticated);
      return;
    }

    try {
      final user = await _authService.getProfile();
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      await _authService.clearSession();
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading, errorMessage: null);

    try {
      final user = await _authService.login(email, password);
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } catch (e) {
      state = AuthState(
        status: AuthStatus.error,
        errorMessage: extractApiError(e, 'Identifiants incorrects'),
      );
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    state = const AuthState(status: AuthStatus.unauthenticated);
  }

  Future<void> refreshProfile() async {
    try {
      final user = await _authService.getProfile();
      state = state.copyWith(user: user);
    } catch (_) {
      // Silently fail — keep current user state
    }
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authServiceProvider));
});
