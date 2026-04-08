import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/trips_provider.dart';
import '../../widgets/trip_card.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/loading_indicator.dart';

class TripsScreen extends ConsumerStatefulWidget {
  const TripsScreen({super.key});

  @override
  ConsumerState<TripsScreen> createState() => _TripsScreenState();
}

class _TripsScreenState extends ConsumerState<TripsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(tripsProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(tripsProvider);

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Mes trajets'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'À venir'),
              Tab(text: 'Passés'),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.history),
              onPressed: () => context.push('/trips/history'),
              tooltip: 'Historique',
            ),
          ],
        ),
        body: state.isLoading
            ? const LoadingIndicator()
            : TabBarView(
                children: [
                  _UpcomingTab(trips: state.upcoming),
                  _PastTab(trips: state.past),
                ],
              ),
      ),
    );
  }
}

class _UpcomingTab extends ConsumerWidget {
  final List trips;
  const _UpcomingTab({required this.trips});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (trips.isEmpty) {
      return const EmptyState(
        title: 'Aucun trajet à venir',
        subtitle: 'Réservez un trajet pour commencer',
        icon: Icons.calendar_today_outlined,
      );
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(tripsProvider.notifier).load(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: trips.length,
        itemBuilder: (context, index) {
          final trip = trips[index];
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: TripCard(
              trip: trip,
              onTap: () => context.push('/trips/${trip.id}'),
              onModify: trip.canModify ? () => context.push('/trips/${trip.id}') : null,
              onCancel: trip.canCancel
                  ? () => _showCancelDialog(context, ref, trip.id)
                  : null,
            ),
          );
        },
      ),
    );
  }

  void _showCancelDialog(BuildContext context, WidgetRef ref, String tripId) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Annuler le trajet ?'),
        content: const Text(
          'Cette action est irréversible. Vous devrez réserver un nouveau trajet si nécessaire.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Non'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(ctx).pop();
              await ref.read(tripsProvider.notifier).cancelTrip(tripId);
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

class _PastTab extends ConsumerWidget {
  final List trips;
  const _PastTab({required this.trips});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (trips.isEmpty) {
      return const EmptyState(
        title: 'Aucun trajet passé',
        icon: Icons.history,
      );
    }

    return RefreshIndicator(
      onRefresh: () => ref.read(tripsProvider.notifier).load(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: trips.length,
        itemBuilder: (context, index) {
          final trip = trips[index];
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: TripCard(
              trip: trip,
              onTap: () => context.push('/trips/${trip.id}'),
            ),
          );
        },
      ),
    );
  }
}
