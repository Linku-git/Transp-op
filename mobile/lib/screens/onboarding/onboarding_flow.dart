import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/onboarding_provider.dart';
import 'welcome_step.dart';
import 'transport_preferences_step.dart';
import 'security_questionnaire_step.dart';
import 'permissions_step.dart';

class OnboardingFlow extends ConsumerStatefulWidget {
  const OnboardingFlow({super.key});

  @override
  ConsumerState<OnboardingFlow> createState() => _OnboardingFlowState();
}

class _OnboardingFlowState extends ConsumerState<OnboardingFlow> {
  late final PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _animateToPage(int page) {
    _pageController.animateToPage(
      page,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  Future<void> _handleNext() async {
    final notifier = ref.read(onboardingProvider.notifier);
    final state = ref.read(onboardingProvider);

    if (state.isLastStep) {
      final success = await notifier.submit();
      if (success && mounted) {
        context.go('/home');
      }
    } else {
      notifier.nextStep();
      _animateToPage(state.currentStep + 1);
    }
  }

  void _handleBack() {
    final notifier = ref.read(onboardingProvider.notifier);
    final state = ref.read(onboardingProvider);

    if (state.canGoBack) {
      notifier.previousStep();
      _animateToPage(state.currentStep - 1);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(onboardingProvider);
    final notifier = ref.read(onboardingProvider.notifier);
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Progress indicator
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
              child: Row(
                children: List.generate(OnboardingState.totalSteps, (index) {
                  return Expanded(
                    child: Container(
                      margin: EdgeInsets.only(
                          right: index < OnboardingState.totalSteps - 1 ? 6 : 0),
                      height: 4,
                      decoration: BoxDecoration(
                        color: index <= state.currentStep
                            ? theme.colorScheme.primary
                            : theme.colorScheme.outlineVariant.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  );
                }),
              ),
            ),

            // Step label
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 4),
              child: Row(
                children: [
                  Text(
                    'Étape ${state.currentStep + 1} sur ${OnboardingState.totalSteps}',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Spacer(),
                  if (state.currentStep < OnboardingState.totalSteps - 1)
                    TextButton(
                      onPressed: () => context.go('/home'),
                      child: Text(
                        'Passer',
                        style: TextStyle(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                ],
              ),
            ),

            // Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                children: [
                  const WelcomeStep(),
                  TransportPreferencesStep(
                    preferences: state.transport,
                    onChanged: notifier.updateTransport,
                  ),
                  SecurityQuestionnaireStep(
                    preferences: state.security,
                    onChanged: notifier.updateSecurity,
                  ),
                  PermissionsStep(
                    locationGranted: state.locationGranted,
                    notificationsGranted: state.notificationsGranted,
                    onRequestLocation: () =>
                        notifier.setLocationGranted(true),
                    onRequestNotifications: () =>
                        notifier.setNotificationsGranted(true),
                  ),
                ],
              ),
            ),

            // Error banner
            if (state.error != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.errorContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    state.error!,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onErrorContainer,
                    ),
                  ),
                ),
              ),

            // Navigation buttons
            Padding(
              padding: const EdgeInsets.all(24),
              child: Row(
                children: [
                  if (state.canGoBack)
                    Expanded(
                      child: OutlinedButton(
                        onPressed: _handleBack,
                        child: const Text('Retour'),
                      ),
                    ),
                  if (state.canGoBack) const SizedBox(width: 12),
                  Expanded(
                    flex: state.canGoBack ? 2 : 1,
                    child: SizedBox(
                      height: 52,
                      child: ElevatedButton(
                        onPressed: state.isSubmitting ? null : _handleNext,
                        child: state.isSubmitting
                            ? const SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  color: Colors.white,
                                ),
                              )
                            : Text(
                                state.isLastStep ? 'Commencer' : 'Suivant',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
