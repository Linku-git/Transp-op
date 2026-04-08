import 'package:flutter/material.dart';
import '../config/colors.dart';
import '../services/statistics_service.dart';
import '../utils/co2_calculator.dart';

class ShareImpactCard extends StatelessWidget {
  final StatisticsData data;
  final VoidCallback? onShare;

  const ShareImpactCard({super.key, required this.data, this.onShare});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final trees = Co2Calculator.treesEquivalent(data.co2SavedKg);

    return Card(
      color: AppColors.primary,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const Icon(Icons.eco, size: 40, color: Colors.white),
            const SizedBox(height: 12),
            Text(
              'Mon impact positif',
              style: theme.textTheme.titleMedium?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _ImpactStat(
                  value: '${data.totalTrips}',
                  label: 'Trajets',
                ),
                _ImpactStat(
                  value: Co2Calculator.formatCo2(data.co2SavedKg),
                  label: 'CO2 éco.',
                ),
                _ImpactStat(
                  value: '$trees',
                  label: 'Arbres eq.',
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Transpop - Mobilité durable',
              style: theme.textTheme.bodySmall?.copyWith(
                color: Colors.white.withValues(alpha: 0.7),
              ),
            ),
            if (onShare != null) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: onShare,
                  icon: const Icon(Icons.share, size: 18),
                  label: const Text('Partager mon impact'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: AppColors.primary,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ImpactStat extends StatelessWidget {
  final String value;
  final String label;

  const _ImpactStat({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.white.withValues(alpha: 0.8),
          ),
        ),
      ],
    );
  }
}
