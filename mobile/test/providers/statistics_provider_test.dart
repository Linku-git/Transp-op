import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/providers/statistics_provider.dart';
import 'package:transpop_mobile/services/statistics_service.dart';

void main() {
  group('StatisticsState', () {
    test('initial state', () {
      const state = StatisticsState();
      expect(state.period, StatsPeriod.month);
      expect(state.isLoading, false);
      expect(state.data.totalTrips, 0);
    });

    test('copyWith preserves values', () {
      const state = StatisticsState(period: StatsPeriod.year);
      final updated = state.copyWith(isLoading: true);
      expect(updated.period, StatsPeriod.year);
      expect(updated.isLoading, true);
    });
  });

  group('StatisticsData', () {
    test('fromJson parses correctly', () {
      final data = StatisticsData.fromJson({
        'total_trips': 42,
        'total_distance_km': 500.5,
        'co2_saved_kg': 45.0,
        'training_completed': 3,
        'quiz_average': 85.5,
        'monthly_trips': [
          {'month': '2026-01', 'count': 10},
          {'month': '2026-02', 'count': 15},
        ],
        'co2_trend': [
          {'date': '2026-01-01', 'value': 5.0},
          {'date': '2026-02-01', 'value': 12.0},
        ],
        'mode_distribution': {
          'company_transport': 30,
          'voiture': 10,
          'covoiturage': 2,
        },
      });

      expect(data.totalTrips, 42);
      expect(data.totalDistanceKm, 500.5);
      expect(data.co2SavedKg, 45.0);
      expect(data.monthlyTrips.length, 2);
      expect(data.co2Trend.length, 2);
      expect(data.modeDistribution['company_transport'], 30);
    });

    test('fromJson handles empty data', () {
      final data = StatisticsData.fromJson({});
      expect(data.totalTrips, 0);
      expect(data.monthlyTrips, isEmpty);
      expect(data.modeDistribution, isEmpty);
    });
  });

  group('MonthlyTrips', () {
    test('fromJson parses correctly', () {
      final mt = MonthlyTrips.fromJson({'month': '2026-03', 'count': 8});
      expect(mt.month, '2026-03');
      expect(mt.count, 8);
    });
  });
}
