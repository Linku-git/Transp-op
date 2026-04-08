import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/main.dart';
import 'package:transpop_mobile/providers/auth_provider.dart';
import 'package:transpop_mobile/services/api_client.dart';
import 'package:transpop_mobile/services/auth_service.dart';

void main() {
  testWidgets('App launches and renders splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authProvider.overrideWith((ref) => _NoOpAuthNotifier()),
        ],
        child: const TranspopApp(),
      ),
    );

    expect(find.text('Transpop'), findsAtLeast(1));
  });

  testWidgets('App renders with Material theme', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authProvider.overrideWith((ref) => _NoOpAuthNotifier()),
        ],
        child: const TranspopApp(),
      ),
    );

    expect(find.byType(MaterialApp), findsOneWidget);
  });
}

class _NoOpAuthNotifier extends AuthNotifier {
  _NoOpAuthNotifier() : super(AuthService(apiClient: ApiClient()));

  @override
  Future<void> checkSession() async {}
}
