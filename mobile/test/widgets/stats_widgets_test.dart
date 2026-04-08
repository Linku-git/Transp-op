import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/services/statistics_service.dart';
import 'package:transpop_mobile/widgets/stats_summary_cards.dart';
import 'package:transpop_mobile/widgets/trips_bar_chart.dart';
import 'package:transpop_mobile/widgets/co2_trend_chart.dart';
import 'package:transpop_mobile/widgets/transport_mode_pie_chart.dart';
import 'package:transpop_mobile/widgets/share_impact_card.dart';

void main() {
  const data = StatisticsData(
    totalTrips: 42,
    totalDistanceKm: 500,
    co2SavedKg: 45.0,
    trainingCompleted: 3,
    quizAverage: 85,
  );

  group('StatsSummaryCards', () {
    testWidgets('renders all stat values', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: StatsSummaryCards(data: data))),
      );

      expect(find.text('42'), findsOneWidget);
      expect(find.text('500 km'), findsOneWidget);
      expect(find.text('45.0 kg'), findsOneWidget);
      expect(find.text('3'), findsOneWidget);
      expect(find.text('85%'), findsOneWidget);
    });

    testWidgets('renders labels', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: StatsSummaryCards(data: data))),
      );

      expect(find.text('Trajets'), findsOneWidget);
      expect(find.text('Distance'), findsOneWidget);
      expect(find.text('CO2 économisé'), findsOneWidget);
      expect(find.text('Formations'), findsOneWidget);
    });
  });

  group('TripsBarChart', () {
    testWidgets('renders title', (tester) async {
      final trips = [
        const MonthlyTrips(month: '2026-01', count: 10),
        const MonthlyTrips(month: '2026-02', count: 15),
      ];

      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: TripsBarChart(data: trips))),
      );

      expect(find.text('TRAJETS PAR MOIS'), findsOneWidget);
      expect(find.text('10'), findsOneWidget);
      expect(find.text('15'), findsOneWidget);
    });

    testWidgets('renders nothing when empty', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: TripsBarChart(data: const []))),
      );

      expect(find.text('TRAJETS PAR MOIS'), findsNothing);
    });
  });

  group('Co2TrendChart', () {
    testWidgets('renders title', (tester) async {
      final trend = [
        const Co2DataPoint(date: '2026-01-01', value: 5.0),
        const Co2DataPoint(date: '2026-02-01', value: 12.0),
      ];

      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: Co2TrendChart(data: trend))),
      );

      expect(find.text('ÉVOLUTION CO2 ÉCONOMISÉ'), findsOneWidget);
    });
  });

  group('TransportModePieChart', () {
    testWidgets('renders title and labels', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: TransportModePieChart(
              distribution: const {'voiture': 10, 'covoiturage': 5},
            ),
          ),
        ),
      );

      expect(find.text('RÉPARTITION PAR MODE'), findsOneWidget);
      expect(find.text('Voiture'), findsOneWidget);
      expect(find.text('Covoiturage'), findsOneWidget);
    });

    testWidgets('renders nothing when empty', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: TransportModePieChart(distribution: const {})),
        ),
      );

      expect(find.text('RÉPARTITION PAR MODE'), findsNothing);
    });
  });

  group('ShareImpactCard', () {
    testWidgets('renders impact stats', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: ShareImpactCard(data: data))),
      );

      expect(find.text('Mon impact positif'), findsOneWidget);
      expect(find.text('42'), findsOneWidget);
      expect(find.text('Trajets'), findsOneWidget);
    });

    testWidgets('shows share button when callback provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: ShareImpactCard(data: data, onShare: () {}),
          ),
        ),
      );

      expect(find.text('Partager mon impact'), findsOneWidget);
    });
  });
}
