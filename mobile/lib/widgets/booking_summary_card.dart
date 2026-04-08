import 'package:flutter/material.dart';
import '../config/colors.dart';
import '../models/trip_booking.dart';

class BookingSummaryCard extends StatelessWidget {
  final DateTime date;
  final Shift? shift;
  final PickupPoint? pickupPoint;

  const BookingSummaryCard({
    super.key,
    required this.date,
    this.shift,
    this.pickupPoint,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      color: AppColors.primary.withValues(alpha: 0.04),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: AppColors.primary.withValues(alpha: 0.15),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.summarize, size: 18, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'RÉCAPITULATIF',
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                    color: theme.colorScheme.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _SummaryRow(
              icon: Icons.calendar_today,
              label: 'Date',
              value: '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}',
            ),
            if (shift != null) ...[
              const SizedBox(height: 8),
              _SummaryRow(
                icon: Icons.schedule,
                label: 'Horaire',
                value: '${shift!.label} (${shift!.entryTime} — ${shift!.exitTime})',
              ),
            ],
            if (pickupPoint != null) ...[
              const SizedBox(height: 8),
              _SummaryRow(
                icon: Icons.place,
                label: 'Ramassage',
                value: pickupPoint!.name,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _SummaryRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(width: 8),
        SizedBox(
          width: 70,
          child: Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
}
