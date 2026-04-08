import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/screens/auth/login_screen.dart';

void main() {
  Widget createTestWidget() {
    return const ProviderScope(
      child: MaterialApp(
        home: LoginScreen(),
      ),
    );
  }

  group('LoginScreen', () {
    testWidgets('renders logo and title', (tester) async {
      await tester.pumpWidget(createTestWidget());

      expect(find.text('Transpop'), findsOneWidget);
      expect(find.text('Plateforme Mobilité RH'), findsOneWidget);
    });

    testWidgets('renders email and password fields', (tester) async {
      await tester.pumpWidget(createTestWidget());

      expect(find.text('Adresse e-mail'), findsOneWidget);
      expect(find.text('Mot de passe'), findsOneWidget);
    });

    testWidgets('renders login button', (tester) async {
      await tester.pumpWidget(createTestWidget());

      expect(find.text('Se connecter'), findsOneWidget);
    });

    testWidgets('validates empty email', (tester) async {
      await tester.pumpWidget(createTestWidget());

      await tester.tap(find.text('Se connecter'));
      await tester.pumpAndSettle();

      expect(find.text('Veuillez saisir votre e-mail'), findsOneWidget);
    });

    testWidgets('validates empty password', (tester) async {
      await tester.pumpWidget(createTestWidget());

      // Enter email but not password
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Adresse e-mail'),
        'test@test.com',
      );
      await tester.tap(find.text('Se connecter'));
      await tester.pumpAndSettle();

      expect(find.text('Veuillez saisir votre mot de passe'), findsOneWidget);
    });

    testWidgets('validates invalid email format', (tester) async {
      await tester.pumpWidget(createTestWidget());

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Adresse e-mail'),
        'notanemail',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Mot de passe'),
        'password123',
      );
      await tester.tap(find.text('Se connecter'));
      await tester.pumpAndSettle();

      expect(find.text('Adresse e-mail invalide'), findsOneWidget);
    });

    testWidgets('toggles password visibility', (tester) async {
      await tester.pumpWidget(createTestWidget());

      // Initially password is obscured
      expect(find.byIcon(Icons.visibility_outlined), findsOneWidget);

      await tester.tap(find.byIcon(Icons.visibility_outlined));
      await tester.pump();

      expect(find.byIcon(Icons.visibility_off_outlined), findsOneWidget);
    });
  });
}
