import 'api_client.dart';

class StatisticsData {
  final int totalTrips;
  final double totalDistanceKm;
  final double co2SavedKg;
  final int trainingCompleted;
  final double quizAverage;
  final List<MonthlyTrips> monthlyTrips;
  final List<Co2DataPoint> co2Trend;
  final Map<String, int> modeDistribution;

  const StatisticsData({
    this.totalTrips = 0,
    this.totalDistanceKm = 0,
    this.co2SavedKg = 0,
    this.trainingCompleted = 0,
    this.quizAverage = 0,
    this.monthlyTrips = const [],
    this.co2Trend = const [],
    this.modeDistribution = const {},
  });

  factory StatisticsData.fromJson(Map<String, dynamic> json) {
    return StatisticsData(
      totalTrips: json['total_trips'] as int? ?? 0,
      totalDistanceKm: (json['total_distance_km'] as num?)?.toDouble() ?? 0,
      co2SavedKg: (json['co2_saved_kg'] as num?)?.toDouble() ?? 0,
      trainingCompleted: json['training_completed'] as int? ?? 0,
      quizAverage: (json['quiz_average'] as num?)?.toDouble() ?? 0,
      monthlyTrips: (json['monthly_trips'] as List?)
              ?.map((e) => MonthlyTrips.fromJson(e))
              .toList() ??
          [],
      co2Trend: (json['co2_trend'] as List?)
              ?.map((e) => Co2DataPoint.fromJson(e))
              .toList() ??
          [],
      modeDistribution: (json['mode_distribution'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, (v as num).toInt())) ??
          {},
    );
  }
}

class MonthlyTrips {
  final String month;
  final int count;

  const MonthlyTrips({required this.month, required this.count});

  factory MonthlyTrips.fromJson(Map<String, dynamic> json) {
    return MonthlyTrips(
      month: json['month'] as String,
      count: json['count'] as int? ?? 0,
    );
  }
}

class Co2DataPoint {
  final String date;
  final double value;

  const Co2DataPoint({required this.date, required this.value});

  factory Co2DataPoint.fromJson(Map<String, dynamic> json) {
    return Co2DataPoint(
      date: json['date'] as String,
      value: (json['value'] as num?)?.toDouble() ?? 0,
    );
  }
}

class StatisticsService {
  final ApiClient _apiClient;

  StatisticsService({required ApiClient apiClient}) : _apiClient = apiClient;

  Future<StatisticsData> getStatistics({String period = 'month'}) async {
    try {
      final response = await _apiClient.dio.get(
        '/mobile/statistics',
        queryParameters: {'period': period},
      );
      return StatisticsData.fromJson(response.data);
    } catch (_) {
      return const StatisticsData();
    }
  }
}
