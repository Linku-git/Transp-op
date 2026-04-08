import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/transport_preferences.dart';
import '../models/security_preferences.dart';
import '../services/onboarding_service.dart';
import '../utils/api_error.dart';
import 'auth_provider.dart';

final onboardingServiceProvider = Provider<OnboardingService>((ref) {
  return OnboardingService(apiClient: ref.watch(apiClientProvider));
});

class OnboardingState {
  final int currentStep;
  final TransportPreferences transport;
  final SecurityPreferences security;
  final bool locationGranted;
  final bool notificationsGranted;
  final bool isSubmitting;
  final String? error;

  OnboardingState({
    this.currentStep = 0,
    TransportPreferences? transport,
    SecurityPreferences? security,
    this.locationGranted = false,
    this.notificationsGranted = false,
    this.isSubmitting = false,
    this.error,
  })  : transport = transport ?? TransportPreferences(),
        security = security ?? SecurityPreferences();

  static const int totalSteps = 4;

  bool get canGoBack => currentStep > 0;
  bool get canGoForward => currentStep < totalSteps - 1;
  bool get isLastStep => currentStep == totalSteps - 1;

  OnboardingState copyWith({
    int? currentStep,
    TransportPreferences? transport,
    SecurityPreferences? security,
    bool? locationGranted,
    bool? notificationsGranted,
    bool? isSubmitting,
    String? error,
  }) {
    return OnboardingState(
      currentStep: currentStep ?? this.currentStep,
      transport: transport ?? this.transport,
      security: security ?? this.security,
      locationGranted: locationGranted ?? this.locationGranted,
      notificationsGranted: notificationsGranted ?? this.notificationsGranted,
      isSubmitting: isSubmitting ?? this.isSubmitting,
      error: error,
    );
  }
}

class OnboardingNotifier extends StateNotifier<OnboardingState> {
  final OnboardingService _service;

  OnboardingNotifier(this._service) : super(OnboardingState());

  void nextStep() {
    if (state.canGoForward) {
      state = state.copyWith(currentStep: state.currentStep + 1);
    }
  }

  void previousStep() {
    if (state.canGoBack) {
      state = state.copyWith(currentStep: state.currentStep - 1);
    }
  }

  void goToStep(int step) {
    if (step >= 0 && step < OnboardingState.totalSteps) {
      state = state.copyWith(currentStep: step);
    }
  }

  void updateTransport(TransportPreferences transport) {
    state = state.copyWith(transport: transport);
  }

  void updateSecurity(SecurityPreferences security) {
    state = state.copyWith(security: security);
  }

  void setLocationGranted(bool granted) {
    state = state.copyWith(locationGranted: granted);
  }

  void setNotificationsGranted(bool granted) {
    state = state.copyWith(notificationsGranted: granted);
  }

  Future<bool> submit() async {
    state = state.copyWith(isSubmitting: true, error: null);
    try {
      await _service.savePreferences(
        transport: state.transport,
        security: state.security,
      );
      state = state.copyWith(isSubmitting: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isSubmitting: false,
        error: extractApiError(e, 'Erreur lors de la sauvegarde'),
      );
      return false;
    }
  }
}

final onboardingProvider =
    StateNotifierProvider<OnboardingNotifier, OnboardingState>((ref) {
  return OnboardingNotifier(ref.watch(onboardingServiceProvider));
});
