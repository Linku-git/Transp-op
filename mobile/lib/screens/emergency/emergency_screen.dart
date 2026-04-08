import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class EmergencyScreen extends ConsumerStatefulWidget {
  const EmergencyScreen({super.key});

  @override
  ConsumerState<EmergencyScreen> createState() => _EmergencyScreenState();
}

class _EmergencyScreenState extends ConsumerState<EmergencyScreen> {
  bool _alertSent = false;

  @override
  void initState() {
    super.initState();
    // Haptic feedback on activation
    HapticFeedback.heavyImpact();
    _sendAlert();
  }

  Future<void> _sendAlert() async {
    // In production: POST /emergency/alert with GPS coordinates
    await Future.delayed(const Duration(seconds: 1));
    if (mounted) setState(() => _alertSent = true);
  }

  void _confirmCancel() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        title: const Text('Annuler l\'alerte ?'),
        content: const Text('Êtes-vous sûr(e) d\'être en sécurité ?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Non, garder l\'alerte'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              if (context.mounted) context.pop();
            },
            style: TextButton.styleFrom(foregroundColor: Colors.white),
            child: const Text('Oui, je suis en sécurité'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFDC2626),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.emergency,
                size: 80,
                color: Colors.white,
              ),
              const SizedBox(height: 24),
              const Text(
                'ALERTE URGENCE ACTIVÉE',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                  letterSpacing: 1,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Text(
                'Votre position est partagée en temps réel',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.white.withValues(alpha: 0.9),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // Location sharing indicator
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.gps_fixed,
                          color: Colors.white.withValues(alpha: 0.9),
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        const Text(
                          'Localisation GPS active',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                        ),
                        const Spacer(),
                        if (_alertSent)
                          const Icon(Icons.check_circle, color: Colors.white, size: 20)
                        else
                          const SizedBox(
                            width: 16, height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Envoi de l\'alerte à :',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    const SizedBox(height: 8),
                    _ResponderRow(name: 'Responsable sécurité', status: _alertSent ? 'Notifié' : 'Envoi...'),
                    _ResponderRow(name: 'Administration', status: _alertSent ? 'Notifié' : 'Envoi...'),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Call emergency services
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  onPressed: () {
                    // In production: url_launcher to dial emergency number
                  },
                  icon: const Icon(Icons.phone, size: 24),
                  label: const Text(
                    'Appeler les secours',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: const Color(0xFFDC2626),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Cancel button
              TextButton(
                onPressed: _confirmCancel,
                child: Text(
                  'Annuler l\'alerte',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.8),
                    fontSize: 14,
                    decoration: TextDecoration.underline,
                    decorationColor: Colors.white.withValues(alpha: 0.5),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ResponderRow extends StatelessWidget {
  final String name;
  final String status;

  const _ResponderRow({required this.name, required this.status});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.person, color: Colors.white70, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(name, style: const TextStyle(color: Colors.white, fontSize: 13)),
          ),
          Text(status, style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }
}
