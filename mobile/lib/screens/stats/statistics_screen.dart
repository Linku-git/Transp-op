import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/statistics_provider.dart';
import '../../widgets/stats_summary_cards.dart';
import '../../widgets/trips_bar_chart.dart';
import '../../widgets/co2_trend_chart.dart';
import '../../widgets/transport_mode_pie_chart.dart';
import '../../widgets/share_impact_card.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/empty_state.dart';

class StatisticsScreen extends ConsumerStatefulWidget {
  const StatisticsScreen({super.key});

  @override
  ConsumerState<StatisticsScreen> createState() => _StatisticsScreenState();
}

class _StatisticsScreenState extends ConsumerState<StatisticsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() => ref.read(statisticsProvider.notifier).load());
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(statisticsProvider);
    final notifier = ref.read(statisticsProvider.notifier);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Statistiques')),
      body: state.isLoading
          ? const LoadingIndicator()
          : state.data.totalTrips == 0
              ? const EmptyState(
                  title: 'Pas encore de statistiques',
                  subtitle: 'Effectuez des trajets pour voir vos stats',
                  icon: Icons.bar_chart,
                )
              : RefreshIndicator(
                  onRefresh: () => notifier.load(),
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      // Period selector
                      Row(
                        children: StatsPeriod.values.map((period) {
                          final isSelected = state.period == period;
                          return Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: ChoiceChip(
                              label: Text(_periodLabel(period)),
                              selected: isSelected,
                              onSelected: (_) => notifier.setPeriod(period),
                              selectedColor: theme.colorScheme.primary.withValues(alpha: 0.15),
                              labelStyle: TextStyle(
                                color: isSelected
                                    ? theme.colorScheme.primary
                                    : theme.colorScheme.onSurface,
                                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: 16),

                      // Summary cards
                      StatsSummaryCards(data: state.data),
                      const SizedBox(height: 16),

                      // Bar chart
                      TripsBarChart(data: state.data.monthlyTrips),
                      const SizedBox(height: 16),

                      // CO2 trend
                      Co2TrendChart(data: state.data.co2Trend),
                      const SizedBox(height: 16),

                      // Pie chart
                      TransportModePieChart(distribution: state.data.modeDistribution),
                      const SizedBox(height: 16),

                      // Share card
                      ShareImpactCard(
                        data: state.data,
                        onShare: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Partage disponible prochainement')),
                          );
                        },
                      ),
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
    );
  }

  String _periodLabel(StatsPeriod period) => switch (period) {
        StatsPeriod.month => 'Ce mois',
        StatsPeriod.year => 'Cette année',
        StatsPeriod.allTime => 'Tout',
      };
}
