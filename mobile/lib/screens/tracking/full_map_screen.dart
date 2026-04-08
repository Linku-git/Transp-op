import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/colors.dart';
import '../../providers/tracking_provider.dart';
import '../../utils/map_utils.dart';

class FullMapScreen extends ConsumerWidget {
  const FullMapScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(trackingProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Carte en direct'),
        actions: [
          if (state.isConnected)
            const Padding(
              padding: EdgeInsets.only(right: 12),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.gps_fixed, size: 14, color: Colors.green),
                  SizedBox(width: 4),
                  Text('LIVE', style: TextStyle(color: Colors.green, fontSize: 10, fontWeight: FontWeight.w700)),
                ],
              ),
            ),
        ],
      ),
      body: Stack(
        children: [
          // Map placeholder — google_maps_flutter GoogleMap widget goes here
          // with markers for vehicle, gathering point, employee, and polylines
          Container(
            color: theme.colorScheme.surfaceContainerHigh,
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.map,
                    size: 64,
                    color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.3),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Google Maps sera affiché ici',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  if (state.vehiclePosition != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      'Position: ${state.vehiclePosition!.lat.toStringAsFixed(4)}, ${state.vehiclePosition!.lng.toStringAsFixed(4)}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),

          // Bottom ETA overlay
          Positioned(
            left: 16,
            right: 16,
            bottom: 16 + MediaQuery.of(context).padding.bottom,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: MapUtils.etaColor(state.etaSeconds).withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        MapUtils.formatEta(state.etaSeconds),
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: MapUtils.etaColor(state.etaSeconds),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            state.gatheringPointName,
                            style: theme.textTheme.titleSmall,
                          ),
                          Text(
                            '${state.vehicleType} — ${state.routeName}',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Legend overlay
          Positioned(
            left: 16,
            top: 16,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _LegendRow(color: AppColors.primary, label: 'Ma position', dashed: false),
                    const SizedBox(height: 4),
                    _LegendRow(color: AppColors.success, label: 'Point de ramassage', dashed: false),
                    const SizedBox(height: 4),
                    _LegendRow(color: AppColors.warning, label: 'Véhicule', dashed: false),
                    const SizedBox(height: 4),
                    _LegendRow(color: AppColors.outline, label: 'Trajet à pied', dashed: true),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _LegendRow extends StatelessWidget {
  final Color color;
  final String label;
  final bool dashed;

  const _LegendRow({
    required this.color,
    required this.label,
    required this.dashed,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (dashed)
          SizedBox(
            width: 16,
            child: Row(
              children: [
                Container(width: 4, height: 2, color: color),
                const SizedBox(width: 2),
                Container(width: 4, height: 2, color: color),
                const SizedBox(width: 2),
                Container(width: 4, height: 2, color: color),
              ],
            ),
          )
        else
          Container(width: 16, height: 3, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(1))),
        const SizedBox(width: 6),
        Text(
          label,
          style: TextStyle(fontSize: 10, color: Theme.of(context).colorScheme.onSurfaceVariant),
        ),
      ],
    );
  }
}
