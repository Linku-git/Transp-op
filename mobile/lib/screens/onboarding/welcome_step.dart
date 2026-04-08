import 'package:flutter/material.dart';
import '../../config/colors.dart';

class WelcomeStep extends StatefulWidget {
  const WelcomeStep({super.key});

  @override
  State<WelcomeStep> createState() => _WelcomeStepState();
}

class _WelcomeStepState extends State<WelcomeStep> {
  final _pageController = PageController();
  int _currentSlide = 0;

  static const _slides = [
    _SlideData(
      icon: Icons.directions_bus,
      title: 'Transport optimisé',
      description:
          'Des trajets intelligents calculés pour réduire votre temps de transport et votre empreinte carbone.',
    ),
    _SlideData(
      icon: Icons.access_time,
      title: 'Suivi en temps réel',
      description:
          'Suivez votre véhicule en direct et recevez des alertes avant son arrivée à votre point de ramassage.',
    ),
    _SlideData(
      icon: Icons.eco,
      title: 'Impact positif',
      description:
          'Visualisez vos économies de CO2 et contribuez à la mobilité durable de votre entreprise.',
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Expanded(
          child: PageView.builder(
            controller: _pageController,
            onPageChanged: (index) => setState(() => _currentSlide = index),
            itemCount: _slides.length,
            itemBuilder: (context, index) {
              final slide = _slides[index];
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 96,
                      height: 96,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [AppColors.primary, AppColors.primaryContainer],
                        ),
                        borderRadius: BorderRadius.circular(24),
                      ),
                      child: Icon(slide.icon, size: 48, color: Colors.white),
                    ),
                    const SizedBox(height: 32),
                    Text(
                      slide.title,
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: theme.colorScheme.onSurface,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      slide.description,
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                        height: 1.5,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              );
            },
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(_slides.length, (index) {
              return AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                width: _currentSlide == index ? 24 : 8,
                height: 8,
                decoration: BoxDecoration(
                  color: _currentSlide == index
                      ? theme.colorScheme.primary
                      : theme.colorScheme.outlineVariant,
                  borderRadius: BorderRadius.circular(4),
                ),
              );
            }),
          ),
        ),
      ],
    );
  }
}

class _SlideData {
  final IconData icon;
  final String title;
  final String description;

  const _SlideData({
    required this.icon,
    required this.title,
    required this.description,
  });
}
