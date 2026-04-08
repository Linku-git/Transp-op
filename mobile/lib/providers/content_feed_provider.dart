import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/content_feed.dart';
import '../services/content_feed_service.dart';
import '../services/api_client.dart';
import 'auth_provider.dart';

final contentFeedServiceProvider = Provider<ContentFeedService>((ref) {
  return ContentFeedService(apiClient: ref.watch(apiClientProvider));
});

class ContentFeedState {
  final List<FeedContent> items;
  final bool isLoading;
  final bool isOffline;
  final String? error;
  final String selectedType;

  const ContentFeedState({
    this.items = const [],
    this.isLoading = false,
    this.isOffline = false,
    this.error,
    this.selectedType = 'all',
  });

  ContentFeedState copyWith({
    List<FeedContent>? items,
    bool? isLoading,
    bool? isOffline,
    String? error,
    String? selectedType,
    bool clearError = false,
  }) {
    return ContentFeedState(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      isOffline: isOffline ?? this.isOffline,
      error: clearError ? null : (error ?? this.error),
      selectedType: selectedType ?? this.selectedType,
    );
  }

  List<FeedContent> get filteredItems {
    if (selectedType == 'all') return items;
    return items.where((i) => i.contentType == selectedType).toList();
  }
}

class ContentFeedNotifier extends StateNotifier<ContentFeedState> {
  final ContentFeedService _service;
  final String? _employeeId;

  ContentFeedNotifier(this._service, this._employeeId)
      : super(const ContentFeedState());

  Future<void> load() async {
    if (_employeeId == null) return;
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final items = await _service.fetchFeed(employeeId: _employeeId);
      state = ContentFeedState(items: items, selectedType: state.selectedType);
    } catch (_) {
      // Try offline cache
      final cached = await _service.getCachedFeed();
      if (cached.isNotEmpty) {
        state = ContentFeedState(
          items: cached,
          isOffline: true,
          selectedType: state.selectedType,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Impossible de charger le contenu',
        );
      }
    }
  }

  Future<void> refresh() async {
    await load();
  }

  void setType(String type) {
    state = state.copyWith(selectedType: type);
  }
}

final contentFeedProvider =
    StateNotifierProvider<ContentFeedNotifier, ContentFeedState>((ref) {
  final service = ref.watch(contentFeedServiceProvider);
  final authState = ref.watch(authProvider);
  // Use user ID as employee ID for feed personalization
  final employeeId = authState.user?.id;
  return ContentFeedNotifier(service, employeeId);
});

/// Provider for a single content detail.
final contentDetailProvider =
    FutureProvider.family<FeedContent, String>((ref, contentId) async {
  final service = ref.watch(contentFeedServiceProvider);
  return service.getContent(contentId);
});
