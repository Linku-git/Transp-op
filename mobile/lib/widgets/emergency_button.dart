import 'package:flutter/material.dart';
import '../config/colors.dart';

class EmergencyButton extends StatelessWidget {
  final VoidCallback onPressed;

  const EmergencyButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.nightEmergency,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          elevation: 4,
          shadowColor: AppColors.nightEmergency.withValues(alpha: 0.4),
        ),
        icon: const Icon(Icons.emergency, size: 24),
        label: const Text(
          'URGENCE',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            letterSpacing: 1,
          ),
        ),
      ),
    );
  }
}
