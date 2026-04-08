import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/connectivity_service.dart';

final connectivityServiceProvider = Provider<ConnectivityService>((ref) {
  final service = ConnectivityService();
  ref.onDispose(() => service.dispose());
  return service;
});

final connectivityStateProvider =
    StreamProvider<ConnectivityState>((ref) {
  final service = ref.watch(connectivityServiceProvider);
  return service.stateStream;
});

final isOnlineProvider = Provider<bool>((ref) {
  final state = ref.watch(connectivityStateProvider);
  return state.when(
    data: (s) => s != ConnectivityState.offline,
    loading: () => true,
    error: (_, _) => true,
  );
});
