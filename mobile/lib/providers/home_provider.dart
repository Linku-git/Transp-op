import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/departure.dart';
import '../services/departure_service.dart';
import 'auth_provider.dart';

final departureServiceProvider = Provider<DepartureService>((ref) {
  return DepartureService(apiClient: ref.watch(apiClientProvider));
});

class HomeState {
  final Departure? nextDeparture;
  final List<ContentItem> contentItems;
  final int unreadNotifications;
  final bool isLoading;
  final String? error;

  const HomeState({
    this.nextDeparture,
    this.contentItems = const [],
    this.unreadNotifications = 0,
    this.isLoading = false,
    this.error,
  });

  HomeState copyWith({
    Departure? nextDeparture,
    List<ContentItem>? contentItems,
    int? unreadNotifications,
    bool? isLoading,
    String? error,
    bool clearDeparture = false,
  }) {
    return HomeState(
      nextDeparture: clearDeparture ? null : (nextDeparture ?? this.nextDeparture),
      contentItems: contentItems ?? this.contentItems,
      unreadNotifications: unreadNotifications ?? this.unreadNotifications,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class HomeNotifier extends StateNotifier<HomeState> {
  final DepartureService _service;

  HomeNotifier(this._service) : super(const HomeState());

  Future<void> load() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final results = await Future.wait([
        _service.getNextDeparture(),
        _service.getLatestContent(),
        _service.getUnreadNotificationCount(),
      ]);

      state = HomeState(
        nextDeparture: results[0] as Departure?,
        contentItems: results[1] as List<ContentItem>,
        unreadNotifications: results[2] as int,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, error: 'Erreur de chargement');
    }
  }
}

final homeProvider = StateNotifierProvider<HomeNotifier, HomeState>((ref) {
  return HomeNotifier(ref.watch(departureServiceProvider));
});
