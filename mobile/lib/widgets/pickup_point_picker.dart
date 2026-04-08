import 'package:flutter/material.dart';
import '../models/trip_booking.dart';

class PickupPointPicker extends StatelessWidget {
  final PickupPoint? selectedPoint;
  final List<PickupPoint> availablePoints;
  final ValueChanged<PickupPoint> onPointSelected;
  final VoidCallback? onChangePressed;

  const PickupPointPicker({
    super.key,
    this.selectedPoint,
    this.availablePoints = const [],
    required this.onPointSelected,
    this.onChangePressed,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.place,
                  size: 20,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'POINT DE RAMASSAGE',
                  style: theme.textTheme.labelSmall?.copyWith(
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (selectedPoint != null) ...[
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          selectedPoint!.name,
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        if (selectedPoint!.walkingMinutes != null) ...[
                          const SizedBox(height: 2),
                          Text(
                            '${selectedPoint!.walkingMinutes!.round()} min à pied',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: onChangePressed ?? () => _showPointPicker(context),
                    child: const Text('Changer'),
                  ),
                ],
              ),
            ] else
              Text(
                'Aucun point sélectionné',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
          ],
        ),
      ),
    );
  }

  void _showPointPicker(BuildContext context) {
    if (availablePoints.isEmpty) return;

    showModalBottomSheet(
      context: context,
      builder: (ctx) {
        final theme = Theme.of(ctx);
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  'Choisir un point de ramassage',
                  style: theme.textTheme.titleMedium,
                ),
              ),
              ...availablePoints.map((point) => ListTile(
                    leading: const Icon(Icons.place),
                    title: Text(point.name),
                    subtitle: point.walkingMinutes != null
                        ? Text('${point.walkingMinutes!.round()} min à pied')
                        : null,
                    selected: point.id == selectedPoint?.id,
                    onTap: () {
                      onPointSelected(point);
                      Navigator.of(ctx).pop();
                    },
                  )),
              const SizedBox(height: 8),
            ],
          ),
        );
      },
    );
  }
}
