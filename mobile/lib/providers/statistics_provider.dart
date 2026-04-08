import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/statistics_service.dart';
import 'auth_provider.dart';

final statisticsServiceProvider = Provider<StatisticsService>((ref) {
  return StatisticsService(apiClient: ref.watch(apiClientProvider));
});

enum StatsPeriod { month, year, allTime }

class StatisticsState {
  final StatisticsData data;
  final StatsPeriod period;
  final bool isLoading;
  final String? error;

  const StatisticsState({
    this.data = const StatisticsData(),
    this.period = StatsPeriod.month,
    this.isLoading = false,
    this.error,
  });

  StatisticsState copyWith({
    StatisticsData? data,
    StatsPeriod? period,
    bool? isLoading,
    String? error,
  }) {
    return StatisticsState(
      data: data ?? this.data,
      period: period ?? this.period,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class StatisticsNotifier extends StateNotifier<StatisticsState> {
  final StatisticsService _service;

  StatisticsNotifier(this._service) : super(const StatisticsState());

  Future<void> load([StatsPeriod? period]) async {
    final p = period ?? state.period;
    state = state.copyWith(isLoading: true, period: p, error: null);
    try {
      final periodStr = switch (p) {
        StatsPeriod.month => 'month',
        StatsPeriod.year => 'year',
        StatsPeriod.allTime => 'all',
      };
      final data = await _service.getStatistics(period: periodStr);
      state = state.copyWith(data: data, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Erreur de chargement');
    }
  }

  void setPeriod(StatsPeriod period) => load(period);
}

final statisticsProvider =
    StateNotifierProvider<StatisticsNotifier, StatisticsState>((ref) {
  return StatisticsNotifier(ref.watch(statisticsServiceProvider));
});
