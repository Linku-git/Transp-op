import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

enum ConnectivityState { online, offline, degraded }

class ConnectivityService {
  final Connectivity _connectivity;
  final _stateController = StreamController<ConnectivityState>.broadcast();
  ConnectivityState _currentState = ConnectivityState.online;

  ConnectivityService({Connectivity? connectivity})
      : _connectivity = connectivity ?? Connectivity() {
    _connectivity.onConnectivityChanged.listen(_onConnectivityChanged);
  }

  Stream<ConnectivityState> get stateStream => _stateController.stream;
  ConnectivityState get currentState => _currentState;
  bool get isOnline => _currentState != ConnectivityState.offline;

  Future<void> initialize() async {
    final results = await _connectivity.checkConnectivity();
    _updateState(results);
  }

  void _onConnectivityChanged(List<ConnectivityResult> results) {
    _updateState(results);
  }

  void _updateState(List<ConnectivityResult> results) {
    final newState = _mapToState(results);
    if (newState != _currentState) {
      _currentState = newState;
      _stateController.add(newState);
    }
  }

  ConnectivityState _mapToState(List<ConnectivityResult> results) {
    if (results.contains(ConnectivityResult.none) || results.isEmpty) {
      return ConnectivityState.offline;
    }
    if (results.contains(ConnectivityResult.wifi) ||
        results.contains(ConnectivityResult.ethernet)) {
      return ConnectivityState.online;
    }
    if (results.contains(ConnectivityResult.mobile)) {
      return ConnectivityState.online;
    }
    return ConnectivityState.degraded;
  }

  void dispose() {
    _stateController.close();
  }
}
