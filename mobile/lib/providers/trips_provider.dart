import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/trip.dart';
import '../services/trip_service.dart';
import '../utils/api_error.dart';
import 'trip_booking_provider.dart';

class TripsState {
  final List<Trip> upcoming;
  final List<Trip> past;
  final bool isLoading;
  final String? error;

  const TripsState({
    this.upcoming = const [],
    this.past = const [],
    this.isLoading = false,
    this.error,
  });

  TripStats get pastStats => TripStats.fromTrips(past);

  Map<String, List<Trip>> get pastByMonth {
    final grouped = <String, List<Trip>>{};
    for (final trip in past) {
      final key =
          '${trip.date.year}-${trip.date.month.toString().padLeft(2, '0')}';
      grouped.putIfAbsent(key, () => []).add(trip);
    }
    return grouped;
  }

  TripsState copyWith({
    List<Trip>? upcoming,
    List<Trip>? past,
    bool? isLoading,
    String? error,
  }) {
    return TripsState(
      upcoming: upcoming ?? this.upcoming,
      past: past ?? this.past,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class TripsNotifier extends StateNotifier<TripsState> {
  final TripService _service;

  TripsNotifier(this._service) : super(const TripsState());

  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final results = await Future.wait([
        _service.getUpcomingTrips(),
        _service.getPastTrips(),
      ]);
      state = TripsState(
        upcoming: results[0],
        past: results[1],
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: extractApiError(e, 'Erreur de chargement'),
      );
    }
  }

  Future<bool> cancelTrip(String tripId) async {
    try {
      await _service.cancelTrip(tripId);
      state = state.copyWith(
        upcoming: state.upcoming.where((t) => t.id != tripId).toList(),
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        error: extractApiError(e, 'Erreur lors de l\'annulation'),
      );
      return false;
    }
  }
}

final tripsProvider = StateNotifierProvider<TripsNotifier, TripsState>((ref) {
  return TripsNotifier(ref.watch(tripServiceProvider));
});
