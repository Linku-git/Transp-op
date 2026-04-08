import 'package:flutter/material.dart';
import '../config/colors.dart';

class Co2Badge extends StatelessWidget {
  final double co2SavedKg;

  const Co2Badge({super.key, required this.co2SavedKg});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.successContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.eco, size: 20, color: AppColors.success),
          const SizedBox(width: 6),
          Text(
            '${co2SavedKg.toStringAsFixed(1)} kg CO2',
            style: theme.textTheme.labelLarge?.copyWith(
              color: AppColors.success,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            'économisés',
            style: theme.textTheme.bodySmall?.copyWith(
              color: AppColors.success,
            ),
          ),
        ],
      ),
    );
  }
}
