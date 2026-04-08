import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/trip.dart';
import '../../providers/trips_provider.dart';
import '../../widgets/trip_status_timeline.dart';
import '../../widgets/co2_badge.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/error_widget.dart';
import '../../providers/trip_booking_provider.dart';

final tripDetailProvider =
    FutureProvider.family<Trip, String>((ref, tripId) async {
  final service = ref.watch(tripServiceProvider);
  return service.getTripDetail(tripId);
});

class TripDetailScreen extends ConsumerWidget {
  final String tripId;

  const TripDetailScreen({super.key, required this.tripId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tripAsync = ref.watch(tripDetailProvider(tripId));
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Détail du trajet')),
      body: tripAsync.when(
        loading: () => const LoadingIndicator(),
        error: (e, _) => AppErrorWidget(
          message: 'Impossible de charger le trajet',
          onRetry: () => ref.invalidate(tripDetailProvider(tripId)),
        ),
        data: (trip) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Status timeline
              TripStatusTimeline(currentStatus: trip.status),
              const SizedBox(height: 24),

              // Details card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _DetailRow(
                        icon: Icons.calendar_today,
                        label: 'Date',
                        value:
                            '${trip.date.day.toString().padLeft(2, '0')}/${trip.date.month.toString().padLeft(2, '0')}/${trip.date.year}',
                      ),
                      const SizedBox(height: 10),
                      _DetailRow(
                        icon: Icons.schedule,
                        label: 'Horaire',
                        value: trip.shiftLabel,
                      ),
                      const SizedBox(height: 10),
                      _DetailRow(
                        icon: Icons.place,
                        label: 'Ramassage',
                        value: trip.pickupPointName,
                      ),
                      const SizedBox(height: 10),
                      _DetailRow(
                        icon: Icons.route,
                        label: 'Route',
                        value: trip.routeName,
                      ),
                      const SizedBox(height: 10),
                      _DetailRow(
                        icon: Icons.directions_bus,
                        label: 'Véhicule',
                        value: trip.vehicleType,
                      ),
                      if (trip.distanceKm != null) ...[
                        const SizedBox(height: 10),
                        _DetailRow(
                          icon: Icons.straighten,
                          label: 'Distance',
                          value: '${trip.distanceKm!.toStringAsFixed(1)} km',
                        ),
                      ],
                      if (trip.durationMinutes != null) ...[
                        const SizedBox(height: 10),
                        _DetailRow(
                          icon: Icons.timer,
                          label: 'Durée',
                          value: '${trip.durationMinutes!.round()} min',
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // CO2 badge
              if (trip.co2SavedKg != null && trip.co2SavedKg! > 0)
                Center(child: Co2Badge(co2SavedKg: trip.co2SavedKg!)),

              // Actions
              if (trip.canCancel) ...[
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _showCancelDialog(context, ref, trip.id),
                    icon: const Icon(Icons.close),
                    label: const Text('Annuler le trajet'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: theme.colorScheme.error,
                      side: BorderSide(color: theme.colorScheme.error),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showCancelDialog(BuildContext context, WidgetRef ref, String id) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Annuler le trajet ?'),
        content: const Text('Cette action est irréversible.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Non'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(ctx).pop();
              await ref.read(tripsProvider.notifier).cancelTrip(id);
              if (context.mounted) Navigator.of(context).pop();
            },
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Oui, annuler'),
          ),
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      children: [
        Icon(icon, size: 16, color: theme.colorScheme.onSurfaceVariant),
        const SizedBox(width: 8),
        SizedBox(
          width: 80,
          child: Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
        Expanded(
          child: Text(value, style: theme.textTheme.bodyMedium),
        ),
      ],
    );
  }
}
