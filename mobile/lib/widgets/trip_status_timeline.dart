import 'package:flutter/material.dart';
import '../models/trip.dart';

class TripStatusTimeline extends StatelessWidget {
  final TripStatus currentStatus;

  const TripStatusTimeline({super.key, required this.currentStatus});

  static const _steps = [
    TripStatus.booked,
    TripStatus.confirmed,
    TripStatus.inProgress,
    TripStatus.completed,
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final currentIndex = currentStatus == TripStatus.cancelled
        ? -1
        : _steps.indexOf(currentStatus);

    return Row(
      children: List.generate(_steps.length * 2 - 1, (index) {
        if (index.isOdd) {
          final stepIndex = index ~/ 2;
          final isCompleted = stepIndex < currentIndex;
          return Expanded(
            child: Container(
              height: 2,
              color: isCompleted
                  ? theme.colorScheme.primary
                  : theme.colorScheme.outlineVariant,
            ),
          );
        }

        final stepIndex = index ~/ 2;
        final step = _steps[stepIndex];
        final isCompleted = stepIndex <= currentIndex;
        final isCurrent = stepIndex == currentIndex;

        return Column(
          children: [
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: isCompleted
                    ? theme.colorScheme.primary
                    : theme.colorScheme.surfaceContainerHigh,
                shape: BoxShape.circle,
                border: isCurrent
                    ? Border.all(color: theme.colorScheme.primary, width: 2)
                    : null,
              ),
              child: Icon(
                isCompleted ? Icons.check : _iconForStep(step),
                size: 14,
                color: isCompleted
                    ? Colors.white
                    : theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              step.label,
              style: theme.textTheme.labelSmall?.copyWith(
                color: isCompleted
                    ? theme.colorScheme.primary
                    : theme.colorScheme.onSurfaceVariant,
                fontWeight: isCurrent ? FontWeight.w700 : FontWeight.w500,
                fontSize: 9,
              ),
            ),
          ],
        );
      }),
    );
  }

  IconData _iconForStep(TripStatus status) => switch (status) {
        TripStatus.booked => Icons.calendar_today,
        TripStatus.confirmed => Icons.check_circle_outline,
        TripStatus.inProgress => Icons.directions_bus,
        TripStatus.completed => Icons.flag,
        _ => Icons.circle_outlined,
      };
}
