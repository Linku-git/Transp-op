import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:transpop_mobile/screens/onboarding/onboarding_flow.dart';
import 'package:transpop_mobile/screens/onboarding/welcome_step.dart';
import 'package:transpop_mobile/screens/onboarding/transport_preferences_step.dart';
import 'package:transpop_mobile/screens/onboarding/security_questionnaire_step.dart';
import 'package:transpop_mobile/screens/onboarding/permissions_step.dart';

void main() {
  Widget createTestWidget() {
    return const ProviderScope(
      child: MaterialApp(
        home: OnboardingFlow(),
      ),
    );
  }

  group('OnboardingFlow', () {
    testWidgets('renders step 1 (Welcome) initially', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.byType(WelcomeStep), findsOneWidget);
    });

    testWidgets('shows progress indicator', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('Étape 1 sur 4'), findsOneWidget);
    });

    testWidgets('shows Suivant button', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('Suivant'), findsOneWidget);
    });

    testWidgets('shows Passer button on non-last step', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('Passer'), findsOneWidget);
    });

    testWidgets('does not show Retour on first step', (tester) async {
      await tester.pumpWidget(createTestWidget());
      expect(find.text('Retour'), findsNothing);
    });

    testWidgets('navigates to step 2 on Suivant tap', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();

      expect(find.text('Étape 2 sur 4'), findsOneWidget);
      expect(find.byType(TransportPreferencesStep), findsOneWidget);
      expect(find.text('Retour'), findsOneWidget);
    });

    testWidgets('navigates back from step 2', (tester) async {
      await tester.pumpWidget(createTestWidget());

      // Go to step 2
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();
      expect(find.text('Étape 2 sur 4'), findsOneWidget);

      // Go back
      await tester.tap(find.text('Retour'));
      await tester.pumpAndSettle();
      expect(find.text('Étape 1 sur 4'), findsOneWidget);
    });

    testWidgets('navigates through all 4 steps', (tester) async {
      await tester.pumpWidget(createTestWidget());

      // Step 1 -> 2
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();
      expect(find.byType(TransportPreferencesStep), findsOneWidget);

      // Step 2 -> 3
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();
      expect(find.byType(SecurityQuestionnaireStep), findsOneWidget);

      // Step 3 -> 4
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();
      expect(find.byType(PermissionsStep), findsOneWidget);
      expect(find.text('Commencer'), findsOneWidget);
    });
  });

  group('WelcomeStep', () {
    testWidgets('renders 3 carousel slides', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: Scaffold(body: WelcomeStep())),
      );

      expect(find.text('Transport optimisé'), findsOneWidget);
      expect(find.byType(PageView), findsOneWidget);
    });
  });

  group('TransportPreferencesStep', () {
    testWidgets('renders transport mode chips', (tester) async {
      await tester.pumpWidget(createTestWidget());
      // Navigate to step 2
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();

      expect(find.text('Voiture'), findsOneWidget);
      expect(find.text('Transport en commun'), findsOneWidget);
      expect(find.text('Covoiturage'), findsOneWidget);
    });

    testWidgets('renders walking distance slider', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();

      expect(find.text('DISTANCE DE MARCHE MAXIMALE'), findsOneWidget);
      expect(find.byType(Slider), findsOneWidget);
    });

    testWidgets('renders switch toggles', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();

      expect(find.text('Transport entreprise'), findsOneWidget);
      expect(find.text('Véhicule personnel'), findsOneWidget);
    });
  });

  group('SecurityQuestionnaireStep', () {
    testWidgets('renders safety rating stars', (tester) async {
      await tester.pumpWidget(createTestWidget());
      // Navigate to step 3
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();

      expect(find.text('Questionnaire sécurité'), findsOneWidget);
      expect(find.byIcon(Icons.star_rounded), findsWidgets);
    });

    testWidgets('renders time slot chips', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Suivant'));
      await tester.pumpAndSettle();

      expect(find.text('22h - 05h'), findsOneWidget);
      expect(find.text('05h - 07h'), findsOneWidget);
    });
  });

  group('PermissionsStep', () {
    testWidgets('renders permission cards', (tester) async {
      await tester.pumpWidget(createTestWidget());
      // Navigate to step 4
      for (var i = 0; i < 3; i++) {
        await tester.tap(find.text('Suivant'));
        await tester.pumpAndSettle();
      }

      expect(find.text('Autorisations'), findsOneWidget);
      expect(find.text('Localisation'), findsOneWidget);
      expect(find.text('Notifications'), findsOneWidget);
      expect(find.text('Autoriser'), findsNWidgets(2));
    });

    testWidgets('shows privacy note', (tester) async {
      await tester.pumpWidget(createTestWidget());
      for (var i = 0; i < 3; i++) {
        await tester.tap(find.text('Suivant'));
        await tester.pumpAndSettle();
      }

      expect(find.byIcon(Icons.privacy_tip_outlined), findsOneWidget);
    });
  });
}
