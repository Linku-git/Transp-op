import 'package:flutter/material.dart';
import '../config/colors.dart';
import '../models/vehicle_position.dart';

class TrackingMiniMap extends StatelessWidget {
  final VehiclePosition? vehiclePosition;
  final double? gatheringPointLat;
  final double? gatheringPointLng;
  final double? employeeLat;
  final double? employeeLng;
  final VoidCallback? onTap;

  const TrackingMiniMap({
    super.key,
    this.vehiclePosition,
    this.gatheringPointLat,
    this.gatheringPointLng,
    this.employeeLat,
    this.employeeLng,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Placeholder map view — google_maps_flutter requires platform setup
    // Real implementation will use GoogleMap widget with markers and polylines
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 200,
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Stack(
          children: [
            // Map placeholder
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.map,
                    size: 48,
                    color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.3),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Carte de suivi en direct',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),

            // Status indicators
            Positioned(
              left: 12,
              bottom: 12,
              child: Row(
                children: [
                  _LegendItem(color: AppColors.primary, label: 'Vous'),
                  const SizedBox(width: 12),
                  _LegendItem(color: AppColors.success, label: 'Arrêt'),
                  const SizedBox(width: 12),
                  _LegendItem(color: AppColors.warning, label: 'Véhicule'),
                ],
              ),
            ),

            // Vehicle status badge
            if (vehiclePosition != null)
              Positioned(
                right: 12,
                top: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.success.withValues(alpha: 0.9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.gps_fixed, size: 12, color: Colors.white),
                      const SizedBox(width: 4),
                      Text(
                        'EN DIRECT',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w700,
                          fontSize: 9,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // Expand icon
            if (onTap != null)
              Positioned(
                right: 12,
                bottom: 12,
                child: Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    Icons.fullscreen,
                    size: 20,
                    color: theme.colorScheme.onSurface,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}
