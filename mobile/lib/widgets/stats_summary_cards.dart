import 'package:flutter/material.dart';
import '../config/colors.dart';
import '../services/statistics_service.dart';
import '../utils/co2_calculator.dart';

class StatsSummaryCards extends StatelessWidget {
  final StatisticsData data;

  const StatsSummaryCards({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _StatCard(
                icon: Icons.directions_bus,
                value: '${data.totalTrips}',
                label: 'Trajets',
                color: AppColors.primary,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _StatCard(
                icon: Icons.straighten,
                value: '${data.totalDistanceKm.toStringAsFixed(0)} km',
                label: 'Distance',
                color: AppColors.secondary,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _StatCard(
                icon: Icons.eco,
                value: Co2Calculator.formatCo2(data.co2SavedKg),
                label: 'CO2 économisé',
                color: AppColors.success,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _StatCard(
                icon: Icons.school,
                value: '${data.trainingCompleted}',
                label: 'Formations',
                color: Colors.purple,
              ),
            ),
          ],
        ),
        if (data.quizAverage > 0) ...[
          const SizedBox(height: 8),
          _StatCard(
            icon: Icons.quiz,
            value: '${data.quizAverage.toStringAsFixed(0)}%',
            label: 'Score moyen quiz',
            color: AppColors.tertiary,
          ),
        ],
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, size: 20, color: color),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    value,
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                  ),
                  Text(
                    label,
                    style: theme.textTheme.labelSmall?.copyWith(color: theme.colorScheme.onSurfaceVariant),
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
