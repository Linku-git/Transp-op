import 'package:flutter/material.dart';
import '../models/trip.dart';

class TripCard extends StatelessWidget {
  final Trip trip;
  final VoidCallback? onTap;
  final VoidCallback? onModify;
  final VoidCallback? onCancel;

  const TripCard({
    super.key,
    required this.trip,
    this.onTap,
    this.onModify,
    this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    '${trip.date.day.toString().padLeft(2, '0')}/${trip.date.month.toString().padLeft(2, '0')}',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    trip.shiftLabel,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const Spacer(),
                  _StatusChip(status: trip.status),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.place, size: 14, color: theme.colorScheme.onSurfaceVariant),
                  const SizedBox(width: 4),
                  Text(trip.pickupPointName, style: theme.textTheme.bodySmall),
                  const SizedBox(width: 12),
                  Icon(Icons.route, size: 14, color: theme.colorScheme.onSurfaceVariant),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(trip.routeName, style: theme.textTheme.bodySmall, overflow: TextOverflow.ellipsis),
                  ),
                ],
              ),
              if (trip.co2SavedKg != null && trip.co2SavedKg! > 0) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(Icons.eco, size: 14, color: Colors.green.shade600),
                    const SizedBox(width: 4),
                    Text(
                      '${trip.co2SavedKg!.toStringAsFixed(1)} kg CO2 économisés',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.green.shade600,
                      ),
                    ),
                  ],
                ),
              ],
              if (trip.canModify || trip.canCancel) ...[
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    if (trip.canModify && onModify != null)
                      TextButton.icon(
                        onPressed: onModify,
                        icon: const Icon(Icons.edit, size: 16),
                        label: const Text('Modifier'),
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 8),
                          visualDensity: VisualDensity.compact,
                        ),
                      ),
                    if (trip.canCancel && onCancel != null) ...[
                      const SizedBox(width: 8),
                      TextButton.icon(
                        onPressed: onCancel,
                        icon: const Icon(Icons.close, size: 16),
                        label: const Text('Annuler'),
                        style: TextButton.styleFrom(
                          foregroundColor: theme.colorScheme.error,
                          padding: const EdgeInsets.symmetric(horizontal: 8),
                          visualDensity: VisualDensity.compact,
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final TripStatus status;
  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    final (color, bgColor) = switch (status) {
      TripStatus.booked => (Colors.blue.shade700, Colors.blue.shade50),
      TripStatus.confirmed => (Colors.green.shade700, Colors.green.shade50),
      TripStatus.inProgress => (Colors.orange.shade700, Colors.orange.shade50),
      TripStatus.completed => (Colors.grey.shade600, Colors.grey.shade100),
      TripStatus.cancelled => (Colors.red.shade600, Colors.red.shade50),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        status.label,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }
}
