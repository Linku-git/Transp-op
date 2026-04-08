import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../config/colors.dart';
import '../../models/trip.dart';
import '../../providers/trips_provider.dart';
import '../../widgets/trip_card.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/loading_indicator.dart';

class TripHistoryScreen extends ConsumerStatefulWidget {
  const TripHistoryScreen({super.key});

  @override
  ConsumerState<TripHistoryScreen> createState() => _TripHistoryScreenState();
}

class _TripHistoryScreenState extends ConsumerState<TripHistoryScreen> {
  @override
  void initState() {
    super.initState();
    final state = ref.read(tripsProvider);
    if (state.past.isEmpty) {
      Future.microtask(() => ref.read(tripsProvider.notifier).load());
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(tripsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Historique')),
      body: state.isLoading
          ? const LoadingIndicator()
          : state.past.isEmpty
              ? const EmptyState(
                  title: 'Aucun trajet dans l\'historique',
                  icon: Icons.history,
                )
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    // Stats header
                    _StatsHeader(stats: state.pastStats),
                    const SizedBox(height: 16),

                    // Monthly groups
                    ...state.pastByMonth.entries.map((entry) {
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Padding(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            child: Text(
                              _formatMonthKey(entry.key),
                              style: theme.textTheme.titleSmall?.copyWith(
                                fontWeight: FontWeight.w700,
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ),
                          ...entry.value.map((trip) => Padding(
                                padding: const EdgeInsets.only(bottom: 8),
                                child: TripCard(
                                  trip: trip,
                                  onTap: () =>
                                      context.push('/trips/${trip.id}'),
                                ),
                              )),
                        ],
                      );
                    }),
                  ],
                ),
    );
  }

  String _formatMonthKey(String key) {
    final parts = key.split('-');
    final month = int.parse(parts[1]);
    const months = [
      'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre',
    ];
    return '${months[month - 1]} ${parts[0]}';
  }
}

class _StatsHeader extends StatelessWidget {
  final TripStats stats;
  const _StatsHeader({required this.stats});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.primary.withValues(alpha: 0.04),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: AppColors.primary.withValues(alpha: 0.12)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            _StatItem(
              value: '${stats.totalTrips}',
              label: 'Trajets',
              icon: Icons.directions_bus,
            ),
            _StatItem(
              value: '${stats.totalCo2SavedKg.toStringAsFixed(1)} kg',
              label: 'CO2 éco.',
              icon: Icons.eco,
            ),
            _StatItem(
              value: '${stats.totalDistanceKm.toStringAsFixed(0)} km',
              label: 'Distance',
              icon: Icons.straighten,
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String value;
  final String label;
  final IconData icon;

  const _StatItem({
    required this.value,
    required this.label,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Expanded(
      child: Column(
        children: [
          Icon(icon, size: 20, color: theme.colorScheme.primary),
          const SizedBox(height: 4),
          Text(
            value,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          Text(
            label,
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}
