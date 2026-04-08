import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/tracking_provider.dart';
import '../../widgets/vehicle_arrival_card.dart';
import '../../widgets/tracking_mini_map.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/loading_indicator.dart';

class RTITrackingScreen extends ConsumerWidget {
  const RTITrackingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(trackingProvider);
    final theme = Theme.of(context);

    if (state.isLoading) {
      return const Scaffold(
        body: LoadingIndicator(message: 'Connexion au suivi...'),
      );
    }

    if (state.vehicleId == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Suivi en direct')),
        body: const EmptyState(
          title: 'Aucun véhicule à suivre',
          subtitle: 'Le suivi sera disponible le jour de votre trajet',
          icon: Icons.location_off,
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Suivi en direct'),
        actions: [
          // Connection indicator
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: state.isConnected ? Colors.green : Colors.orange,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  state.isConnected ? 'EN DIRECT' : 'HORS LIGNE',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: state.isConnected ? Colors.green : Colors.orange,
                    fontWeight: FontWeight.w700,
                    fontSize: 9,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Vehicle arrival card
            VehicleArrivalCard(
              etaSeconds: state.etaSeconds,
              vehicleType: state.vehicleType,
              routeName: state.routeName,
              driverName: state.driverName,
              gatheringPointName: state.gatheringPointName,
              onViewFullMap: () => context.push('/tracking/map'),
            ),
            const SizedBox(height: 16),

            // Mini map
            TrackingMiniMap(
              vehiclePosition: state.vehiclePosition,
              gatheringPointLat: state.gatheringPointLat,
              gatheringPointLng: state.gatheringPointLng,
              employeeLat: state.employeeLat,
              employeeLng: state.employeeLng,
              onTap: () => context.push('/tracking/map'),
            ),

            // Error banner
            if (state.error != null) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  state.error!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onErrorContainer,
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
