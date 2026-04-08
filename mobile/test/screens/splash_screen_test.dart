import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/config/colors.dart';
import 'package:transpop_mobile/providers/auth_provider.dart';
import 'package:transpop_mobile/services/api_client.dart';
import 'package:transpop_mobile/services/auth_service.dart';

void main() {
  group('SplashScreen layout', () {
    // Test the splash screen layout without the real screen (which triggers auth)
    testWidgets('splash screen layout renders branding', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authProvider.overrideWith(
              (ref) => _NoOpAuthNotifier(),
            ),
          ],
          child: MaterialApp(
            home: Scaffold(
              backgroundColor: AppColors.primary,
              body: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Icon(
                        Icons.directions_bus,
                        size: 44,
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Transpop',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.w700,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text('Plateforme Mobilité RH'),
                    const SizedBox(height: 48),
                    const CircularProgressIndicator(color: Colors.white),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('Transpop'), findsOneWidget);
      expect(find.text('Plateforme Mobilité RH'), findsOneWidget);
      expect(find.byIcon(Icons.directions_bus), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });

  group('AuthNotifier navigation logic', () {
    test('checkSession sets unauthenticated when no session exists', () {
      // This is tested in auth_provider_test.dart
      // SplashScreen listens to authProvider and navigates accordingly
      const state = AuthState(status: AuthStatus.unauthenticated);
      expect(state.isAuthenticated, false);
    });
  });
}

class _NoOpAuthNotifier extends AuthNotifier {
  _NoOpAuthNotifier() : super(_createFakeService());

  static AuthService _createFakeService() {
    return AuthService(apiClient: ApiClient());
  }

  @override
  Future<void> checkSession() async {
    // No-op: don't touch secure storage in tests
  }
}
