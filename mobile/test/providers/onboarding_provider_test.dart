import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/providers/onboarding_provider.dart';

void main() {
  group('OnboardingState', () {
    test('initial state is step 0', () {
      final state = OnboardingState();
      expect(state.currentStep, 0);
      expect(state.canGoBack, false);
      expect(state.canGoForward, true);
      expect(state.isLastStep, false);
      expect(state.isSubmitting, false);
      expect(state.error, isNull);
    });

    test('totalSteps is 4', () {
      expect(OnboardingState.totalSteps, 4);
    });

    test('isLastStep on step 3', () {
      final state = OnboardingState(currentStep: 3);
      expect(state.isLastStep, true);
      expect(state.canGoForward, false);
      expect(state.canGoBack, true);
    });

    test('canGoBack on step 1', () {
      final state = OnboardingState(currentStep: 1);
      expect(state.canGoBack, true);
      expect(state.canGoForward, true);
    });

    test('copyWith preserves values', () {
      final state = OnboardingState(
        currentStep: 2,
        locationGranted: true,
      );
      final updated = state.copyWith(notificationsGranted: true);

      expect(updated.currentStep, 2);
      expect(updated.locationGranted, true);
      expect(updated.notificationsGranted, true);
    });
  });
}
