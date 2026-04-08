import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';
import '../../providers/home_provider.dart';
import '../../utils/night_mode_helper.dart';
import '../../widgets/next_departure_card.dart';
import '../../widgets/quick_actions_row.dart';
import '../../widgets/content_carousel.dart';
import '../../widgets/emergency_button.dart';
import '../../widgets/empty_state.dart';
import '../../widgets/loading_indicator.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(homeProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final homeState = ref.watch(homeProvider);
    final theme = Theme.of(context);
    final isNight = NightModeHelper.isNightTime();

    return Scaffold(
      appBar: AppBar(
        title: Text(
          _greeting(authState.user?.firstName),
          style: theme.textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () => context.push('/notifications'),
              ),
              if (homeState.unreadNotifications > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.error,
                      shape: BoxShape.circle,
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 18,
                      minHeight: 18,
                    ),
                    child: Text(
                      homeState.unreadNotifications > 9
                          ? '9+'
                          : '${homeState.unreadNotifications}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
      body: homeState.isLoading
          ? const LoadingIndicator(message: 'Chargement...')
          : RefreshIndicator(
              onRefresh: () => ref.read(homeProvider.notifier).load(),
              child: ListView(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
                children: [
                  // Next departure
                  if (homeState.nextDeparture != null)
                    NextDepartureCard(
                      departure: homeState.nextDeparture!,
                      onViewMap: () => context.push('/tracking/map'),
                    )
                  else
                    const _NoDepartureCard(),
                  const SizedBox(height: 16),

                  // Quick actions
                  QuickActionsRow(
                    onBookTrip: () => context.push('/trips/book'),
                    onViewMap: () => context.push('/tracking/map'),
                    onMyTrips: () => context.go('/trips'),
                  ),
                  const SizedBox(height: 24),

                  // Content carousel
                  ContentCarousel(
                    items: homeState.contentItems,
                    onItemTap: (id) => context.push('/content/$id'),
                  ),

                  // Night mode emergency
                  if (isNight) ...[
                    const SizedBox(height: 24),
                    EmergencyButton(
                      onPressed: () => context.push('/emergency'),
                    ),
                  ],

                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }

  String _greeting(String? firstName) {
    final hour = DateTime.now().hour;
    final name = firstName ?? '';
    final prefix = name.isNotEmpty ? ', $name' : '';

    if (hour < 12) return 'Bonjour$prefix';
    if (hour < 18) return 'Bon après-midi$prefix';
    return 'Bonsoir$prefix';
  }
}

class _NoDepartureCard extends StatelessWidget {
  const _NoDepartureCard();

  @override
  Widget build(BuildContext context) {
    return const EmptyState(
      title: 'Aucun trajet prévu',
      subtitle: 'Réservez votre prochain trajet',
      icon: Icons.directions_bus_outlined,
    );
  }
}
